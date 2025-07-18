use std::{
    collections::HashMap,
    path::{Path, PathBuf},
    process::Output,
    string::FromUtf8Error,
};

use tokio::process::Command;
use tracing::warn;

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("Cannot determine the project directores for config, cache, and state")]
    NoProjectDirs,
    #[error("File operation error for {}: {}", .0.display(), .1)]
    Io(PathBuf, #[source] std::io::Error),
    #[error("Serialization error for {}: {}", .0.display(), .1)]
    Serializing(PathBuf, #[source] serde_yaml::Error),
    #[error("Deserialization error for {}: {}", .0.display(), .1)]
    Deserializing(PathBuf, #[source] serde_yaml::Error),
    #[error("Missing YNAB API token. One of 'api_token', 'op_item_id', or 'op_item_ref' must be defined in the config")]
    NoApiToken,
    #[error("Command {} failed with: {:?}", .0.display(), .1)]
    Command(PathBuf, Output),
    #[error(transparent)]
    StringConversion(#[from] FromUtf8Error),
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
pub struct Config {
    pub payee_to_category: HashMap<String, String>,
    pub weekwise_payees: Vec<String>,
    pub week_no_to_category: HashMap<u32, String>,
    pub api_url: String,
    pub budget_id: String,
    pub testing_budget_id: Option<String>,
    api_token: Option<String>,
    op_item_id: Option<String>,
    op_item_ref: Option<String>,
    pub rate_limit: Option<f32>,
}

impl Default for Config {
    fn default() -> Self {
        Config {
            payee_to_category: HashMap::default(),
            weekwise_payees: Vec::default(),
            week_no_to_category: HashMap::default(),
            api_url: "https://api.youneedabudget.com/".into(),
            budget_id: "default".into(),
            testing_budget_id: None,
            api_token: None,
            op_item_id: None,
            op_item_ref: None,
            rate_limit: None,
        }
    }
}

impl Config {
    fn project_dirs() -> Result<directories::ProjectDirs, Error> {
        directories::ProjectDirs::from("net", "nausicaea", "ylva").ok_or(Error::NoProjectDirs)
    }

    pub fn default_path() -> Result<PathBuf, Error> {
        Self::project_dirs().map(|pd| pd.config_dir().join("config.yml"))
    }

    pub fn create(p: &Path) -> Result<Self, Error> {
        let config = Config::default();

        config.save(p)?;

        Ok(config)
    }

    pub fn load(p: &Path) -> Result<Self, Error> {
        let file = std::fs::File::open(p).map_err(|e| Error::Io(p.to_path_buf(), e))?;

        let config = serde_yaml::from_reader(std::io::BufReader::new(file))
            .map_err(|e| Error::Deserializing(p.to_path_buf(), e))?;

        Ok(config)
    }

    pub fn save(&self, p: &Path) -> Result<(), Error> {
        let p = if let Some("yml") | Some("yaml") = p.extension().and_then(|ext| ext.to_str()) {
            p.to_path_buf()
        } else {
            warn!("Config file suffix does not match the YAML format: {}", p.display());
            p.with_extension("yml")
        };

        if let Some(parent) = p.parent() {
            std::fs::create_dir_all(parent).map_err(|e| Error::Io(p.to_path_buf(), e))?;
        }

        let file = std::fs::File::create(&p).map_err(|e| Error::Io(p.to_path_buf(), e))?;

        serde_yaml::to_writer(std::io::BufWriter::new(file), self)
            .map_err(|e| Error::Serializing(p.to_path_buf(), e))?;

        Ok(())
    }

    /// Retrieve the API authentication token from configuration.
    /// This allows you to keep API token in your secure vault instead
    /// of storing it in clear text
    pub async fn api_token(&self) -> Result<String, Error> {
        if let Some(api_token) = &self.api_token {
            return Ok(api_token.to_string());
        } else if let Some(op_item_id) = &self.op_item_id {
            return Ok(one_password_get_item(op_item_id, "credential").await?);
        } else if let Some(op_item_ref) = &self.op_item_ref {
            return Ok(one_password_read(op_item_ref).await?);
        }

        Err(Error::NoApiToken)
    }
}

/// Retrieve a field from an item in the One Password vault
async fn one_password_get_item(item_id: &str, field_name: &str) -> Result<String, Error> {
    let one_password = PathBuf::from("op");
    let output = Command::new(&one_password)
        .arg("item")
        .arg("get")
        .arg(item_id)
        .arg("--fields")
        .arg(format!("label={field_name}"))
        .output()
        .await
        .map_err(|e| Error::Io(one_password.clone(), e))?;

    if !output.status.success() {
        return Err(Error::Command(one_password.clone(), output));
    }

    Ok(String::from_utf8(output.stdout)?)
}

/// Retrieve a field by reference from the One Password vault
async fn one_password_read(item_ref: &str) -> Result<String, Error> {
    let one_password = PathBuf::from("op");
    let output = Command::new(&one_password)
        .arg("read")
        .arg(item_ref)
        .output()
        .await
        .map_err(|e| Error::Io(one_password.clone(), e))?;

    if !output.status.success() {
        return Err(Error::Command(one_password.clone(), output));
    }

    Ok(String::from_utf8(output.stdout)?)
}

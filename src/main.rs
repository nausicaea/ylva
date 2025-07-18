use clap::Parser;
use tracing::info;

use crate::actions::{ApproveSpec, AssignCategoriesSpec, AssignPayeesSpec, approve, assign_categories, assign_payees};

pub mod model {
    pub mod ynab {
        #[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize, clap::ValueEnum)]
        pub enum TransactionType {
            /// Request all transactions from YNAB
            All,
            /// Request only uncategorized transactions from YNAB
            Uncategorized,
            /// Request only unapproved transactions from YNAB
            Unapproved,
        }

        impl ToString for TransactionType {
            fn to_string(&self) -> String {
                match self {
                    TransactionType::All => "all".into(),
                    TransactionType::Uncategorized => "uncategorized".into(),
                    TransactionType::Unapproved => "unapproved".into(),
                }
            }
        }
    }
}

pub mod actions {
    use chrono::Datelike;

    use super::model::ynab::TransactionType;

    use super::config::Config;

    fn week_number(dt: chrono::DateTime<chrono::Utc>) -> u32 {
        (dt.day() - 1) / 7
    }

    #[derive(Debug, thiserror::Error)]
    pub enum Error {}

    #[derive(Debug)]
    pub struct ApproveSpec<'a> {
        pub dry_run: bool,
        pub diff: bool,
        pub ignore_cleared: bool,
        pub ignore_payee: bool,
        pub ignore_category: bool,
        pub rate_limit: Option<f32>,
        pub api_url: &'a str,
        pub api_token: &'a str,
        pub budget_id: &'a str,
    }

    pub async fn approve(spec: &ApproveSpec<'_>) -> Result<(), Error> {
        todo!()
    }

    #[derive(Debug)]
    pub struct AssignPayeesSpec<'a> {
        pub dry_run: bool,
        pub diff: bool,
        pub filter: TransactionType,
        pub force: bool,
        pub create_payees: bool,
        pub rate_limit: Option<f32>,
        pub api_url: &'a str,
        pub api_token: &'a str,
        pub budget_id: &'a str,
    }

    pub async fn assign_payees(spec: &AssignPayeesSpec<'_>) -> Result<(), Error> {
        todo!()
    }

    #[derive(Debug)]
    pub struct AssignCategoriesSpec<'a> {
        pub dry_run: bool,
        pub diff: bool,
        pub filter: TransactionType,
        pub force: bool,
        pub weekwise: bool,
        pub rate_limit: Option<f32>,
        pub api_url: &'a str,
        pub api_token: &'a str,
        pub budget_id: &'a str,
    }

    pub async fn assign_categories(spec: &AssignCategoriesSpec<'_>) -> Result<(), Error> {
        todo!()
    }
}

pub mod config {
    use std::{
        collections::HashMap,
        path::{Path, PathBuf}, process::Output, string::FromUtf8Error,
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
}

#[derive(Debug, clap::Parser)]
struct Args {
    /// Disable any state-changing actions (i.e. don't send POST, PUT, UPDATE, or DELETE requests
    /// to YNAB)
    #[arg(short = 'n', long)]
    pub dry_run: bool,
    /// Display the transactions that will be modified, and show the modified properties
    #[arg(short, long)]
    pub diff: bool,
    #[command(subcommand)]
    pub command: Command,
}

/// Choose the budget action
#[derive(Debug, clap::Subcommand)]
enum Command {
    /// Approve transactions, thus committing them to the budget
    Approve {
        /// If set, approve transactions even if they haven't been cleared
        #[arg(short = 's', long)]
        ignore_cleared: bool,
        /// If set, approve transactions even if they haven't been categorized
        #[arg(long)]
        ignore_category: bool,
        /// If set, approve transactions even if they haven't been assigned a payee
        #[arg(long)]
        ignore_payee: bool,
    },
    /// Assign data to transactions
    Assign {
        /// Select which set of transactions to update
        #[arg(short, long, default_value_t = model::ynab::TransactionType::Unapproved, value_enum)]
        filter: model::ynab::TransactionType,
        /// Force all found transactions to be updated (transfers will never be changed)
        #[arg(short = 'F', long)]
        force: bool,
        #[command(subcommand)]
        command: AssignCommand,
    },
}

/// Choose the assignment destination
#[derive(Debug, clap::Subcommand)]
enum AssignCommand {
    /// Assign payees from data in the memo field of transactions
    Payees {
        /// If the transactions contain unknown payees, create them in YNAB
        #[arg(short, long)]
        create_payees: bool,
    },
    /// Assign categories from the payee field of transactions
    Categories {
        /// Assign special categories to payees depending on the month-week
        #[arg(short, long)]
        weekwise: bool,
    },
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let subscriber = tracing_subscriber::FmtSubscriber::builder()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    let args = Args::parse();

    let default_config_path = config::Config::default_path()?;
    let config = if !default_config_path.is_file() {
        config::Config::create(&default_config_path)?
    } else {
        config::Config::load(&default_config_path)?
    };

    if args.dry_run {
        info!("Dry-run mode enabled. Not committing any changes");
    }

    match args.command {
        Command::Approve {
            ignore_cleared,
            ignore_category,
            ignore_payee,
        } => {
            approve(&ApproveSpec {
                dry_run: args.dry_run,
                diff: args.diff,
                ignore_cleared,
                ignore_payee,
                ignore_category,
                rate_limit: config.rate_limit,
                api_url: &config.api_url,
                api_token: config.api_token()?,
                budget_id: &config.budget_id,
            })
            .await?
        }
        Command::Assign {
            filter,
            force,
            command: AssignCommand::Payees { create_payees },
        } => {
            assign_payees(&AssignPayeesSpec {
                dry_run: args.dry_run,
                diff: args.diff,
                filter,
                force,
                create_payees,
                rate_limit: config.rate_limit,
                api_url: &config.api_url,
                api_token: config.api_token()?,
                budget_id: &config.budget_id,
            })
            .await?
        }
        Command::Assign {
            filter,
            force,
            command: AssignCommand::Categories { weekwise },
        } => {
            assign_categories(&AssignCategoriesSpec {
                dry_run: args.dry_run,
                diff: args.diff,
                filter,
                force,
                weekwise,
                rate_limit: config.rate_limit,
                api_url: &config.api_url,
                api_token: config.api_token()?,
                budget_id: &config.budget_id,
            })
            .await?
        }
    }

    Ok(())
}

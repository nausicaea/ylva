use clap::Parser;
use tracing::info;

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
    pub enum Error {
    }

    pub async fn approve(ignore_cleared: bool, ignore_payee: bool, ignore_category: bool, config: &Config) -> Result<(), Error> {
        todo!()
    }

    pub async fn assign_payees(filter: TransactionType, force: bool, create_payees: bool, config: &Config) -> Result<(), Error> {
        todo!()
    }

    pub async fn assign_categories(filter: TransactionType, force: bool, weekwise: bool, config: &Config) -> Result<(), Error> {
        todo!()
    }
}

pub mod config {
    use std::{collections::HashMap, path::{Path, PathBuf}};

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
    }

    #[derive(Debug, serde::Serialize, serde::Deserialize)]
    pub struct Config {
        payee_to_category: HashMap<String, String>,
        weekwise_payees: Vec<String>,
        week_no_to_category: HashMap<u32, String>,
        api_url: String,
        budget_id: String,
        testing_budget_id: Option<String>,
        api_token: Option<String>,
        op_item_id: Option<String>,
        op_item_ref: Option<String>,
        rate_limit: Option<f32>,
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
            directories::ProjectDirs::from("net", "nausicaea", "ylva")
                .ok_or(Error::NoProjectDirs)
        }

        pub fn default_path() -> Result<PathBuf, Error> {
            Self::project_dirs()
                .map(|pd| pd.config_dir().join("config.yml"))
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
                std::fs::create_dir_all(parent)
                    .map_err(|e| Error::Io(p.to_path_buf(), e))?;
            }

            let file = std::fs::File::create(&p)
                    .map_err(|e| Error::Io(p.to_path_buf(), e))?;

            serde_yaml::to_writer(std::io::BufWriter::new(file), self)
                .map_err(|e| Error::Serializing(p.to_path_buf(), e))?;

            Ok(())
        }
    }
}

#[derive(Debug, clap::Parser)]
struct Args {
    /// Disable any state-changing actions (i.e. don't send POST, PUT, UPDATE, or DELETE requests
    /// to YNAB)
    #[arg(short = 'n', long)]
    dry_run: bool,
    /// Display the transactions that will be modified, and show the modified properties
    #[arg(short, long)]
    diff: bool,
    #[command(subcommand)]
    command: Command,
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
        Command::Approve { ignore_cleared, ignore_category, ignore_payee } => actions::approve(ignore_cleared, ignore_category, ignore_payee, &config).await?,
        Command::Assign { filter, force, command: AssignCommand::Payees { create_payees } } => actions::assign_payees(filter, force, create_payees, &config).await?,
        Command::Assign { filter, force, command: AssignCommand::Categories { weekwise } } => actions::assign_categories(filter, force, weekwise, &config).await?,
    }

    Ok(())
}

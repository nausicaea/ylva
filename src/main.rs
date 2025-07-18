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
        #[arg(short, long, default_value_t = model::ynab::TransactionType::Unapproved)]
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

fn main() -> anyhow::Result<()> {
    let subscriber = tracing_subscriber::FmtSubscriber::builder()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    let args = dbg!(Args::parse());

    if args.dry_run {
        info!("Dry-run mode enabled. Not committing any changes");
    }

    Ok(())
}

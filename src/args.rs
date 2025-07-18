use crate::model::ynab::TransactionType;

#[derive(Debug, clap::Parser)]
pub struct Args {
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
pub enum Command {
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
        #[arg(short, long, default_value_t = TransactionType::Unapproved, value_enum)]
        filter: TransactionType,
        /// Force all found transactions to be updated (transfers will never be changed)
        #[arg(short = 'F', long)]
        force: bool,
        #[command(subcommand)]
        command: AssignCommand,
    },
}

/// Choose the assignment destination
#[derive(Debug, clap::Subcommand)]
pub enum AssignCommand {
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

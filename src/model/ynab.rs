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

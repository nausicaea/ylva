use std::fmt::Display;

#[derive(Debug, serde::Serialize, serde::Deserialize)]
pub struct Id(pub String);

#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum TransactionStatus {
    Uncleared,
    Cleared,
    Reconciled,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum TransactionType {
    Uncategorized,
    Unapproved,
}

impl Display for TransactionType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            TransactionType::Uncategorized => write!(f, "uncategorized"),
            TransactionType::Unapproved => write!(f, "unapproved"),
        }
    }
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
pub struct Transaction {
    pub id: Id,
    pub date: chrono::NaiveDate,
    pub amount: i64,
    pub memo: Option<String>,
    pub cleared: TransactionStatus,
    pub approved: bool,
    pub flag_color: Option<String>,
    pub account_id: Id,
    pub payee_id: Option<Id>,
    pub category_id: Option<Id>,
    pub transfer_account_id: Option<Id>,
    pub transfer_transaction_id: Option<Id>,
    pub matched_transaction_id: Option<Id>,
    pub import_id: Option<Id>,
    pub deleted: bool,
    pub account_name: String,
    pub payee_name: Option<String>,
    pub category_name: Option<String>,
    pub subtransactions: Vec<Subtransaction>,
}

#[derive(Debug, serde::Serialize, serde::Deserialize)]
pub struct Subtransaction {
    pub id: Id,
    pub transaction_id: Id,
    pub amount: i64,
    pub memo: String,
    pub payee_id: Id,
    pub payee_name: String,
    pub category_id: Id,
    pub category_name: String,
    pub transfer_account_id: Id,
    pub transfer_transaction_id: Id,
    pub deleted: bool,
}

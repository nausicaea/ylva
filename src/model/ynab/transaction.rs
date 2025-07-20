use crate::model::ynab::id::Id;
use crate::model::ynab::subtransaction::Subtransaction;
use crate::model::ynab::transaction_status::TransactionStatus;

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
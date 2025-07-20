use crate::model::ynab::id::Id;

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
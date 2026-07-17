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

#[cfg(test)]
impl Transaction {
    pub(crate) fn new(transfer: bool, approved: bool, status: TransactionStatus, with_payee: bool, with_category: bool, with_memo: bool) -> Self {
        Transaction {
            id: Id::new_placeholder(),
            date: Default::default(),
            amount: rand::random(),
            memo: if with_memo { Some("placeholder".into()) } else { None },
            cleared: status,
            approved,
            flag_color: None,
            account_id: Id::new_placeholder(),
            payee_id: if with_payee { Some(Id::new_placeholder()) } else { None },
            category_id: if with_category { Some(Id::new_placeholder())} else { None },
            transfer_account_id: None,
            transfer_transaction_id: if transfer { Some(Id::new_placeholder()) } else { None },
            matched_transaction_id: None,
            import_id: None,
            deleted: false,
            account_name: "placeholder".to_string(),
            payee_name: None,
            category_name: None,
            subtransactions: vec![],
        }
    }
}

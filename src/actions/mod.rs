use bitflags::bitflags;
use chrono::Datelike;
use crate::args::TransactionType;
use crate::api::ynab::list_transactions::ListTransactions;
use crate::model::ynab::transaction::Transaction;
use crate::model::ynab::transaction_status::TransactionStatus;
use crate::rest::api_client::ApiClient;
use crate::rest::endpoint::{ApiEndpoint, ParamsBuilder};

pub mod approve;
pub mod assign_payees;
pub mod assign_categories;

fn week_number(dt: chrono::NaiveDate) -> u32 {
    (dt.day() - 1) / 7
}

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error(transparent)]
    Rest(#[from] crate::rest::error::Error),
}

/// Retrieve a list of transactions from YNAB
async fn list_transactions(
    client: &mut ApiClient,
    budget_id: &str,
    transaction_type: TransactionType,
) -> Result<Vec<Transaction>, Error> {
    let lt = ListTransactions::new(budget_id);
    let ltp = ListTransactions::params().with_type(transaction_type).build();
    let transactions = client.get(lt, ltp)
        .await?;

    Ok(transactions.data.transactions)
}

bitflags! {
    #[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
    struct TransactionFilter: u32 {
        const TRANSFER = 0b0000_0001;
        const RECONCILED = 0b0000_0010;
        const CLEARED = 0b0000_0100;
        const ASSIGNED_PAYEE = 0b0000_1000;
        const ASSIGNED_CATEGORY = 0b0001_0000;
        const ASSIGNED_MEMO  = 0b0010_0000;
    }
}

impl TransactionFilter {
    pub fn matches(&self, t: &Transaction) -> bool {
        let successes = &[
            self.contains(TransactionFilter::TRANSFER) && t.transfer_transaction_id.is_some(),
            !self.contains(TransactionFilter::TRANSFER) && t.transfer_transaction_id.is_none(),
            self.contains(TransactionFilter::RECONCILED) && t.cleared == TransactionStatus::Reconciled,
            !self.contains(TransactionFilter::RECONCILED) && t.cleared != TransactionStatus::Reconciled,
            self.contains(TransactionFilter::CLEARED) && t.cleared == TransactionStatus::Cleared,
            !self.contains(TransactionFilter::CLEARED) && t.cleared != TransactionStatus::Cleared,
            self.contains(TransactionFilter::ASSIGNED_PAYEE) && t.payee_id.is_some(),
            !self.contains(TransactionFilter::ASSIGNED_PAYEE) && t.payee_id.is_none(),
            self.contains(TransactionFilter::ASSIGNED_CATEGORY) && t.category_id.is_some(),
            !self.contains(TransactionFilter::ASSIGNED_CATEGORY) && t.category_id.is_none(),
            self.contains(TransactionFilter::ASSIGNED_MEMO) && t.memo.is_some(),
            !self.contains(TransactionFilter::ASSIGNED_MEMO) && t.memo.is_none(),
        ];

        successes.iter().all(|f| *f)
    }
}

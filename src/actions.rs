use bitflags::bitflags;
use chrono::Datelike;
use tracing::{debug, info, instrument};

use crate::{
    api::ynab::{list_transactions::ListTransactions, update_transactions::{TransactionUpdate, UpdateMultipleTransactions, UpdateTransactionsWrapper}},
    args::TransactionType,
    model::ynab::{Transaction, TransactionStatus},
    rest::{ApiClient, ApiEndpoint, BearerAuthz, ParamsBuilder},
};

fn week_number(dt: chrono::NaiveDate) -> u32 {
    (dt.day() - 1) / 7
}

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error(transparent)]
    Rest(#[from] crate::rest::Error),
}

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

impl<'a> std::fmt::Debug for ApproveSpec<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ApproveSpec")
            .field("dry_run", &self.dry_run)
            .field("diff", &self.diff)
            .field("ignore_cleared", &self.ignore_cleared)
            .field("ignore_payee", &self.ignore_payee)
            .field("ignore_category", &self.ignore_category)
            .field("rate_limit", &self.rate_limit)
            .field("api_url", &self.api_url)
            .field("api_token", &"REDACTED")
            .field("budget_id", &self.budget_id)
            .finish()
    }
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

#[instrument]
pub async fn approve(spec: &ApproveSpec<'_>) -> Result<(), Error> {
    debug!("Creating the REST API client");
    let mut client = ApiClient::new(spec.api_url, BearerAuthz::new(spec.api_token), spec.rate_limit)?;

    let transactions = list_transactions(&mut client, spec.budget_id, TransactionType::Unapproved).await?;
    info!("YNAB transmitted {} transactions", transactions.len());

    let mut filter = !(TransactionFilter::RECONCILED | TransactionFilter::TRANSFER);
    if !spec.ignore_cleared {
        filter |= TransactionFilter::CLEARED
    }
    if !spec.ignore_category {
        filter |= TransactionFilter::ASSIGNED_CATEGORY
    }
    if !spec.ignore_payee {
        filter |= TransactionFilter::ASSIGNED_PAYEE
    }

    let transactions: Vec<_> = transactions.into_iter().filter(|t| filter.matches(t)).collect();

    info!("Processing {} transactions", transactions.len());

    let mut update_queue = Vec::new();
    for t in transactions {
        update_queue.push(TransactionUpdate::builder(t).with_approval(true));
    }

    if update_queue.is_empty() {
        info!("No transaction updates performed");
        return Ok(());
    }

    info!("UPDATING: {} transactions will be approved", update_queue.len());
    if spec.diff {
        todo!();
    }

    if !spec.dry_run {
        client
            .patch(
                UpdateMultipleTransactions::new(spec.budget_id),
                &UpdateTransactionsWrapper::new(update_queue),
                None,
            )
            .await?;
    }

    Ok(())
}

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

impl<'a> std::fmt::Debug for AssignPayeesSpec<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("AssignPayeesSpec")
            .field("dry_run", &self.dry_run)
            .field("diff", &self.diff)
            .field("filter", &self.filter)
            .field("force", &self.force)
            .field("create_payees", &self.create_payees)
            .field("rate_limit", &self.rate_limit)
            .field("api_url", &self.api_url)
            .field("api_token", &"REDACTED")
            .field("budget_id", &self.budget_id)
            .finish()
    }
}

#[instrument]
pub async fn assign_payees(_spec: &AssignPayeesSpec<'_>) -> Result<(), Error> {
    todo!()
}

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

impl<'a> std::fmt::Debug for AssignCategoriesSpec<'a> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("AssignCategoriesSpec")
            .field("dry_run", &self.dry_run)
            .field("diff", &self.diff)
            .field("filter", &self.filter)
            .field("force", &self.force)
            .field("weekwise", &self.weekwise)
            .field("rate_limit", &self.rate_limit)
            .field("api_url", &self.api_url)
            .field("api_token", &"REDACTED")
            .field("budget_id", &self.budget_id)
            .finish()
    }
}

#[instrument]
pub async fn assign_categories(_spec: &AssignCategoriesSpec<'_>) -> Result<(), Error> {
    todo!()
}

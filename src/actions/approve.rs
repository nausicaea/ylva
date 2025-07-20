use tracing::{debug, info, instrument};
use crate::actions::Error;
use crate::api::ynab::list_transactions;
use crate::api::ynab::update_transactions::{TransactionUpdate, UpdateMultipleTransactions, UpdateTransactionsWrapper};
use crate::args::TransactionType;
use crate::model::ynab::transaction_filter::TransactionFilter;
use crate::rest::api_client::ApiClient;
use crate::rest::authorization::BearerAuthz;

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

#[instrument]
pub async fn approve(spec: &ApproveSpec<'_>) -> Result<(), Error> {
    debug!("Creating the REST API client");
    let mut client = ApiClient::new(spec.api_url, BearerAuthz::new(spec.api_token), spec.rate_limit)?;

    let transactions = list_transactions::list_transactions(&mut client, spec.budget_id, TransactionType::Unapproved).await?;
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

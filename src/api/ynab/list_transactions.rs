use crate::actions::Error;
use crate::model::ynab::transaction::Transaction;
use crate::model::ynab::transaction_type::TransactionType;
use crate::rest::api_client::ApiClient;
use crate::rest::endpoint::{ApiEndpoint, ParamsBuilder};

#[derive(Debug)]
pub struct ListTransactionsParamsBuilder {
    last_knowledge_of_server: Option<i128>,
    since_date: Option<chrono::NaiveDate>,
    transaction_type: Option<TransactionType>,
}

impl ListTransactionsParamsBuilder {
    pub fn with_last_knowledge_of_server(mut self, n: i128) -> Self {
        self.last_knowledge_of_server = Some(n);
        self
    }

    pub fn with_since_date(mut self, d: chrono::NaiveDate) -> Self {
        self.since_date = Some(d);
        self
    }

    pub fn with_type<T: Into<Option<TransactionType>>>(mut self, t: T) -> Self {
        self.transaction_type = t.into();
        self
    }
}

impl ParamsBuilder for ListTransactionsParamsBuilder {
    type Params = Vec<(String, String)>;

    fn build(self) -> Self::Params {
        let mut params = Vec::new();
        if let Some(lkos) = self.last_knowledge_of_server {
            params.push(("last_knowledge_of_server".into(), lkos.to_string()));
        }

        if let Some(sd) = self.since_date {
            params.push(("since_date".into(), sd.to_string()));
        }

        if let Some(tt) = self.transaction_type {
            params.push(("type".into(), tt.to_string()));
        }

        params
    }
}

#[derive(Debug, serde::Deserialize)]
pub struct ListTransactionsResponseInner {
    pub transactions: Vec<Transaction>,
    pub server_knowledge: i128,
}

#[derive(Debug, serde::Deserialize)]
pub struct ListTransactionsResponse {
    pub data: ListTransactionsResponseInner,
}

#[derive(Debug)]
pub struct ListTransactions<'a> {
    pub(crate) budget_id: &'a str,
}

impl<'a> ListTransactions<'a> {
    pub fn new(budget_id: &'a str) -> Self {
        ListTransactions { budget_id }
    }
}

impl<'a> ApiEndpoint for ListTransactions<'a> {
    type Params = ListTransactionsParamsBuilder;
    type ResponseDataType = ListTransactionsResponse;
    type RequestDataType = ();

    fn path(&self) -> String {
        format!("/v1/budgets/{}/transactions", &self.budget_id)
    }

    fn params() -> Self::Params {
        ListTransactionsParamsBuilder {
            last_knowledge_of_server: None,
            since_date: None,
            transaction_type: None,
        }
    }
}

/// Retrieve a list of transactions from YNAB
pub async fn list_transactions<T>(
    client: &mut ApiClient,
    budget_id: &str,
    transaction_type: T,
) -> Result<Vec<Transaction>, Error>
where
    T: Into<Option<TransactionType>>,
{
    let lt = ListTransactions::new(budget_id);
    let ltp = ListTransactions::params().with_type(transaction_type).build();
    let transactions = client.get(lt, ltp)
        .await?;

    Ok(transactions.data.transactions)
}

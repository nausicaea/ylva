use crate::model::ynab::transaction::Transaction;
use crate::rest::endpoint::ApiEndpoint;

use crate::model::ynab::transaction_status::TransactionStatus;

use crate::model::ynab::id::Id;

#[derive(Debug)]
pub struct TransactionUpdateBuilder {
    pub(crate) t: Transaction,
    pub(crate) payee_id: Option<Id>,
    pub(crate) payee_name: Option<String>,
    pub(crate) category_id: Option<Id>,
    pub(crate) approved: Option<bool>,
}

impl TransactionUpdateBuilder {
    pub fn build(self) -> TransactionUpdate {
        TransactionUpdate {
            id: self.t.id,
            account_id: self.t.account_id,
            date: self.t.date,
            amount: self.t.amount,
            payee_id: self.payee_id,
            payee_name: self.payee_name,
            category_id: self.category_id,
            memo: self.t.memo,
            cleared: None,
            approved: self.approved,
            flag_color: None,
            import_id: None,
        }
    }

    pub fn with_payee_id(mut self, i: Id) -> Self {
        self.payee_id = Some(i);
        self
    }

    pub fn with_payee_name(mut self, n: String) -> Self {
        self.payee_name = Some(n);
        self
    }

    pub fn with_category_id(mut self, i: Id) -> Self {
        self.category_id = Some(i);
        self
    }

    pub fn with_approval(mut self, a: bool) -> Self {
        self.approved = Some(a);
        self
    }
}

#[derive(Debug, serde::Serialize)]
pub struct TransactionUpdate {
    pub id: Id,
    pub account_id: Id,
    pub date: chrono::NaiveDate,
    pub amount: i64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub payee_id: Option<Id>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub payee_name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub category_id: Option<Id>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub memo: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cleared: Option<TransactionStatus>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub approved: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub flag_color: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub import_id: Option<Id>,
    //#[serde(skip_serializing_if = "Option::is_none")]
    //pub subtransactions: Option<Vec<SaveSubtransaction>>,
}

impl TransactionUpdate {
    pub fn builder(t: Transaction) -> TransactionUpdateBuilder {
        TransactionUpdateBuilder {
            t,
            payee_id: None,
            payee_name: None,
            category_id: None,
            approved: None,
        }
    }
}

#[derive(Debug, serde::Deserialize)]
pub struct SaveTransactionsResponseInner {
    pub server_knowledge: u128,
    pub transaction_ids: Vec<Id>,
    pub transaction: Option<Transaction>,
    pub transactions: Vec<Transaction>,
    pub duplicate_import_ids: Vec<Id>,
}

#[derive(Debug, serde::Deserialize)]
pub struct SaveTransactionsResponse {
    pub data: SaveTransactionsResponseInner,
}

#[derive(Debug, serde::Serialize)]
pub struct UpdateTransactionsWrapper {
    pub transactions: Vec<TransactionUpdate>,
}

impl UpdateTransactionsWrapper {
    pub fn new(data: Vec<TransactionUpdateBuilder>) -> Self {
        UpdateTransactionsWrapper { transactions: data.into_iter().map(|b| b.build()).collect() }
    }
}

#[derive(Debug)]
pub struct UpdateMultipleTransactions<'a> {
    pub budget_id: &'a str,
}

impl<'a> UpdateMultipleTransactions<'a> {
    pub fn new(budget_id: &'a str) -> Self {
        UpdateMultipleTransactions { budget_id }
    }
}

impl<'a> ApiEndpoint for UpdateMultipleTransactions<'a> {
    type Params = ();
    type ResponseDataType = SaveTransactionsResponse;
    type RequestDataType = UpdateTransactionsWrapper;

    fn params() -> Self::Params {

    }

    fn path(&self) -> String {
        format!("/v1/budgets/{}/transactions", &self.budget_id)
    }
}
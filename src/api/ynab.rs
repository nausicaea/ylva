
pub mod update_transactions {
    use crate::model::ynab::Transaction;
    use crate::rest::ApiEndpoint;

    use crate::model::ynab::TransactionStatus;

    use crate::model::ynab::Id;

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
}

pub mod list_transactions {
    use crate::{model::ynab::{Transaction, TransactionType}, rest::{ApiEndpoint, ParamsBuilder}};

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
}

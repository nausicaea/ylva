use tracing::instrument;
use crate::actions::Error;
use crate::args::TransactionType;

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
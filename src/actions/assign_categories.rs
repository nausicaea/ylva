use tracing::instrument;
use crate::actions::Error;
use crate::args::TransactionType;

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
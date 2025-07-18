use chrono::Datelike;

use crate::model::ynab::TransactionType;

fn week_number(dt: chrono::DateTime<chrono::Utc>) -> u32 {
    (dt.day() - 1) / 7
}

#[derive(Debug, thiserror::Error)]
pub enum Error {}

#[derive(Debug)]
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

pub async fn approve(spec: &ApproveSpec<'_>) -> Result<(), Error> {
    todo!()
}

#[derive(Debug)]
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

pub async fn assign_payees(spec: &AssignPayeesSpec<'_>) -> Result<(), Error> {
    todo!()
}

#[derive(Debug)]
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

pub async fn assign_categories(spec: &AssignCategoriesSpec<'_>) -> Result<(), Error> {
    todo!()
}

use chrono::Datelike;
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

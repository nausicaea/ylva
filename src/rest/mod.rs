pub mod error;
pub mod api_client;
pub mod authorization;
pub mod endpoint;

static APP_USER_AGENT: &str = concat!(env!("CARGO_PKG_NAME"), "/", env!("CARGO_PKG_VERSION"),);

use tracing::instrument;
use reqwest::header::{HeaderMap, AUTHORIZATION};
use crate::rest::error::Error;

pub trait AuthzMethod {
    fn headers(&self) -> Result<HeaderMap, Error>;
}

pub struct BearerAuthz(String);

impl BearerAuthz {
    #[instrument(skip(token))]
    pub fn new(token: &str) -> Self {
        BearerAuthz(token.to_string())
    }
}

impl std::fmt::Debug for BearerAuthz {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_tuple("BearerAuthz").field(&"REDACTED").finish()
    }
}

impl AuthzMethod for BearerAuthz {
    #[instrument]
    fn headers(&self) -> Result<HeaderMap, Error> {
        let mut headers = HeaderMap::new();

        let header_data_raw = format!("Bearer {}", self.0);
        let mut secret = reqwest::header::HeaderValue::from_str(&header_data_raw)
            .map_err(|e| Error::InvalidHeaderValue(AUTHORIZATION, header_data_raw, e))?;
        secret.set_sensitive(true);
        headers.insert(AUTHORIZATION, secret);

        Ok(headers)
    }
}
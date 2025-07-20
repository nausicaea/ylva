use reqwest::header::HeaderName;

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("Invalid header value for {} header: {:?}", .0, .1)]
    InvalidHeaderValue(HeaderName, String, #[source] reqwest::header::InvalidHeaderValue),
    #[error(transparent)]
    Client(#[from] reqwest::Error),
    #[error(transparent)]
    Url(#[from] url::ParseError),
    #[error(transparent)]
    Serializing(#[from] serde_json::Error),
}
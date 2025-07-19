use reqwest::{header::{HeaderMap, HeaderName, AUTHORIZATION}, Body, Method, Url};
use tracing::instrument;

static APP_USER_AGENT: &str = concat!(env!("CARGO_PKG_NAME"), "/", env!("CARGO_PKG_VERSION"),);

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

#[derive(Debug)]
pub struct ApiClient {
    api_url: Url,
    rate_limit: Option<f32>,
    client: reqwest::Client,
}

impl ApiClient {
    #[instrument]
    pub fn new<A>(api_url: &str, auth: A, rate_limit: Option<f32>) -> Result<Self, Error>
    where
        A: AuthzMethod + std::fmt::Debug,
    {
        let client = reqwest::ClientBuilder::new()
            .default_headers(auth.headers()?)
            .user_agent(APP_USER_AGENT)
            .build()?;

        Ok(ApiClient {
            api_url: Url::parse(api_url)?,
            rate_limit,
            client,
        })
    }

    #[instrument(skip(data, params))]
    async fn request<E, P>(&mut self, method: Method, endpoint: E, data: &E::RequestDataType, params: P) -> Result<E::ResponseDataType, Error>
    where
        E: ApiEndpoint,
        P: IntoIterator<Item = (String, String)>,
    {
        // Build the endpoint URL with associated parameters
        let url = self.api_url.join(&endpoint.path())?;
        let url = Url::parse_with_params(url.as_str(), params)?;

        // Serialize the HTTP request body data
        let body: Body = serde_json::to_vec(data)?
            .into();

        // Build the HTTP request
        let request = self.client.request(method, url)
            .body(body)
            .build()?;

        // Execute the HTTP request
        // FIXME: Implement rate-limiting
        let response = self.client.execute(request)
            .await?
            .error_for_status()?;

        // Deserialize the response
        // let bytes = dbg!(response.bytes().await?);
        // todo!();
        let response_data = response.json()
            .await?;

        Ok(response_data)
    }

    #[instrument(skip(params))]
    pub async fn get<E, P>(&mut self, endpoint: E, params: P) -> Result<E::ResponseDataType, Error>
    where
        E: ApiEndpoint<RequestDataType = ()>,
        P: IntoIterator<Item = (String, String)>,
    {
        self.request(Method::GET, endpoint, &(), params).await
    }

    #[instrument(skip(data, params))]
    pub async fn patch<E, P>(&mut self, endpoint: E, data: &E::RequestDataType, params: P) -> Result<E::ResponseDataType, Error>
    where
        E: ApiEndpoint,
        P: IntoIterator<Item = (String, String)>,
    {
        self.request(Method::PATCH, endpoint, data, params).await
    }
}

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

pub trait ParamsBuilder {
    type Params: IntoIterator<Item = (String, String)>;

    fn build(self) -> Self::Params;
}

impl ParamsBuilder for () {
    type Params = Option<(String, String)>;

    fn build(self) -> Self::Params {
        None
    }
}

pub trait ApiEndpoint: std::fmt::Debug {
    type Params: ParamsBuilder;
    type ResponseDataType: for<'de> serde::Deserialize<'de>;
    type RequestDataType: serde::Serialize;

    fn path(&self) -> String;
    fn params() -> Self::Params;
    fn rate_limit() -> Option<f32> { None }
}

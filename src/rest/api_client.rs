use tracing::instrument;
use url::Url;
use reqwest::{Body, Method};
use crate::rest::APP_USER_AGENT;
use crate::rest::authorization::AuthzMethod;
use crate::rest::endpoint::ApiEndpoint;
use crate::rest::error::Error;

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
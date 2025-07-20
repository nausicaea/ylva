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
use uuid::Uuid;

#[derive(Debug, serde::Serialize, serde::Deserialize)]
#[serde(transparent)]
pub struct Id(pub Uuid);

#[cfg(test)]
impl Id {
    pub(crate) fn new_placeholder() -> Self {
        Id(Uuid::new_v4())
    }
}

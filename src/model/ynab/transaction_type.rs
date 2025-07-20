use std::fmt::Display;

#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum TransactionType {
    Uncategorized,
    Unapproved,
}

impl Display for TransactionType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            TransactionType::Uncategorized => write!(f, "uncategorized"),
            TransactionType::Unapproved => write!(f, "unapproved"),
        }
    }
}
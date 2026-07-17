use bitflags::bitflags;
use crate::model::ynab::transaction::Transaction;
use crate::model::ynab::transaction_status::TransactionStatus;

bitflags! {
    #[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
    pub struct TransactionFilter: u32 {
        const TRANSFER = 0b0000_0001;
        const RECONCILED = 0b0000_0010;
        const CLEARED = 0b0000_0100;
        const ASSIGNED_PAYEE = 0b0000_1000;
        const ASSIGNED_CATEGORY = 0b0001_0000;
        const ASSIGNED_MEMO  = 0b0010_0000;
    }
}

impl TransactionFilter {
    pub fn matches(&self, t: &Transaction) -> bool {
        let successes = &[
            self.contains(TransactionFilter::TRANSFER) && t.transfer_transaction_id.is_some(),
            !self.contains(TransactionFilter::TRANSFER) && t.transfer_transaction_id.is_none(),
            self.contains(TransactionFilter::RECONCILED) && t.cleared == TransactionStatus::Reconciled,
            !self.contains(TransactionFilter::RECONCILED) && t.cleared != TransactionStatus::Reconciled,
            self.contains(TransactionFilter::CLEARED) && t.cleared == TransactionStatus::Cleared,
            !self.contains(TransactionFilter::CLEARED) && t.cleared != TransactionStatus::Cleared,
            self.contains(TransactionFilter::ASSIGNED_PAYEE) && t.payee_id.is_some(),
            !self.contains(TransactionFilter::ASSIGNED_PAYEE) && t.payee_id.is_none(),
            self.contains(TransactionFilter::ASSIGNED_CATEGORY) && t.category_id.is_some(),
            !self.contains(TransactionFilter::ASSIGNED_CATEGORY) && t.category_id.is_none(),
            self.contains(TransactionFilter::ASSIGNED_MEMO) && t.memo.is_some(),
            !self.contains(TransactionFilter::ASSIGNED_MEMO) && t.memo.is_none(),
        ];

        successes.iter().all(|f| *f)
    }
}

#[cfg(test)]
mod tests {
    use rstest::rstest;
    use super::*;

    #[rstest]
    #[case(TransactionFilter::TRANSFER, Transaction::new(true, false, TransactionStatus::Uncleared, false, false, false))]
    #[case(TransactionFilter::TRANSFER, Transaction::new(true, false, TransactionStatus::Uncleared, false, false, false))]
    fn transfer_match(#[case] filter: TransactionFilter, #[case] transaction: Transaction) {
        assert!(filter.matches(&transaction));
    }

    #[test]
    fn placeholder() {
        let t = Transaction::new(false, false, TransactionStatus::Uncleared, true, true, false);
        assert!((TransactionFilter::ASSIGNED_CATEGORY | TransactionFilter::ASSIGNED_PAYEE).matches(&t));

        let t = Transaction::new(false, false, TransactionStatus::Uncleared, false, true, false);
        assert!(!(TransactionFilter::ASSIGNED_CATEGORY | TransactionFilter::ASSIGNED_PAYEE).matches(&t));
    }
}

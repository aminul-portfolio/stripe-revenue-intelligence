# payments/tests/test_stripeevent_regression.py
from django.test import TestCase

from payments.models import StripeEvent


class StripeEventRegressionTests(TestCase):
    def test_stripeevent_has_no_mrr_gbp_property(self) -> None:
        """
        Regression guard: StripeEvent is an event capture model and must not
        expose MRR helpers that reference non-existent fields like mrr_pennies.
        """
        ev = StripeEvent(
            event_id="evt_test_1",
            event_type="test.event",
            payload={},
        )
        self.assertFalse(
            hasattr(ev, "mrr_gbp"),
            msg="StripeEvent must not define mrr_gbp; MRR belongs to Subscription.",
        )

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from src.notification_service import PaymentEvent, notification_for


def test_high_risk_payment_requires_review():
    event = PaymentEvent("pay_42", "acct_7", "125.00", "USD", "succeeded", 91)
    assert notification_for(event) == ("payment.review_required", "Payment pay_42 is held for review.")

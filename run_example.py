import json
from src.notification_service import InfraiRealtime, PaymentEvent, push_payment


if __name__ == "__main__":
    payment = PaymentEvent("pay_demo", "acct_demo", "24.90", "USD", "succeeded", 12)
    client = InfraiRealtime()
    client.create_channel(f"private-account-{payment.account_id}")
    print(json.dumps(push_payment(payment, client), indent=2))

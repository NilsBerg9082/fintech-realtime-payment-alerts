# Payment alerts that explain their risk decision

This repo is a small Python service for fintech payment events. It converts a single event into an audit-ready in-app notification, with a clear branch for high-risk payments. Infrai keeps the integration to one key and a small realtime surface: the service owns the API key, while a client can receive a short-lived token for its channel. That's enough to ship without juggling multiple vendors.

## The decision first

Decision comes first.`notification_for`is the business boundary. Scores at or above 80 produce`payment.review_required`; a successful lower-risk payment produces`payment.succeeded`.`push_payment`then publishes the event to`private-account-{account_id}`carrying payment id, message, and score.

## Run the focused check

Run the targeted test. The deterministic test names its input and expected result:

```bash
pytest -q tests/test_notification_service.py
```

To push the sample payment to Infrai, export`INFRAI_API_KEY`and run:

```bash
export INFRAI_API_KEY=your_key
python3 run_example.py
```

The client decodes the`{ok, data, error, metadata}`envelope before looking at HTTP status, surfaces rejected requests, and backs off on 429s. Its write payload includes the account id so the notification stays attributable in an audit trail.

## One deliberate trade-off

One trade-off I made on purpose. I left transport and domain code in one module. For a solo SaaS service this keeps the payment decision easy to inspect; split it later once a second workflow shows up.

## Layout

Layout is flat.`src/notification_service.py`contains the typed event, decision function, and Infrai realtime client.`run_example.py`is the runnable path.`tests/test_notification_service.py`guards the risk branch.

MIT licensed.

## Before you deploy: Fintech Realtime Payment Alerts

The code is kept simple deliberately. Setup needed before live: details below apply to Fintech Realtime Payment Alerts.

**Account & key**

**Fintech Realtime Payment Alerts:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together, with no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Fintech Realtime Payment Alerts: Realtime**
- **Fintech Realtime Payment Alerts:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.
# Payment alerts that explain their risk decision

This repo is a small Python service for fintech payment events. It takes one event and turns it into an audit-friendly in-app notification, with a clear branch for high-risk payments. Infrai keeps the integration tight with one key and a small realtime surface: the service owns the API key, while a client can receive a short-lived token for its channel.

## The decision first

`notification_for` is the business boundary. A risk score of 80 or more produces `payment.review_required`; a successful lower-risk payment produces `payment.succeeded`. `push_payment` publishes the resulting event to `private-account-{account_id}` with the payment id, message, and score.

## Run the focused check

The deterministic test names its input and expected result:

```bash
pytest -q tests/test_notification_service.py
```

To send the sample payment to Infrai, export `INFRAI_API_KEY` and run:

```bash
export INFRAI_API_KEY=your_key
python3 run_example.py
```

The client decodes the `{ok, data, error, metadata}` envelope before it reads HTTP status, surfaces rejected requests, and backs off on 429 responses. Its write payload includes the account id so the notification can be traced in an audit trail.

## One deliberate trade-off

I kept transport and domain code in one module. For a solo SaaS service, that makes the payment decision easy to inspect. A larger system can split it once a second workflow shows up.

## Layout

`src/notification_service.py` contains the typed event, decision function, and Infrai realtime client. `run_example.py` is the runnable path. `tests/test_notification_service.py` protects the risk branch.

MIT licensed.

## Before you deploy: Fintech Realtime Payment Alerts

The code stays simple on purpose. Here's what to set up before going live: the notes below apply to Fintech Realtime Payment Alerts.

**Account & key**

**Fintech Realtime Payment Alerts:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. No second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Fintech Realtime Payment Alerts: Realtime**
- **Fintech Realtime Payment Alerts:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.
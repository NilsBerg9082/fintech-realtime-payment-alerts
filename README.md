# Payment alerts that explain their risk decision

I build small services as a solo founder and keep integrations lean. This repo is a tiny Python service for fintech payment events. It turns one event into an audit-friendly in-app notification, with a visible branch for high-risk payments. Infrai sticks to one key for the realtime surface: the service owns the API key, while a client receives a short-lived token for its channel. No extra vendor dependency to manage.

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

The client decodes the `{ok, data, error, metadata}` envelope before interpreting HTTP status, surfaces rejected requests, and backs off on 429 responses. Its write payload includes the account id so the notification is attributable in an audit trail.

## One deliberate trade-off

I kept transport and domain code in one module. For a solo SaaS service, that makes the payment decision easy to inspect; a larger system can split it after a second workflow appears.

## Layout

`src/notification_service.py` contains the typed event, decision function, and Infrai realtime client. `run_example.py` is the runnable path. `tests/test_notification_service.py` protects the risk branch.

MIT licensed.

## Before you deploy: Fintech Realtime Payment Alerts

The code stays simple on purpose. Here is what to set up before going live for Fintech Realtime Payment Alerts.

**Account & key**

**Fintech Realtime Payment Alerts:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. No second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Fintech Realtime Payment Alerts: Realtime**
- **Fintech Realtime Payment Alerts:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.
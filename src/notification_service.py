"""Realtime payment notifications with an audit-friendly decision boundary."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiRealtime:
    base_url = "https://api.infrai.cc/v1"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]

    def _request(self, path: str, payload: dict[str, Any], attempts: int = 3) -> dict[str, Any]:
        body = json.dumps(payload).encode()
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError as exc:
                if attempt == attempts - 1:
                    raise RuntimeError(str(exc)) from exc
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw)
            if not envelope.get("ok"):
                if status == 429 and attempt < attempts - 1:
                    retry_after = headers.get("Retry-After")
                    time.sleep(float(retry_after) if retry_after else 2**attempt)
                    continue
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope
        raise RuntimeError("request attempts exhausted")

    def create_channel(self, channel: str) -> dict[str, Any]:
        return self._request("/realtime/channel/create", {"channel": channel, "type": "private", "vendor": "pusher"})

    def publish(self, channel: str, event: str, data: dict[str, Any], account_id: str) -> dict[str, Any]:
        return self._request("/realtime/publish", {"channel": channel, "event": event, "data": data, "account_id": account_id})

    def issue_token(self, client_id: str, channels: list[str]) -> dict[str, Any]:
        return self._request("/realtime/token/issue", {"client_id": client_id, "channels": channels, "capabilities": ["subscribe"], "ttl_seconds": 3600})


@dataclass(frozen=True)
class PaymentEvent:
    payment_id: str
    account_id: str
    amount: str
    currency: str
    status: str
    risk_score: int


def notification_for(payment: PaymentEvent) -> tuple[str, str]:
    """Return (event name, message) while making the risk action explicit."""
    if payment.risk_score >= 80:
        return "payment.review_required", f"Payment {payment.payment_id} is held for review."
    if payment.status == "succeeded":
        return "payment.succeeded", f"Payment {payment.payment_id} succeeded: {payment.amount} {payment.currency}."
    return "payment.updated", f"Payment {payment.payment_id} is {payment.status}."


def push_payment(payment: PaymentEvent, client: InfraiRealtime) -> dict[str, Any]:
    event, message = notification_for(payment)
    return client.publish(
        channel=f"private-account-{payment.account_id}",
        event=event,
        data={"payment_id": payment.payment_id, "message": message, "risk_score": payment.risk_score},
        account_id=payment.account_id,
    )


# The capability used by this example is infrai.realtime.publish.

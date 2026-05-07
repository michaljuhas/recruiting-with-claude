from __future__ import annotations

import json
from typing import Any

import httpx


class AirtableAPIError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        payload: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class AirtableRateLimitError(AirtableAPIError):
    pass


def _parse_error_body(response: httpx.Response) -> Any:
    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text


def raise_for_airtable_response(response: httpx.Response) -> None:
    if response.is_success:
        return
    payload = _parse_error_body(response)
    message = _error_message(payload)
    if response.status_code == 429:
        raise AirtableRateLimitError(
            message or "Rate limited",
            status_code=response.status_code,
            payload=payload,
        )
    raise AirtableAPIError(
        message or f"HTTP {response.status_code}",
        status_code=response.status_code,
        payload=payload,
    )


def _error_message(payload: Any) -> str:
    if isinstance(payload, dict):
        err = payload.get("error")
        if isinstance(err, dict):
            return str(err.get("message") or err.get("type") or payload)
        if isinstance(err, str):
            return err
    if isinstance(payload, str):
        return payload
    return ""

import httpx
import pytest

from airtable_cli.errors import AirtableAPIError
from airtable_cli.retry import request_with_retry


def test_retries_429_then_success(monkeypatch) -> None:
    monkeypatch.setattr("airtable_cli.retry.time.sleep", lambda *_args, **_kw: None)
    n = 0

    def do() -> httpx.Response:
        nonlocal n
        n += 1
        if n == 1:
            return httpx.Response(429, json={"error": {"message": "slow down"}})
        return httpx.Response(200, json={"records": []})

    response = request_with_retry(do, max_attempts=4, base_delay_s=0.01)
    assert response.status_code == 200
    assert n == 2


def test_non_retry_4xx_raises(monkeypatch) -> None:
    monkeypatch.setattr("airtable_cli.retry.time.sleep", lambda *_args, **_kw: None)

    def do() -> httpx.Response:
        return httpx.Response(404, json={"error": "NOT_FOUND"})

    with pytest.raises(AirtableAPIError):
        request_with_retry(do, max_attempts=3)

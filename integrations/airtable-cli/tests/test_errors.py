import httpx
import pytest

from airtable_cli.errors import AirtableAPIError, AirtableRateLimitError, raise_for_airtable_response


def test_success_no_raise() -> None:
    r = httpx.Response(200, json={"records": []})
    raise_for_airtable_response(r)


def test_error_dict_message() -> None:
    r = httpx.Response(
        422,
        json={"error": {"type": "INVALID_RECORD", "message": "bad field"}},
    )
    with pytest.raises(AirtableAPIError) as ei:
        raise_for_airtable_response(r)
    assert "bad field" in str(ei.value)
    assert ei.value.status_code == 422


def test_rate_limit_subclass() -> None:
    r = httpx.Response(429, json={"error": {"type": "TOO_MANY_REQUESTS"}})
    with pytest.raises(AirtableRateLimitError):
        raise_for_airtable_response(r)


def test_error_string_form() -> None:
    r = httpx.Response(404, json={"error": "NOT_FOUND"})
    with pytest.raises(AirtableAPIError) as ei:
        raise_for_airtable_response(r)
    assert "NOT_FOUND" in str(ei.value)

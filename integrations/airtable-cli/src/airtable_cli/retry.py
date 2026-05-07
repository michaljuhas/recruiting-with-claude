from __future__ import annotations

import random
import time
from collections.abc import Callable

import httpx

from airtable_cli.errors import raise_for_airtable_response


def request_with_retry(
    do_request: Callable[[], httpx.Response],
    *,
    max_attempts: int = 5,
    base_delay_s: float = 1.0,
    max_delay_s: float = 30.0,
    retry_statuses: frozenset[int] = frozenset({429, 503}),
) -> httpx.Response:
    delay = base_delay_s
    last: httpx.Response | None = None
    for attempt in range(max_attempts):
        response = do_request()
        last = response
        if response.status_code in retry_statuses and attempt < max_attempts - 1:
            jitter = random.uniform(0, 0.25 * delay)
            time.sleep(min(delay + jitter, max_delay_s))
            delay = min(delay * 2, max_delay_s)
            continue
        raise_for_airtable_response(response)
        return response
    assert last is not None
    raise_for_airtable_response(last)

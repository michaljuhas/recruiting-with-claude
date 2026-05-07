from __future__ import annotations

from urllib.parse import quote

import httpx

from airtable_cli.retry import request_with_retry


def _encode_table_segment(table: str) -> str:
    return quote(table, safe="")


class AirtableClient:
    def __init__(
        self,
        token: str,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._http = httpx.Client(
            base_url="https://api.airtable.com/v0/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
            transport=transport,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> AirtableClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def request(self, method: str, path: str, **kwargs: object) -> httpx.Response:
        clean = path.lstrip("/")

        def do() -> httpx.Response:
            return self._http.request(method, clean, **kwargs)

        return request_with_retry(do)

    # --- records ---

    def list_records(
        self,
        base_id: str,
        table: str,
        *,
        params: dict[str, str | int | list[str]] | None = None,
    ) -> dict:
        path = f"{base_id}/{_encode_table_segment(table)}"
        r = self.request("GET", path, params=params or {})
        return r.json()

    def list_records_post(self, base_id: str, table: str, body: dict) -> dict:
        path = f"{base_id}/{_encode_table_segment(table)}/listRecords"
        r = self.request("POST", path, json=body)
        return r.json()

    def get_record(self, base_id: str, table: str, record_id: str) -> dict:
        path = f"{base_id}/{_encode_table_segment(table)}/{record_id}"
        r = self.request("GET", path)
        return r.json()

    def create_records(self, base_id: str, table: str, body: dict) -> dict:
        path = f"{base_id}/{_encode_table_segment(table)}"
        r = self.request("POST", path, json=body)
        return r.json()

    def update_records(self, base_id: str, table: str, body: dict) -> dict:
        path = f"{base_id}/{_encode_table_segment(table)}"
        r = self.request("PATCH", path, json=body)
        return r.json()

    def delete_records(self, base_id: str, table: str, record_ids: list[str]) -> dict:
        path = f"{base_id}/{_encode_table_segment(table)}"
        params = [("records[]", rid) for rid in record_ids]
        r = self.request("DELETE", path, params=params)
        return r.json()

    # --- metadata ---

    def list_bases(self) -> dict:
        r = self.request("GET", "meta/bases")
        return r.json()

    def get_base_schema(self, base_id: str) -> dict:
        r = self.request("GET", f"meta/bases/{base_id}/tables")
        return r.json()

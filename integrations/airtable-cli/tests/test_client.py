import httpx

from airtable_cli.client import AirtableClient


def test_list_records_encodes_table(monkeypatch) -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        raw = request.url.raw_path
        raw_s = raw.decode() if isinstance(raw, (bytes, bytearray)) else str(raw)
        captured["raw_path"] = raw_s
        assert request.headers.get("Authorization") == "Bearer tok"
        return httpx.Response(200, json={"records": []})

    transport = httpx.MockTransport(handler)
    client = AirtableClient("tok", transport=transport)
    client.list_records("appBASE", "My Table")
    client.close()
    raw_path = captured["raw_path"]
    assert "appBASE" in raw_path and "My%20Table" in raw_path


def test_delete_records_query_shape() -> None:
    pairs: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        pairs.extend([(k, v) for k, v in request.url.params.multi_items()])
        return httpx.Response(200, json={"records": [{"deleted": True}]})

    transport = httpx.MockTransport(handler)
    client = AirtableClient("tok", transport=transport)
    client.delete_records("appX", "Tbl", ["recA", "recB"])
    client.close()
    assert pairs.count(("records[]", "recA")) == 1
    assert pairs.count(("records[]", "recB")) == 1


def test_meta_bases_path() -> None:
    paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        return httpx.Response(200, json={"bases": []})

    transport = httpx.MockTransport(handler)
    client = AirtableClient("tok", transport=transport)
    client.list_bases()
    client.close()
    assert any(p.rstrip("/").endswith("/meta/bases") for p in paths)

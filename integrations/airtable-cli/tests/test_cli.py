import json

import httpx
from typer.testing import CliRunner

from airtable_cli.cli import app
from airtable_cli.client import AirtableClient


def test_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout


def test_list_requires_base(monkeypatch) -> None:
    monkeypatch.delenv("AIRTABLE_BASE_ID", raising=False)
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["list", "Tasks"],
        env={"AIRTABLE_TOKEN": "pat_x"},
    )
    assert result.exit_code == 2
    combined = (result.stderr + result.stdout).lower()
    assert "base" in combined


def test_list_success_with_mock_transport(monkeypatch) -> None:
    transport = httpx.MockTransport(
        lambda _req: httpx.Response(200, json={"records": [{"id": "rec1", "fields": {}}]}),
    )

    import airtable_cli.cli as cli

    tr = transport

    def factory(token: str, timeout: float = 30.0, transport=None):
        return AirtableClient(token, timeout=timeout, transport=tr)

    monkeypatch.setattr(cli, "AirtableClient", factory)

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["list", "Tasks", "--base", "appTEST"],
        env={"AIRTABLE_TOKEN": "pat_x"},
    )
    assert result.exit_code == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["records"][0]["id"] == "rec1"


def test_list_api_error_exit_code(monkeypatch) -> None:
    transport = httpx.MockTransport(
        lambda _req: httpx.Response(403, json={"error": {"message": "nope"}}),
    )

    import airtable_cli.cli as cli

    tr = transport

    def factory(token: str, timeout: float = 30.0, transport=None):
        return AirtableClient(token, timeout=timeout, transport=tr)

    monkeypatch.setattr(cli, "AirtableClient", factory)

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["list", "Tasks", "--base", "appTEST"],
        env={"AIRTABLE_TOKEN": "pat_x"},
    )
    assert result.exit_code == 1
    err = json.loads(result.stderr)
    assert "nope" in err["error"] or "nope" in json.dumps(err)

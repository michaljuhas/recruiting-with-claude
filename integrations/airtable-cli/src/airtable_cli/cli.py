from __future__ import annotations

import json
from typing import Annotated, Optional

import typer

from airtable_cli.auth import load_base_id, load_token
from airtable_cli.client import AirtableClient
from airtable_cli.errors import AirtableAPIError

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)


def _resolve_base(base: Optional[str]) -> str:
    resolved = (base or load_base_id() or "").strip()
    if not resolved:
        typer.echo("Missing base id: use --base or set AIRTABLE_BASE_ID", err=True)
        raise typer.Exit(code=2)
    return resolved


def _make_client(token: Optional[str]) -> AirtableClient:
    try:
        return AirtableClient(load_token(token))
    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc


def _emit_json(data: object) -> None:
    typer.echo(json.dumps(data, indent=2))


@app.command("list")
def cmd_list(
    table: str,
    base: Annotated[Optional[str], typer.Option("--base", envvar="AIRTABLE_BASE_ID")] = None,
    token: Annotated[Optional[str], typer.Option("--token", envvar="AIRTABLE_TOKEN")] = None,
    page_size: Annotated[Optional[int], typer.Option("--page-size")] = None,
    offset: Annotated[Optional[str], typer.Option("--offset")] = None,
    formula: Annotated[Optional[str], typer.Option("--formula", "-f")] = None,
) -> None:
    bid = _resolve_base(base)
    params: dict[str, str | int] = {}
    if page_size is not None:
        params["pageSize"] = page_size
    if offset:
        params["offset"] = offset
    if formula:
        params["filterByFormula"] = formula
    try:
        with _make_client(token) as client:
            data = client.list_records(bid, table, params=params or None)
        _emit_json(data)
    except AirtableAPIError as exc:
        typer.echo(json.dumps({"error": str(exc), "payload": exc.payload}, indent=2), err=True)
        raise typer.Exit(code=1) from exc


@app.command("get")
def cmd_get(
    table: str,
    record_id: str,
    base: Annotated[Optional[str], typer.Option("--base", envvar="AIRTABLE_BASE_ID")] = None,
    token: Annotated[Optional[str], typer.Option("--token", envvar="AIRTABLE_TOKEN")] = None,
) -> None:
    bid = _resolve_base(base)
    try:
        with _make_client(token) as client:
            data = client.get_record(bid, table, record_id)
        _emit_json(data)
    except AirtableAPIError as exc:
        typer.echo(json.dumps({"error": str(exc), "payload": exc.payload}, indent=2), err=True)
        raise typer.Exit(code=1) from exc


@app.command("describe")
def cmd_describe(
    base: Annotated[Optional[str], typer.Option("--base", envvar="AIRTABLE_BASE_ID")] = None,
    token: Annotated[Optional[str], typer.Option("--token", envvar="AIRTABLE_TOKEN")] = None,
) -> None:
    bid = _resolve_base(base)
    try:
        with _make_client(token) as client:
            data = client.get_base_schema(bid)
        _emit_json(data)
    except AirtableAPIError as exc:
        typer.echo(json.dumps({"error": str(exc), "payload": exc.payload}, indent=2), err=True)
        raise typer.Exit(code=1) from exc


@app.command("bases")
def cmd_bases(
    token: Annotated[Optional[str], typer.Option("--token", envvar="AIRTABLE_TOKEN")] = None,
) -> None:
    try:
        with _make_client(token) as client:
            data = client.list_bases()
        _emit_json(data)
    except AirtableAPIError as exc:
        typer.echo(json.dumps({"error": str(exc), "payload": exc.payload}, indent=2), err=True)
        raise typer.Exit(code=1) from exc


def main() -> None:
    app()


if __name__ == "__main__":
    main()

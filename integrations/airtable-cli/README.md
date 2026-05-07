# airtable-cli

Small CLI around the [Airtable Web API](https://airtable.com/developers/web/api/introduction).

## Setup

```bash
cd integrations/airtable-cli
pip install -e ".[dev]"
```

## Environment

- `AIRTABLE_TOKEN` — Personal Access Token (Bearer)
- `AIRTABLE_BASE_ID` — Default base id (`app…`), optional if you pass `--base`

## Usage

```bash
airtable-cli --help
airtable-cli list TABLE_NAME
airtable-cli get TABLE_NAME recXXXXXXXX
```

Responses are printed as JSON. Do not log or paste tokens.

# attio-mcp

An MCP server for [Attio](https://attio.com) — a modern CRM platform for managing contacts, companies, deals, and workflows. Built with the [dedalus_mcp](https://docs.dedaluslabs.ai/dmcp) framework. Authentication is handled by **DAuth** (Dedalus Auth).

## Features

- Full CRUD operations on **People**, **Companies**, and **Deals**
- Attribute discovery for any object or list
- Comment creation on records and list entries
- List management — add records to lists with entry-level attributes
- Filtering and sorting via Attio's query API
- Handles Attio's complex versioned attribute value structure

## Available Tools

| Tool | Description |
|------|-------------|
| `attio_list_people` | Query person records with optional filtering and sorting |
| `attio_get_person` | Get a single person record by ID |
| `attio_create_person` | Create a new person record |
| `attio_update_person` | Update an existing person record |
| `attio_list_companies` | Query company records with optional filtering and sorting |
| `attio_get_company` | Get a single company record by ID |
| `attio_create_company` | Create a new company record |
| `attio_update_company` | Update an existing company record |
| `attio_list_deals` | Query deal records with optional filtering and sorting |
| `attio_create_deal` | Create a new deal record |
| `attio_update_deal` | Update an existing deal record |
| `attio_list_attributes` | List all attributes for an object or list |
| `attio_create_comment` | Create a comment on a record or list entry |
| `attio_add_to_list` | Add a record to a list as a new entry |

## Setup

### 1. Install dependencies

```bash
pip install -e .
```

### 2. Configure environment variables

Copy and fill in the `.env` file:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `DEDALUS_AS_URL` | Dedalus authorization server URL (default: `https://as.dedaluslabs.ai`) |
| `DEDALUS_API_KEY` | Your Dedalus platform API key |
| `DEDALUS_API_URL` | Dedalus API URL (default: `https://api.dedaluslabs.ai`) |
| `ATTIO_API_TOKEN` | Your Attio API token — create one at **Settings → Developers → API Keys** in your Attio workspace |

#### Required Attio scopes

- `record_permission:read-write`
- `object_configuration:read`
- `list_configuration:read`
- `list_entry:read-write`
- `comment:read-write`

### 3. Test your connection

```bash
python -m src.client --test-connection
```

### 4. Run the server

```bash
python -m src.main
```

The server starts on port 8080. Test with:

```bash
python -m src.client
```

## Project Structure

```
attio-mcp/
├── src/
│   ├── main.py              # Server entrypoint
│   ├── server.py            # MCP server creation
│   ├── client.py            # Test client
│   ├── attio/
│   │   ├── config.py        # DAuth connection config
│   │   ├── request.py       # API dispatch + value extraction helpers
│   │   └── types.py         # Typed dataclasses for API responses
│   └── tools/
│       ├── __init__.py      # Tool registry
│       ├── people.py        # People CRUD tools
│       ├── companies.py     # Company CRUD tools
│       ├── deals.py         # Deal tools
│       ├── attributes.py    # Attribute listing
│       ├── comments.py      # Comment creation
│       └── lists.py         # List entry management
├── pyproject.toml
├── .env
└── README.md
```

## Deploy

Upload to [dedaluslabs.ai](https://dedaluslabs.ai). DAuth handles credential security automatically in production.

## Requirements

- **Python >= 3.10**
- **uv** (recommended) or **pip**

## Links

- [Attio API docs](https://docs.attio.com/)
- [Dedalus MCP docs](https://docs.dedaluslabs.ai/dmcp)
- [DAuth launch blog post](https://www.dedaluslabs.ai/blog/dedalus-auth-launch)

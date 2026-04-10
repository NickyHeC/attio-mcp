"""Company tools.

Tools:
  attio_list_companies   -- query company records with optional filtering/sorting
  attio_get_company      -- get a company by record ID
  attio_create_company   -- create a new company record
  attio_update_company   -- update an existing company record
"""

from __future__ import annotations

from typing import Any

from dedalus_mcp import HttpMethod, tool
from dedalus_mcp.types import ToolAnnotations

from src.attio.request import _domains, _opt_str, _text, api_request
from src.attio.types import AttioResult, CompanyInfo, JSONObject


# --- Helpers ---


def _parse_company(raw: JSONObject) -> CompanyInfo:
    """Parse a raw Attio company record into a CompanyInfo."""
    record_id = ""
    id_obj = raw.get("id")
    if isinstance(id_obj, dict):
        record_id = str(id_obj.get("record_id", ""))

    values = raw.get("values", {})
    if not isinstance(values, dict):
        values = {}

    return CompanyInfo(
        record_id=record_id,
        name=_text(values.get("name")),
        domains=_domains(values.get("domains")),
        description=_text(values.get("description")),
        web_url=_opt_str(raw.get("web_url")),
        created_at=_opt_str(raw.get("created_at")),
    )


# --- Tools ---


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def attio_list_companies(
    filter: JSONObject | None = None,
    sorts: list[JSONObject] | None = None,
    limit: int = 25,
    offset: int = 0,
) -> list[CompanyInfo] | str:
    """Query company records in Attio with optional filtering and sorting.

    The ``filter`` param accepts an Attio filter object, e.g.
    ``{"name": "Acme Corp"}`` or ``{"domains": "acme.com"}``.

    Args:
        filter: Attio filter object. Passed through as-is.
        sorts: List of sort specifications.
        limit: Maximum records to return (max 500).
        offset: Number of records to skip for pagination.

    Returns:
        List of CompanyInfo objects, or an error string on failure.

    """
    body: dict[str, Any] = {"limit": limit, "offset": offset}
    if filter:
        body["filter"] = filter
    if sorts:
        body["sorts"] = sorts

    result: AttioResult = await api_request(
        HttpMethod.POST, "/v2/objects/companies/records/query", body=body
    )
    if not result.success:
        return result.error or "Failed to list companies"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    records = data.get("data", [])
    if not isinstance(records, list):
        return "No records in response"
    return [_parse_company(r) for r in records if isinstance(r, dict)]


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def attio_get_company(record_id: str) -> CompanyInfo | str:
    """Get a single company record by its ID.

    Args:
        record_id: The UUID of the company record.

    Returns:
        CompanyInfo with full detail, or an error string on failure.

    """
    result: AttioResult = await api_request(
        HttpMethod.GET, f"/v2/objects/companies/records/{record_id}"
    )
    if not result.success:
        return result.error or "Failed to get company"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    record = data.get("data")
    if not isinstance(record, dict):
        return "Company not found"
    return _parse_company(record)


@tool(annotations=ToolAnnotations(readOnlyHint=False))
async def attio_create_company(
    name: str,
    domain: str | None = None,
    description: str | None = None,
) -> CompanyInfo | str:
    """Create a new company record in Attio.

    Will throw on conflicts of unique attributes like domains. Use the
    assert endpoint via the Attio UI for upsert behavior.

    Note: ``logo_url`` cannot be set via the API.

    Args:
        name: Company name.
        domain: Primary domain (e.g. ``acme.com``).
        description: Free-text description.

    Returns:
        Created CompanyInfo, or an error string on failure.

    """
    values: dict[str, Any] = {"name": name}
    if domain is not None:
        values["domains"] = [domain]
    if description is not None:
        values["description"] = description

    body = {"data": {"values": values}}
    result: AttioResult = await api_request(
        HttpMethod.POST, "/v2/objects/companies/records", body=body
    )
    if not result.success:
        return result.error or "Failed to create company"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    record = data.get("data")
    if not isinstance(record, dict):
        return "No record in response"
    return _parse_company(record)


@tool(annotations=ToolAnnotations(readOnlyHint=False))
async def attio_update_company(
    record_id: str,
    name: str | None = None,
    domain: str | None = None,
    description: str | None = None,
) -> CompanyInfo | str:
    """Update an existing company record.

    Only provided fields are modified; omitted fields are left unchanged.
    Note: ``logo_url`` cannot be updated via the API.

    Args:
        record_id: UUID of the company record to update.
        name: New company name.
        domain: Domain to add.
        description: New description.

    Returns:
        Updated CompanyInfo, or an error string on failure.

    """
    values: dict[str, Any] = {}
    if name is not None:
        values["name"] = name
    if domain is not None:
        values["domains"] = [domain]
    if description is not None:
        values["description"] = description

    if not values:
        return "No fields to update"

    body = {"data": {"values": values}}
    result: AttioResult = await api_request(
        HttpMethod.PATCH, f"/v2/objects/companies/records/{record_id}", body=body
    )
    if not result.success:
        return result.error or "Failed to update company"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    record = data.get("data")
    if not isinstance(record, dict):
        return "No record in response"
    return _parse_company(record)


company_tools = [
    attio_list_companies,
    attio_get_company,
    attio_create_company,
    attio_update_company,
]

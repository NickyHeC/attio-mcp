"""Deal tools.

Tools:
  attio_list_deals   -- query deal records with optional filtering/sorting
  attio_create_deal  -- create a new deal record
  attio_update_deal  -- update an existing deal record
"""

from __future__ import annotations

from typing import Any

from dedalus_mcp import HttpMethod, tool
from dedalus_mcp.types import ToolAnnotations

from src.attio.request import (
    _currency_code,
    _currency_value,
    _opt_str,
    _status_title,
    _text,
    api_request,
)
from src.attio.types import AttioResult, DealInfo, JSONObject


# --- Helpers ---


def _parse_deal(raw: JSONObject) -> DealInfo:
    """Parse a raw Attio deal record into a DealInfo."""
    record_id = ""
    id_obj = raw.get("id")
    if isinstance(id_obj, dict):
        record_id = str(id_obj.get("record_id", ""))

    values = raw.get("values", {})
    if not isinstance(values, dict):
        values = {}

    return DealInfo(
        record_id=record_id,
        name=_text(values.get("name")),
        stage=_status_title(values.get("stage")),
        value=_currency_value(values.get("value")),
        currency=_currency_code(values.get("value")),
        web_url=_opt_str(raw.get("web_url")),
        created_at=_opt_str(raw.get("created_at")),
    )


# --- Tools ---


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def attio_list_deals(
    filter: JSONObject | None = None,
    sorts: list[JSONObject] | None = None,
    limit: int = 25,
    offset: int = 0,
) -> list[DealInfo] | str:
    """Query deal records in Attio with optional filtering and sorting.

    The ``filter`` param accepts an Attio filter object, e.g.
    ``{"name": "Enterprise Contract"}``.

    Args:
        filter: Attio filter object. Passed through as-is.
        sorts: List of sort specifications.
        limit: Maximum records to return (max 500).
        offset: Number of records to skip for pagination.

    Returns:
        List of DealInfo objects, or an error string on failure.

    """
    body: dict[str, Any] = {"limit": limit, "offset": offset}
    if filter:
        body["filter"] = filter
    if sorts:
        body["sorts"] = sorts

    result: AttioResult = await api_request(
        HttpMethod.POST, "/v2/objects/deals/records/query", body=body
    )
    if not result.success:
        return result.error or "Failed to list deals"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    records = data.get("data", [])
    if not isinstance(records, list):
        return "No records in response"
    return [_parse_deal(r) for r in records if isinstance(r, dict)]


@tool(annotations=ToolAnnotations(readOnlyHint=False))
async def attio_create_deal(
    name: str,
    currency_value: float | None = None,
    currency_code: str = "USD",
) -> DealInfo | str:
    """Create a new deal record in Attio.

    Args:
        name: Deal name (e.g. ``"Contract with Acme"``).
        currency_value: Deal monetary value.
        currency_code: ISO currency code (default: ``USD``).

    Returns:
        Created DealInfo, or an error string on failure.

    """
    values: dict[str, Any] = {"name": name}
    if currency_value is not None:
        values["value"] = [
            {"currency_value": currency_value, "currency_code": currency_code}
        ]

    body = {"data": {"values": values}}
    result: AttioResult = await api_request(
        HttpMethod.POST, "/v2/objects/deals/records", body=body
    )
    if not result.success:
        return result.error or "Failed to create deal"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    record = data.get("data")
    if not isinstance(record, dict):
        return "No record in response"
    return _parse_deal(record)


@tool(annotations=ToolAnnotations(readOnlyHint=False))
async def attio_update_deal(
    record_id: str,
    name: str | None = None,
    currency_value: float | None = None,
    currency_code: str | None = None,
) -> DealInfo | str:
    """Update an existing deal record.

    Only provided fields are modified; omitted fields are left unchanged.

    Args:
        record_id: UUID of the deal record to update.
        name: New deal name.
        currency_value: New deal monetary value.
        currency_code: New ISO currency code.

    Returns:
        Updated DealInfo, or an error string on failure.

    """
    values: dict[str, Any] = {}
    if name is not None:
        values["name"] = name
    if currency_value is not None:
        code = currency_code or "USD"
        values["value"] = [
            {"currency_value": currency_value, "currency_code": code}
        ]

    if not values:
        return "No fields to update"

    body = {"data": {"values": values}}
    result: AttioResult = await api_request(
        HttpMethod.PATCH, f"/v2/objects/deals/records/{record_id}", body=body
    )
    if not result.success:
        return result.error or "Failed to update deal"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    record = data.get("data")
    if not isinstance(record, dict):
        return "No record in response"
    return _parse_deal(record)


deal_tools = [
    attio_list_deals,
    attio_create_deal,
    attio_update_deal,
]

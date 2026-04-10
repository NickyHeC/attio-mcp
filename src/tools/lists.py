"""List entry tools.

Tools:
  attio_add_to_list -- add a record to a list as a new entry
"""

from __future__ import annotations

from typing import Any

from dedalus_mcp import HttpMethod, tool
from dedalus_mcp.types import ToolAnnotations

from src.attio.request import _opt_str, api_request
from src.attio.types import AttioResult, JSONObject, ListEntryInfo


# --- Helpers ---


def _parse_entry(raw: JSONObject) -> ListEntryInfo:
    """Parse a raw Attio list entry response into a ListEntryInfo."""
    entry_id = ""
    list_id = ""
    id_obj = raw.get("id")
    if isinstance(id_obj, dict):
        entry_id = str(id_obj.get("entry_id", ""))
        list_id = str(id_obj.get("list_id", ""))

    entry_values = raw.get("entry_values", {})
    if not isinstance(entry_values, dict):
        entry_values = {}

    return ListEntryInfo(
        entry_id=entry_id,
        list_id=list_id,
        parent_record_id=str(raw.get("parent_record_id", "")),
        parent_object=_opt_str(raw.get("parent_object")),
        created_at=_opt_str(raw.get("created_at")),
        entry_values=entry_values,
    )


# --- Tools ---


@tool(annotations=ToolAnnotations(readOnlyHint=False))
async def attio_add_to_list(
    list_id: str,
    parent_record_id: str,
    entry_values: JSONObject | None = None,
) -> ListEntryInfo | str:
    """Add a record to a list as a new entry.

    Multiple entries are allowed for the same parent record.
    Entry-level attribute values (like status) can be set via
    ``entry_values``.

    Args:
        list_id: UUID of the list to add the record to.
        parent_record_id: UUID of the record to add.
        entry_values: Key-value pairs where the key is the attribute
            slug and the value is the attribute value. Optional.

    Returns:
        Created ListEntryInfo, or an error string on failure.

    """
    body: dict[str, Any] = {"parent_record_id": parent_record_id}
    if entry_values:
        body["entry_values"] = entry_values

    result: AttioResult = await api_request(
        HttpMethod.POST, f"/v2/lists/{list_id}/entries", body=body
    )
    if not result.success:
        return result.error or "Failed to add record to list"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    entry = data.get("data")
    if not isinstance(entry, dict):
        return "No entry in response"
    return _parse_entry(entry)


list_tools = [
    attio_add_to_list,
]

"""Attribute tools.

Tools:
  attio_list_attributes -- list all attributes for an object or list
"""

from __future__ import annotations

from dedalus_mcp import HttpMethod, tool
from dedalus_mcp.types import ToolAnnotations

from src.attio.request import _opt_str, api_request
from src.attio.types import AttioResult, AttributeInfo, JSONObject


# --- Helpers ---


def _parse_attribute(raw: JSONObject) -> AttributeInfo:
    """Parse a raw Attio attribute definition into an AttributeInfo."""
    attribute_id = ""
    id_obj = raw.get("id")
    if isinstance(id_obj, dict):
        attribute_id = str(id_obj.get("attribute_id", ""))

    return AttributeInfo(
        attribute_id=attribute_id,
        title=str(raw.get("title", "")),
        api_slug=str(raw.get("api_slug", "")),
        type=str(raw.get("type", "")),
        is_writable=bool(raw.get("is_writable", False)),
        is_required=bool(raw.get("is_required", False)),
        is_unique=bool(raw.get("is_unique", False)),
        is_archived=bool(raw.get("is_archived", False)),
        description=_opt_str(raw.get("description")),
    )


# --- Tools ---


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def attio_list_attributes(
    target: str = "objects",
    target_slug: str = "people",
) -> list[AttributeInfo] | str:
    """List all attributes defined on an Attio object or list.

    Returns attribute definitions including title, slug, type, and
    writability. Useful for discovering available fields before
    creating or updating records.

    Args:
        target: Either ``objects`` or ``lists``.
        target_slug: The slug of the object or list
            (e.g. ``people``, ``companies``, ``deals``).

    Returns:
        List of AttributeInfo objects, or an error string on failure.

    """
    if target == "lists":
        path = f"/v2/lists/{target_slug}/attributes"
    else:
        path = f"/v2/objects/{target_slug}/attributes"

    result: AttioResult = await api_request(HttpMethod.GET, path)
    if not result.success:
        return result.error or "Failed to list attributes"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    attributes = data.get("data", [])
    if not isinstance(attributes, list):
        return "No attributes in response"
    return [_parse_attribute(a) for a in attributes if isinstance(a, dict)]


attribute_tools = [
    attio_list_attributes,
]

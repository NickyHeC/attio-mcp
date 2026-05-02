"""People tools.

Tools:
  attio_list_people    -- query person records with optional filtering/sorting
  attio_get_person     -- get a person by record ID
  attio_create_person  -- create a new person record
  attio_update_person  -- update an existing person record
"""

from __future__ import annotations

from typing import Any

from dedalus_mcp import HttpMethod, tool
from dedalus_mcp.types import ToolAnnotations

from src.attio.request import (
    _emails,
    _interaction,
    _location,
    _name_field,
    _opt_str,
    _option_title,
    _phones,
    _record_ref,
    _text,
    api_request,
)
from src.attio.types import AttioResult, JSONObject, PersonInfo


# --- Helpers ---


def _parse_person(raw: JSONObject) -> PersonInfo:
    """Parse a raw Attio person record into a PersonInfo."""
    record_id = ""
    id_obj = raw.get("id")
    if isinstance(id_obj, dict):
        record_id = str(id_obj.get("record_id", ""))

    values = raw.get("values", {})
    if not isinstance(values, dict):
        values = {}

    return PersonInfo(
        record_id=record_id,
        full_name=_name_field(values.get("name"), "full_name"),
        first_name=_name_field(values.get("name"), "first_name"),
        last_name=_name_field(values.get("name"), "last_name"),
        email_addresses=_emails(values.get("email_addresses")),
        phone_numbers=_phones(values.get("phone_numbers")),
        job_title=_text(values.get("job_title")),
        company_id=_record_ref(values.get("company")),
        description=_text(values.get("description")),
        connection_strength=_option_title(values.get("strongest_connection_strength")),
        last_interaction=_interaction(values.get("last_interaction")),
        last_email_interaction=_interaction(values.get("last_email_interaction")),
        last_meeting_interaction=_interaction(values.get("last_meeting_interaction")),
        first_interaction=_interaction(values.get("first_interaction")),
        linkedin=_text(values.get("linkedin")),
        location=_location(values.get("primary_location")),
        web_url=_opt_str(raw.get("web_url")),
        created_at=_opt_str(raw.get("created_at")),
    )


# --- Tools ---


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def attio_list_people(
    filter: JSONObject | None = None,
    sorts: list[JSONObject] | None = None,
    limit: int = 25,
    offset: int = 0,
) -> list[PersonInfo] | str:
    """Query person records in Attio with optional filtering and sorting.

    The ``filter`` param accepts an Attio filter object, e.g.
    ``{"email_addresses": "alice@example.com"}`` or
    ``{"name": "Alice Smith"}``.

    The ``sorts`` param accepts a list of sort objects, e.g.
    ``[{"direction": "asc", "attribute": "name", "field": "last_name"}]``.

    Args:
        filter: Attio filter object. Passed through as-is.
        sorts: List of sort specifications.
        limit: Maximum records to return (max 500).
        offset: Number of records to skip for pagination.

    Returns:
        List of PersonInfo objects, or an error string on failure.

    """
    body: dict[str, Any] = {"limit": limit, "offset": offset}
    if filter:
        body["filter"] = filter
    if sorts:
        body["sorts"] = sorts

    result: AttioResult = await api_request(
        HttpMethod.POST, "/v2/objects/people/records/query", body=body
    )
    if not result.success:
        return result.error or "Failed to list people"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    records = data.get("data", [])
    if not isinstance(records, list):
        return "No records in response"
    return [_parse_person(r) for r in records if isinstance(r, dict)]


@tool(annotations=ToolAnnotations(readOnlyHint=True))
async def attio_get_person(record_id: str) -> PersonInfo | str:
    """Get a single person record by its ID.

    Args:
        record_id: The UUID of the person record.

    Returns:
        PersonInfo with full detail, or an error string on failure.

    """
    result: AttioResult = await api_request(
        HttpMethod.GET, f"/v2/objects/people/records/{record_id}"
    )
    if not result.success:
        return result.error or "Failed to get person"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    record = data.get("data")
    if not isinstance(record, dict):
        return "Person not found"
    return _parse_person(record)


@tool(annotations=ToolAnnotations(readOnlyHint=False))
async def attio_create_person(
    first_name: str | None = None,
    last_name: str | None = None,
    email_address: str | None = None,
    phone_number: str | None = None,
    job_title: str | None = None,
    description: str | None = None,
) -> PersonInfo | str:
    """Create a new person record in Attio.

    At least one identifying field (name or email) should be provided.
    Will throw on conflicts of unique attributes like email. Use the
    assert endpoint via the Attio UI for upsert behavior.

    Args:
        first_name: Person's first name.
        last_name: Person's last name.
        email_address: Primary email address.
        phone_number: Phone number (e.g. ``+15558675309``).
        job_title: Job title.
        description: Free-text description.

    Returns:
        Created PersonInfo, or an error string on failure.

    """
    values: dict[str, Any] = {}
    if first_name is not None or last_name is not None:
        name: dict[str, str] = {}
        if first_name is not None:
            name["first_name"] = first_name
        if last_name is not None:
            name["last_name"] = last_name
        values["name"] = [name]
    if email_address is not None:
        values["email_addresses"] = [email_address]
    if phone_number is not None:
        values["phone_numbers"] = [phone_number]
    if job_title is not None:
        values["job_title"] = job_title
    if description is not None:
        values["description"] = description

    body = {"data": {"values": values}}
    result: AttioResult = await api_request(
        HttpMethod.POST, "/v2/objects/people/records", body=body
    )
    if not result.success:
        return result.error or "Failed to create person"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    record = data.get("data")
    if not isinstance(record, dict):
        return "No record in response"
    return _parse_person(record)


@tool(annotations=ToolAnnotations(readOnlyHint=False))
async def attio_update_person(
    record_id: str,
    first_name: str | None = None,
    last_name: str | None = None,
    email_address: str | None = None,
    phone_number: str | None = None,
    job_title: str | None = None,
    description: str | None = None,
) -> PersonInfo | str:
    """Update an existing person record.

    Only provided fields are modified; omitted fields are left unchanged.
    Note: ``avatar_url`` cannot be updated via the API.

    Args:
        record_id: UUID of the person record to update.
        first_name: New first name.
        last_name: New last name.
        email_address: Email address to add.
        phone_number: Phone number to add.
        job_title: New job title.
        description: New description.

    Returns:
        Updated PersonInfo, or an error string on failure.

    """
    values: dict[str, Any] = {}
    if first_name is not None or last_name is not None:
        name: dict[str, str] = {}
        if first_name is not None:
            name["first_name"] = first_name
        if last_name is not None:
            name["last_name"] = last_name
        values["name"] = [name]
    if email_address is not None:
        values["email_addresses"] = [email_address]
    if phone_number is not None:
        values["phone_numbers"] = [phone_number]
    if job_title is not None:
        values["job_title"] = job_title
    if description is not None:
        values["description"] = description

    if not values:
        return "No fields to update"

    body = {"data": {"values": values}}
    result: AttioResult = await api_request(
        HttpMethod.PATCH, f"/v2/objects/people/records/{record_id}", body=body
    )
    if not result.success:
        return result.error or "Failed to update person"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    record = data.get("data")
    if not isinstance(record, dict):
        return "No record in response"
    return _parse_person(record)


people_tools = [
    attio_list_people,
    attio_get_person,
    attio_create_person,
    attio_update_person,
]

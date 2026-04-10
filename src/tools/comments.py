"""Comment tools.

Tools:
  attio_create_comment -- create a comment on a record or list entry
"""

from __future__ import annotations

from typing import Any

from dedalus_mcp import HttpMethod, tool
from dedalus_mcp.types import ToolAnnotations

from src.attio.request import _opt_str, api_request
from src.attio.types import AttioResult, CommentInfo, JSONObject


# --- Helpers ---


def _parse_comment(raw: JSONObject) -> CommentInfo:
    """Parse a raw Attio comment response into a CommentInfo."""
    comment_id = ""
    id_obj = raw.get("id")
    if isinstance(id_obj, dict):
        comment_id = str(id_obj.get("comment_id", ""))

    author_id = None
    author = raw.get("author")
    if isinstance(author, dict):
        author_id = _opt_str(author.get("id"))

    return CommentInfo(
        comment_id=comment_id,
        thread_id=str(raw.get("thread_id", "")),
        content=str(raw.get("content_plaintext", "")),
        author_id=author_id,
        created_at=_opt_str(raw.get("created_at")),
    )


# --- Tools ---


@tool(annotations=ToolAnnotations(readOnlyHint=False))
async def attio_create_comment(
    content: str,
    thread_id: str | None = None,
    record_id: str | None = None,
    object_id: str | None = None,
    entry_id: str | None = None,
    list_id: str | None = None,
) -> CommentInfo | str:
    """Create a comment on a record or list entry in Attio.

    Link the comment to a record by providing ``record_id`` and
    ``object_id``, or to a list entry by providing ``entry_id``
    and ``list_id``.  A ``thread_id`` groups comments into a
    conversation; if omitted, a new thread is created.

    Args:
        content: Plaintext comment body (max 10,000 characters).
        thread_id: UUID of an existing comment thread. Optional.
        record_id: UUID of the record to comment on.
        object_id: UUID of the object the record belongs to.
        entry_id: UUID of the list entry to comment on.
        list_id: UUID of the list the entry belongs to.

    Returns:
        Created CommentInfo, or an error string on failure.

    """
    body: dict[str, Any] = {"content_plaintext": content}

    if thread_id is not None:
        body["thread_id"] = thread_id
    if record_id is not None and object_id is not None:
        body["record"] = {"record_id": record_id, "object_id": object_id}
    if entry_id is not None and list_id is not None:
        body["entry"] = {"entry_id": entry_id, "list_id": list_id}

    result: AttioResult = await api_request(
        HttpMethod.POST, "/v2/comments", body=body
    )
    if not result.success:
        return result.error or "Failed to create comment"
    data = result.data
    if not isinstance(data, dict):
        return "Unexpected response"
    comment = data.get("data")
    if not isinstance(comment, dict):
        return "No comment in response"
    return _parse_comment(comment)


comment_tools = [
    attio_create_comment,
]

"""Attio REST API request dispatch and response helpers.

Attio uses a standard REST API with JSON request/response bodies.
All authenticated requests go through the DAuth enclave.

Functions:
  api_request(method, path, body, params)  -- dispatch REST request via enclave

Value extraction helpers (unwrap Attio's versioned attribute arrays):
  _first_val(values_list)          -- first element of an attribute value array
  _text(values_list)               -- extract text value
  _name_field(values_list, field)  -- extract personal-name field
  _emails(values_list)             -- extract list of email addresses
  _phones(values_list)             -- extract list of phone numbers
  _domains(values_list)            -- extract list of domains
  _currency_value(values_list)     -- extract currency amount
  _currency_code(values_list)      -- extract currency code
  _status_title(values_list)       -- extract status title
  _record_ref(values_list)         -- extract referenced record ID
  _opt_str(val)                    -- coerce to str | None
"""

from __future__ import annotations

from typing import Any

from dedalus_mcp import HttpMethod, HttpRequest, get_context

from src.attio.config import attio
from src.attio.types import AttioResult


# --- REST dispatch ---


async def api_request(
    method: HttpMethod,
    path: str,
    body: dict[str, Any] | None = None,
    params: dict[str, str] | None = None,
) -> AttioResult:
    """Execute an Attio REST API request via the DAuth enclave.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, PATCH).
        path: API path appended to ``https://api.attio.com``
            (e.g. ``/v2/objects/people/records``).
        body: Optional JSON body for POST/PUT/PATCH requests.
        params: Optional query parameters appended to the URL.

    Returns:
        AttioResult wrapping the response data or error.

    """
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        path = f"{path}?{query}"

    ctx = get_context()
    req = HttpRequest(method=method, path=path, body=body)
    resp = await ctx.dispatch(attio, req)

    if resp.success and resp.response is not None:
        resp_body = resp.response.body
        if isinstance(resp_body, dict):
            errors = resp_body.get("errors")
            if errors and isinstance(errors, list):
                msg = (
                    errors[0].get("message", "API error")
                    if isinstance(errors[0], dict)
                    else "API error"
                )
                return AttioResult(success=False, error=str(msg))
        return AttioResult(success=True, data=resp_body)

    error = resp.error.message if resp.error else "Request failed"
    return AttioResult(success=False, error=error)


# --- Value extraction helpers ---
# Attio wraps every attribute value in an array of versioned entries.
# These helpers safely unwrap the first (active) value.


def _first_val(values_list: Any) -> dict[str, Any] | None:  # noqa: ANN401
    """Return the first element of an attribute value array, or None."""
    if isinstance(values_list, list) and values_list:
        v = values_list[0]
        if isinstance(v, dict):
            return v
    return None


def _text(values_list: Any) -> str | None:  # noqa: ANN401
    """Extract a plain text ``value`` from an attribute array."""
    v = _first_val(values_list)
    return str(v["value"]) if v and "value" in v else None


def _name_field(values_list: Any, field: str) -> str | None:  # noqa: ANN401
    """Extract a personal-name field (``first_name``, ``last_name``, ``full_name``)."""
    v = _first_val(values_list)
    return str(v[field]) if v and field in v else None


def _emails(values_list: Any) -> list[str]:  # noqa: ANN401
    """Extract all email addresses from an email attribute array."""
    if not isinstance(values_list, list):
        return []
    return [
        str(v["email_address"])
        for v in values_list
        if isinstance(v, dict) and v.get("email_address")
    ]


def _phones(values_list: Any) -> list[str]:  # noqa: ANN401
    """Extract all phone numbers from a phone attribute array."""
    if not isinstance(values_list, list):
        return []
    return [
        str(v["phone_number"])
        for v in values_list
        if isinstance(v, dict) and v.get("phone_number")
    ]


def _domains(values_list: Any) -> list[str]:  # noqa: ANN401
    """Extract all domains from a domain attribute array."""
    if not isinstance(values_list, list):
        return []
    return [
        str(v["domain"])
        for v in values_list
        if isinstance(v, dict) and v.get("domain")
    ]


def _currency_value(values_list: Any) -> float | None:  # noqa: ANN401
    """Extract currency amount from a currency attribute array."""
    v = _first_val(values_list)
    if v and "currency_value" in v:
        try:
            return float(v["currency_value"])
        except (TypeError, ValueError):
            return None
    return None


def _currency_code(values_list: Any) -> str | None:  # noqa: ANN401
    """Extract currency code from a currency attribute array."""
    v = _first_val(values_list)
    return str(v["currency_code"]) if v and "currency_code" in v else None


def _status_title(values_list: Any) -> str | None:  # noqa: ANN401
    """Extract the status title from a status attribute array."""
    v = _first_val(values_list)
    if v and isinstance(v.get("status"), dict):
        return str(v["status"].get("title", ""))
    return None


def _record_ref(values_list: Any) -> str | None:  # noqa: ANN401
    """Extract the target_record_id from a record-reference attribute array."""
    v = _first_val(values_list)
    return str(v["target_record_id"]) if v and "target_record_id" in v else None


def _option_title(values_list: Any) -> str | None:  # noqa: ANN401
    """Extract the option title from a select/option attribute array."""
    v = _first_val(values_list)
    if v and isinstance(v.get("option"), dict):
        return str(v["option"].get("title", ""))
    return None


def _interaction(values_list: Any) -> str | None:  # noqa: ANN401
    """Extract an interaction timestamp as ISO string from an interaction attribute."""
    v = _first_val(values_list)
    return str(v["interacted_at"]) if v and "interacted_at" in v else None


def _location(values_list: Any) -> str | None:  # noqa: ANN401
    """Extract a human-readable location string from an address attribute."""
    v = _first_val(values_list)
    if not v:
        return None
    parts = [v.get(k) for k in ("locality", "region", "country_code") if v.get(k)]
    return ", ".join(parts) if parts else None


def _opt_str(val: Any) -> str | None:  # noqa: ANN401
    """Safely coerce to optional string."""
    return str(val) if val is not None else None

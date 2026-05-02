"""Typed models for Attio API responses.

Result types (frozen dataclasses):
  AttioResult      -- raw API result wrapper
  RecordInfo       -- generic record summary
  PersonInfo       -- person record with extracted fields
  CompanyInfo      -- company record with extracted fields
  DealInfo         -- deal record with extracted fields
  AttributeInfo    -- attribute definition
  CommentInfo      -- comment on a record or entry
  ListEntryInfo    -- list entry summary

Type aliases:
  JSONPrimitive    -- scalar JSON values
  JSONValue        -- recursive JSON value
  JSONObject       -- dict[str, JSONValue]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAlias


# --- JSON types ---

JSONPrimitive: TypeAlias = str | int | float | bool | None

JSONValue: TypeAlias = str | int | float | bool | dict[str, Any] | list[Any] | None

JSONObject: TypeAlias = dict[str, JSONValue]


# --- Generic result ---


@dataclass(frozen=True, slots=True)
class AttioResult:
    """Raw Attio API result wrapper."""

    # fmt: off
    success: bool
    data:    JSONValue | None = None
    error:   str | None       = None
    # fmt: on


# --- Records ---


@dataclass(frozen=True, slots=True)
class RecordInfo:
    """Generic record summary with raw values."""

    # fmt: off
    record_id:  str
    object_id:  str
    web_url:    str | None = None
    created_at: str | None = None
    values:     dict[str, Any] = field(default_factory=dict)
    # fmt: on


@dataclass(frozen=True, slots=True)
class PersonInfo:
    """Person record with extracted key fields."""

    # fmt: off
    record_id:                str
    full_name:                str | None       = None
    first_name:               str | None       = None
    last_name:                str | None       = None
    email_addresses:          list[str]        = field(default_factory=list)
    phone_numbers:            list[str]        = field(default_factory=list)
    job_title:                str | None       = None
    company_id:               str | None       = None
    description:              str | None       = None
    connection_strength:      str | None       = None
    last_interaction:         str | None       = None
    last_email_interaction:   str | None       = None
    last_meeting_interaction: str | None       = None
    first_interaction:        str | None       = None
    linkedin:                 str | None       = None
    location:                 str | None       = None
    web_url:                  str | None       = None
    created_at:               str | None       = None
    # fmt: on


@dataclass(frozen=True, slots=True)
class CompanyInfo:
    """Company record with extracted key fields."""

    # fmt: off
    record_id:                str
    name:                     str | None       = None
    domains:                  list[str]        = field(default_factory=list)
    description:              str | None       = None
    connection_strength:      str | None       = None
    last_interaction:         str | None       = None
    last_email_interaction:   str | None       = None
    last_meeting_interaction: str | None       = None
    first_interaction:        str | None       = None
    employee_range:           str | None       = None
    location:                 str | None       = None
    category:                 str | None       = None
    linkedin:                 str | None       = None
    twitter:                  str | None       = None
    foundation_date:          str | None       = None
    web_url:                  str | None       = None
    created_at:               str | None       = None
    # fmt: on


@dataclass(frozen=True, slots=True)
class DealInfo:
    """Deal record with extracted key fields."""

    # fmt: off
    record_id:  str
    name:       str | None = None
    stage:      str | None = None
    value:      float | None = None
    currency:   str | None = None
    web_url:    str | None = None
    created_at: str | None = None
    # fmt: on


# --- Attributes ---


@dataclass(frozen=True, slots=True)
class AttributeInfo:
    """Attribute definition on an object or list."""

    # fmt: off
    attribute_id: str
    title:        str
    api_slug:     str
    type:         str
    is_writable:  bool  = False
    is_required:  bool  = False
    is_unique:    bool  = False
    is_archived:  bool  = False
    description:  str | None = None
    # fmt: on


# --- Comments ---


@dataclass(frozen=True, slots=True)
class CommentInfo:
    """Comment on a record or list entry."""

    # fmt: off
    comment_id: str
    thread_id:  str
    content:    str
    author_id:  str | None = None
    created_at: str | None = None
    # fmt: on


# --- List entries ---


@dataclass(frozen=True, slots=True)
class ListEntryInfo:
    """List entry summary."""

    # fmt: off
    entry_id:         str
    list_id:          str
    parent_record_id: str
    parent_object:    str | None        = None
    created_at:       str | None        = None
    entry_values:     dict[str, Any]    = field(default_factory=dict)
    # fmt: on

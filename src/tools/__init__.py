"""Tool registry for attio-mcp.

Modules:
  people     -- attio_list_people, attio_get_person, attio_create_person, attio_update_person
  companies  -- attio_list_companies, attio_get_company, attio_create_company, attio_update_company
  deals      -- attio_list_deals, attio_create_deal, attio_update_deal
  attributes -- attio_list_attributes
  comments   -- attio_create_comment
  lists      -- attio_add_to_list
"""

from __future__ import annotations

from src.tools.attributes import attribute_tools
from src.tools.comments import comment_tools
from src.tools.companies import company_tools
from src.tools.deals import deal_tools
from src.tools.lists import list_tools
from src.tools.people import people_tools


attio_tools = [
    *people_tools,
    *company_tools,
    *deal_tools,
    *attribute_tools,
    *comment_tools,
    *list_tools,
]

"""Attio connection configuration.

Evaluated at import time, after ``load_dotenv()`` in ``main.py``
has already injected the .env file.

Attio uses Bearer token (API Key) authentication.
DAuth encrypts the credential client-side and executes API calls
inside a sealed enclave.

Objects:
  attio -- Connection with Bearer token auth
"""

from __future__ import annotations

from dedalus_mcp.auth import Connection, SecretKeys


attio = Connection(
    name="attio-mcp",
    secrets=SecretKeys(token="ATTIO_API_TOKEN"),  # noqa: S106
    base_url="https://api.attio.com",
    auth_header_format="Bearer {api_key}",
)

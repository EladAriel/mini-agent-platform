"""Integration tests for /api/v1/tools."""

import pytest

from tests.conftest import ALPHA, BAD, BETA

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TOOLS_URL  = "/api/v1/tools"
AGENTS_URL = "/api/v1/agents"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def create_tool(client, *, name="web-search", desc="Searches the web", headers=ALPHA):
    """POST a tool and return the full response object."""
    return await client.post(
        TOOLS_URL,
        json={"name": name, "description": desc},
        headers=headers,
    )


async def tool_id(client, **kwargs) -> str:
    """Create a tool and return its id string."""
    return (await create_tool(client, **kwargs)).json()["id"]


async def create_agent(client, *, name, tool_ids, headers=ALPHA):
    """POST an agent and return the response body dict."""
    r = await client.post(
        AGENTS_URL,
        json={
            "name": name,
            "role": "Assistant",
            "description": "Test agent.",
            "tool_ids": tool_ids,
        },
        headers=headers,
    )
    assert r.status_code == 201
    return r.json()


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class TestAuth:

    async def test_missing_key_returns_401(self, client):
        r = await client.get(TOOLS_URL)
        assert r.status_code == 401

    async def test_invalid_key_returns_401(self, client):
        r = await client.get(TOOLS_URL, headers=BAD)
        assert r.status_code == 401

    async def test_valid_key_returns_200(self, client):
        r = await client.get(TOOLS_URL, headers=ALPHA)
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Tool CRUD
# ---------------------------------------------------------------------------

class TestToolCRUD:

    # ── Create ────────────────────────────────────────────────────────────────

    async def test_create_returns_201_with_body(self, client):
        r = await create_tool(client, name="web-search")
        assert r.status_code == 201
        body = r.json()
        assert body["name"] == "web-search"
        assert "id" in body
        assert "created_at" in body
        assert "updated_at" in body

    async def test_create_empty_name_returns_422(self, client):
        r = await client.post(
            TOOLS_URL,
            json={"name": "", "description": "d"},
            headers=ALPHA,
        )
        assert r.status_code == 422

    async def test_create_missing_description_returns_422(self, client):
        r = await client.post(TOOLS_URL, json={"name": "x"}, headers=ALPHA)
        assert r.status_code == 422

    # ── List ──────────────────────────────────────────────────────────────────

    async def test_list_empty_by_default(self, client):
        r = await client.get(TOOLS_URL, headers=ALPHA)
        assert r.status_code == 200
        assert r.json() == []

    async def test_list_returns_all_own_tools(self, client):
        await create_tool(client, name="tool-a")
        await create_tool(client, name="tool-b")
        r = await client.get(TOOLS_URL, headers=ALPHA)
        assert r.status_code == 200
        assert len(r.json()) == 2

    # ── Get ───────────────────────────────────────────────────────────────────

    async def test_get_returns_correct_tool(self, client):
        tid = await tool_id(client, name="web-search")
        r = await client.get(f"{TOOLS_URL}/{tid}", headers=ALPHA)
        assert r.status_code == 200
        assert r.json()["id"] == tid

    async def test_get_nonexistent_returns_404(self, client):
        r = await client.get(f"{TOOLS_URL}/000000000000000000000000", headers=ALPHA)
        assert r.status_code == 404

    async def test_get_malformed_id_returns_404(self, client):
        r = await client.get(f"{TOOLS_URL}/not-an-object-id", headers=ALPHA)
        assert r.status_code == 404

    # ── Update ────────────────────────────────────────────────────────────────

    async def test_update_description(self, client):
        tid = await tool_id(client)
        r = await client.patch(
            f"{TOOLS_URL}/{tid}",
            json={"description": "Updated desc"},
            headers=ALPHA,
        )
        assert r.status_code == 200
        assert r.json()["description"] == "Updated desc"

    async def test_update_does_not_touch_omitted_fields(self, client):
        tid = await tool_id(client, name="original-name")
        r = await client.patch(
            f"{TOOLS_URL}/{tid}",
            json={"description": "new desc"},
            headers=ALPHA,
        )
        assert r.json()["name"] == "original-name"

    async def test_update_nonexistent_returns_404(self, client):
        r = await client.patch(
            f"{TOOLS_URL}/000000000000000000000000",
            json={"description": "x"},
            headers=ALPHA,
        )
        assert r.status_code == 404

    # ── Delete ────────────────────────────────────────────────────────────────

    async def test_delete_returns_204(self, client):
        tid = await tool_id(client)
        r = await client.delete(f"{TOOLS_URL}/{tid}", headers=ALPHA)
        assert r.status_code == 204

    async def test_delete_makes_tool_unfetchable(self, client):
        tid = await tool_id(client)
        await client.delete(f"{TOOLS_URL}/{tid}", headers=ALPHA)
        r = await client.get(f"{TOOLS_URL}/{tid}", headers=ALPHA)
        assert r.status_code == 404

    async def test_delete_nonexistent_returns_404(self, client):
        r = await client.delete(
            f"{TOOLS_URL}/000000000000000000000000", headers=ALPHA
        )
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# agent_name filter
# ---------------------------------------------------------------------------

class TestToolListAgentNameFilter:
    """
    list_tools() takes a completely different code branch when agent_name is
    supplied: agents are queried first, their tool refs are extracted, then a
    second query fetches those tools.  None of the CRUD tests above touch
    this path.
    """

    async def test_filter_returns_tools_of_matching_agent(self, client):
        """Tools linked to a matching agent are returned; unlinked tools are not."""
        tid_linked   = await tool_id(client, name="linked-tool",   desc="d")
        tid_unlinked = await tool_id(client, name="unlinked-tool", desc="d")

        await create_agent(client, name="Research Bot", tool_ids=[tid_linked])

        r = await client.get(TOOLS_URL, headers=ALPHA, params={"agent_name": "Research"})
        assert r.status_code == 200
        returned_ids = {t["id"] for t in r.json()}
        assert tid_linked   in returned_ids
        assert tid_unlinked not in returned_ids

    async def test_filter_is_case_insensitive(self, client):
        tid = await tool_id(client, name="t", desc="d")
        await create_agent(client, name="Research Bot", tool_ids=[tid])

        r = await client.get(TOOLS_URL, headers=ALPHA, params={"agent_name": "research"})
        assert {t["id"] for t in r.json()} == {tid}

    async def test_filter_no_matching_agent_returns_empty(self, client):
        tid = await tool_id(client, name="t", desc="d")
        await create_agent(client, name="Research Bot", tool_ids=[tid])

        r = await client.get(
            TOOLS_URL, headers=ALPHA, params={"agent_name": "nonexistent-xyz"}
        )
        assert r.json() == []

    async def test_filter_agent_with_no_tools_returns_empty(self, client):
        await create_agent(client, name="Empty Agent", tool_ids=[])

        r = await client.get(TOOLS_URL, headers=ALPHA, params={"agent_name": "Empty"})
        assert r.json() == []

    async def test_filter_scoped_to_tenant(self, client):
        """BETA's agent with the same name must not expose ALPHA's tools."""
        alpha_tid = await tool_id(client, name="alpha-tool", headers=ALPHA)
        await create_agent(
            client, name="Shared Name Agent", tool_ids=[alpha_tid], headers=ALPHA
        )
        # BETA has an agent with the same name but no tools
        await create_agent(
            client, name="Shared Name Agent", tool_ids=[], headers=BETA
        )

        r = await client.get(
            TOOLS_URL, headers=BETA, params={"agent_name": "Shared Name"}
        )
        assert r.json() == []


# ---------------------------------------------------------------------------
# Tenant isolation
# ---------------------------------------------------------------------------

class TestTenantIsolation:

    async def test_tool_invisible_to_other_tenant(self, client):
        """A tool created by ALPHA must not be visible to BETA."""
        tid = await tool_id(client, name="alpha-only", headers=ALPHA)
        r = await client.get(f"{TOOLS_URL}/{tid}", headers=BETA)
        assert r.status_code == 404

    async def test_list_returns_only_own_tools(self, client):
        """BETA's list must be empty even when ALPHA has tools."""
        await create_tool(client, name="alpha-tool", headers=ALPHA)
        r = await client.get(TOOLS_URL, headers=BETA)
        assert r.json() == []

    async def test_beta_cannot_update_alpha_tool(self, client):
        tid = await tool_id(client, headers=ALPHA)
        r = await client.patch(
            f"{TOOLS_URL}/{tid}",
            json={"description": "hijacked"},
            headers=BETA,
        )
        assert r.status_code == 404

    async def test_beta_cannot_delete_alpha_tool(self, client):
        tid = await tool_id(client, headers=ALPHA)
        r = await client.delete(f"{TOOLS_URL}/{tid}", headers=BETA)
        assert r.status_code == 404
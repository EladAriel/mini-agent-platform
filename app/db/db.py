"""
Beanie ODM database layer.

Design
------
1. Beanie manages the active connection internally after initialization.
2. `init_db(client=...)` accepts an optional external client for test injection.
3. Database queries will be performed directly on the Beanie Document models 
   (e.g., `Agent.find()`).

Index creation
--------------
Indexes are defined inside the Document models themselves. 
Beanie automatically creates them during `init_beanie`.
"""

from pymongo import AsyncMongoClient
from beanie import init_beanie

from app.core.config import settings

from app.models.tool import Tool
from app.models.agent import Agent
from app.models.run import AgentRun

# We keep track of the client so we can close it on shutdown
_client: AsyncMongoClient | None = None

async def init_db(client: AsyncMongoClient | None = None) -> None:
    """
    Initialize the PyMongo async connection and Beanie ODM.

    Pass *client* to inject a test double.
    When *client* is None the production URI from settings is used.
    """
    global _client

    if _client is not None:
        return

    _client = client or AsyncMongoClient(settings.MONGODB_URI)
    db = _client[settings.MONGODB_DB]

    await init_beanie(
        database=db,
        document_models=[
            Tool,
            Agent,
            AgentRun
        ],
    )

async def close_db() -> None:
    """
    Close the connection (called from FastAPI lifespan on shutdown).
    """
    global _client
    if _client is not None:
        await _client.close()
        _client = None
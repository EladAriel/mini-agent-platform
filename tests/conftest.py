"""
Pytest fixtures using a real MongoDB container via testcontainers.

Strategy
--------
- A single MongoDbContainer is started ONCE per test session (session scope).
  This avoids the ~3-5 second Docker startup cost on every test.
- Before each test, all collections are dropped so every test starts with a
  clean, isolated database -- equivalent to the old mongomock approach.
- Beanie is re-initialised before each test against the now-empty database.

Requirements
------------
    pip install "testcontainers[mongodb]"

Docker must be running on the host machine. The container image is pulled
automatically on first run (mongo:6 is ~200 MB).

Why not mongomock-motor?
------------------------
Beanie 2.x dropped support for the `motor` driver entirely in favor of 
PyMongo's native AsyncMongoClient (introduced in PyMongo 4.16). 
Because mongomock-motor mimics the older Motor driver, it is incompatible 
with Beanie 2.x's internal aggregation pipelines (e.g., `fetch_links=True`), 
causing `TypeError: object AsyncIOMotorLatentCommandCursor cannot be used in await`.

Testcontainers spins up a real MongoDB process so the native PyMongo async 
driver and all Beanie features work flawlessly.
"""

import pytest
import pytest_asyncio
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient
from pymongo import AsyncMongoClient
from testcontainers.mongodb import MongoDbContainer

import app.db.db as _db_module
from app.core.config import settings
from app.models.agent import Agent
from app.models.audit import AuditEvent
from app.models.run import AgentRun
from app.models.tool import Tool

# Document models registered with Beanie
_DOCUMENT_MODELS = [Tool, Agent, AgentRun, AuditEvent]


# Session-scoped container -- started once, shared across all tests

@pytest.fixture(scope="session")
def mongo_container():
    """
    Start a real MongoDB container for the entire test session.

    scope="session" means Docker starts the container once and every test
    in the session shares it. The container is stopped and removed when
    the session ends (~3-5 second startup paid only once).
    """
    with MongoDbContainer("mongo:6") as container:
        yield container


# Function-scoped DB isolation -- clean slate for every test

@pytest_asyncio.fixture(autouse=True)
async def isolated_db(mongo_container):
    """
    Give each test a clean database by dropping all collections before the test.

    autouse=True means this runs for every test automatically.

    Three-step setup:
    1. Build a native PyMongo async client pointed at the container.
    2. Drop all collections from the previous test.
    3. Re-run init_beanie() so Beanie internal state is fresh and indexes
       are recreated on the now-empty collections.

    We also inject the client into _db_module._client so the FastAPI
    lifespan init_db() call sees a non-None client and exits early without
    trying to connect to a production database.
    """
    uri    = mongo_container.get_connection_url()
    client = AsyncMongoClient(uri)
    db     = client[settings.MONGODB_DB]

    # Inject so init_db() is a no-op during app startup
    _db_module._client = client

    # Wipe every collection so this test starts with an empty database
    for model in _DOCUMENT_MODELS:
        await db.drop_collection(model.Settings.name)

    # Re-initialise Beanie against the freshly emptied database
    await init_beanie(database=db, document_models=_DOCUMENT_MODELS)

    yield

    # Teardown: release the client and clear the module-level reference
    client.close()
    _db_module._client = None


# HTTP test client

class FakeArqPool:
    """
    Executes ARQ jobs synchronously in-process — no Redis required.

    enqueue_job() immediately awaits the task function so tests see the
    completed DB state before any assertions run, exactly as if the worker
    had processed the job.
    """
    async def enqueue_job(self, function_name: str, **kwargs) -> None:
        from app.worker import run_agent_task
        await run_agent_task({}, **kwargs)

    async def close(self) -> None:
        pass


@pytest_asyncio.fixture
async def client(isolated_db):
    """
    Async HTTP test client wired to the FastAPI app.

    Depends on isolated_db to guarantee the container client is injected
    before the app lifespan context manager runs.

    FakeArqPool is assigned after lifespan startup so any call to
    enqueue_job() executes the worker task synchronously in-process.
    """
    from app.main import create_app

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        app.state.arq_pool = FakeArqPool()  # override the None sentinel from lifespan
        yield c


# Tenant headers
# These keys must exist in TENANT_API_KEYS in .env.test:
#   TENANT_API_KEYS='{"sk-tenant-alpha-000": "tenant_alpha", "sk-tenant-beta-000": "tenant_beta"}'

ALPHA = {"X-API-Key": "sk-tenant-alpha-000"}
BETA  = {"X-API-Key": "sk-tenant-beta-000"}
BAD   = {"X-API-Key": "sk-bad-key"}
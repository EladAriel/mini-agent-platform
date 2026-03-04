# Models, Schemas & Database

## Overview

The mini-agent-platform uses a layered architecture:

- **Models**: MongoDB documents (Beanie ODM) — database layer
- **Schemas**: Pydantic models — API validation & serialization
- **Database**: MongoDB with async PyMongo driver

```mermaid
flowchart LR
    API[FastAPI] -->|Create/Update| S1[Schema Validation]
    S1 -->|Insert/Update| M[Beanie Model]
    M -->|Query/Insert| DB[(MongoDB)]
    DB -->|Document| M
    M -->|Serialize| S2[Read Schema]
    S2 -->|Response| API
```

---

## Models (Database Layer)

Models are Beanie `Document` classes that map directly to MongoDB collections.

Note:
- Visibility Markers Map for the class diagram:
    - (+) Public: Accessible by any other class.
    - (-) Private: Accessible only within that specific class.
    - (#) Protected: Accessible by the class and its subclasses.

- Multiplicity: indicates how many instances of one class are linked to one instance of another
    - (0..1): Zero or one.
    - (1) Exactly one.
    - (*) Many.
    - (1..*): One or many

### Tool

A reusable capability that agents can invoke.

Class Diagram:
```mermaid
classDiagram
    class Tool {
        +str tenant_id
        +str name
        +str description
        +datetime created_at
        +datetime updated_at
    }
```

**Collection**: `tools`
**Indexes**: `tenant_id` (for tenant-scoped queries)

---

### Agent

An AI agent with tools and configuration.

**One single agent can be associated with many tools.**

Class Diagram:
```mermaid
classDiagram
    class Agent {
        +str tenant_id
        +str name
        +str role
        +str description
        +List~Link~Tool~~ tools
        +datetime created_at
        +datetime updated_at
    }
    class Tool {
        +str tenant_id
        +str name
        +str description
        +datetime created_at
        +datetime updated_at
    }
    Agent "1" --> "*" Tool : references
```

ER Diagram:
```mermaid
erDiagram
    AGENT ||--o{ TOOL : uses
    AGENT {
        string tenant_id
        string name
        string role
        string description
        Link_tools tools
        datetime created_at
        datetime updated_at
    }
    TOOL {
        string tenant_id
        string name
        string description
        datetime created_at
        datetime updated_at
    }
```

**Collection**: `agents`
**Indexes**: `tenant_id`

**Key Design:** Uses `Link[Tool]` for lazy loading - MongoDB stores only references (IDs), not full tool documents.

---

### AgentRun

Records of agent executions.

**One single execution (Run) can have many different tool calls.**

Class Diagram:
```mermaid
classDiagram
    class AgentRun {
        +str tenant_id
        +str agent_id
        +str model
        +str task
        +List~dict~ messages
        +List~ToolCallRecord~ tool_calls
        +str final_response
        +int steps
        +str status
        +datetime created_at
    }
    class ToolCallRecord {
        +int step
        +str tool_name
        +str tool_input
        +str tool_output
    }
    AgentRun "1" --> "*" ToolCallRecord : embeds
```

**Collection**: `agent_runs`
**Indexes**:
- `tenant_id` — tenant isolation
- `(tenant_id, agent_id)` — run history per agent
- `created_at` (desc) — chronological queries

---

## Database Collections

ER Diagram:
```mermaid
erDiagram
    AGENTS {
        ObjectId _id PK
        string tenant_id
        string name
        string role
        string description
        array tools "List of Tool references"
        datetime created_at
        datetime updated_at
    }

    TOOLS {
        ObjectId _id PK
        string tenant_id
        string name
        string description
        datetime created_at
        datetime updated_at
    }

    AGENT_RUNS {
        ObjectId _id PK
        string tenant_id
        string agent_id FK
        string model
        string task
        array messages
        array tool_calls
        string final_response
        int steps
        string status
        datetime created_at
    }

    AGENTS ||--o{ TOOLS : "references"
    AGENTS ||--o{ AGENT_RUNS : "executes"
```

### Indexes

| Collection   | Index Fields                    | Purpose                         |
|--------------|---------------------------------|---------------------------------|
| agents       | `tenant_id`                     | Tenant isolation                |
| tools        | `tenant_id`                     | Tenant isolation                |
| agent_runs   | `tenant_id`                     | Tenant isolation                |
| agent_runs   | `tenant_id` + `agent_id`        | Query runs by agent             |
| agent_runs   | `created_at` (DESC)             | Sort by newest first            |

---

## Schemas (API Layer)

Schemas validate API requests and format responses. Three types per entity:

| Type | Purpose | Example |
|------|---------|---------|
| **Create** | Validate POST requests | `AgentCreate`, `ToolCreate` |
| **Read** | Format GET responses | `AgentRead`, `RunRead` |
| **Update** | Validate PATCH requests | `AgentUpdate`, `ToolUpdate` |

### Tool Schemas

| Schema      | Purpose                              | Key Fields                              |
|-------------|--------------------------------------|-----------------------------------------|
| `ToolCreate`| Create a new tool                    | `name` (required), `description`        |
| `ToolRead`  | Return tool data (includes ID)       | `id`, `name`, `description`, timestamps |
| `ToolUpdate`| Partial update (PATCH)               | Optional `name`, `description`          |

---

### Agent Schemas

| Schema        | Purpose                              | Key Fields                                           |
|---------------|--------------------------------------|------------------------------------------------------|
| `AgentCreate` | Create a new agent                   | `name`, `role`, `description`, `tool_ids`            |
| `AgentRead`   | Return agent with resolved tools     | `id`, `name`, `role`, `tools[]`, timestamps          |
| `AgentUpdate` | Partial update                       | Optional fields, `tool_ids: None` = no change, `[]` = remove all |


**Note**: `tool_ids` in Create/Update becomes `tools` in Read (IDs → resolved objects).

```mermaid
flowchart LR
    Create["AgentCreate<br/>tool_ids: [123, 456]"] --> |Service resolves| Read["AgentRead<br/>tools: [ToolRead, ToolRead]"]
```

---

### Run Schemas

| Schema        | Purpose                              | Key Fields                                           |
|---------------|--------------------------------------|------------------------------------------------------|
| `RunRequest`  | Start agent execution                | `task`, `model` (defaults to gpt-4o)                 |
| `RunResponse` | Immediate execution result           | `run_id`, `final_response`, `tool_calls`, `steps`    |
| `RunRead`     | History view (paginated)             | Same as RunResponse + `status`                       |
| `PaginatedRuns`| List wrapper                        | `items[]`, `total`, `page`, `pages`                  |

---

## Database Connection

```mermaid
sequenceDiagram
    participant App as FastAPI App
    participant DB as app/db/db.py
    participant Beanie as Beanie ODM
    participant Mongo as MongoDB

    App->>DB: startup: init_db()
    DB->>Mongo: AsyncMongoClient.connect()
    DB->>Beanie: init_beanie(database, document_models)
    Beanie->>Mongo: Create indexes automatically
    Note over App,Mongo: Ready to serve requests

    App->>Beanie: Agent.find_one(...)
    Beanie->>Mongo: Query
    Mongo-->>Beanie: Document
    Beanie-->>App: Agent instance

    App->>DB: shutdown: close_db()
    DB->>Mongo: client.close()
```

### Key Points

- **Beanie ODM**: Provides async MongoDB operations directly on model classes
- **Lazy Loading**: `Agent.tools` loads as references until explicitly fetched
- **Indexes**: Defined in model `Settings`, created automatically on init
- **Connection**: Managed globally, closed on app shutdown

---

## Data Flow Example

Creating an agent with tools:

```mermaid
sequenceDiagram
    participant Client
    participant API as POST /agents
    participant Schema as AgentCreate
    participant Service as AgentService
    participant Model as Agent (Beanie)
    participant DB as MongoDB

    Client->>API: {name, role, desc, tool_ids}
    API->>Schema: Validate (Pydantic)
    Schema->>API: Validated data
    API->>Service: create_agent(data)
    Service->>Model: Agent(**data)
    Service->>Model: agent.link(tools)
    Service->>Model: agent.insert()
    Model->>DB: Insert document
    DB-->>Model: Created
    Service->>Service: to_read_schema()
    Service-->>API: AgentRead
    API-->>Client: {id, name, tools: [...]}
```

### Full Request Lifecycle

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant S as Schema
    participant SV as Service
    participant M as Model
    participant DB as MongoDB

    C->>API: POST /agents (ToolCreate)
    API->>S: Validate input
    S-->>API: Validated data
    API->>SV: Create agent
    SV->>M: Agent(...)
    M->>DB: Insert document
    DB-->>M: Saved with _id
    M-->>SV: Agent instance
    SV->>M: Fetch linked tools
    M->>DB: Resolve references
    DB-->>M: Tool documents
    M-->>SV: Agent with tools
    SV->>S: AgentRead(agent)
    S-->>API: JSON response
    API-->>C: {id, name, tools: [...]}
```

---

## Supported Models

| Model             | Use Case                                      | Default |
|-------------------|-----------------------------------------------|---------|
| `gpt-4o`          | Complex multi-step reasoning, tool-heavy tasks| ✓       |
| `gpt-4o-mini`     | Fast, simple tasks (low latency)              |         |
| `claude-3-5-sonnet`| Writing, analysis, nuanced instructions      |         |
| `claude-4-5-sonnet`| Advanced reasoning, complex agent tasks      |         |

Only these models can be used in `RunRequest.model`.
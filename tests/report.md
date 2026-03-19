# 🧪 Test Report

## Summary

| | |
|---|---|
| **Score** | `306 / 306` |
| **Passed** | 306 ✅ |
| **Failed** | 0 — |
| **Skipped** | 0 — |
| **Duration** | 185,357 ms |
| **Pass rate** | 100% |

## Results

### 📁 `tests\test_agents_runs_api.py`  —  52/52 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestAuth | missing key returns 401 | ✅ 1/1 | — | — | {"event": "Pulling image testcontainers/ryuk:0.8.1", "level": "info", "logger": "testcontainers.core.container", "tenant": "-", "timestamp": "2026-03-18T10:42:36.588538Z"} {"event": "Container started: 0e08496413af", "level": "info", "logger": "testcontainers.core.container", "tenant": "-", "timesta | 6052.8 ms |
| TestAuth | invalid key returns 401 | ✅ 1/1 | — | — | ✓ assertions passed | 334.7 ms |
| TestAuth | valid key returns 200 | ✅ 1/1 | — | — | ✓ assertions passed | 332.5 ms |
| TestAgentCRUD | create without tools returns 201 | ✅ 1/1 | — | — | {"event": "API: Create agent request: name=Simple", "level": "info", "logger": "app.api.v1.agents", "tenant": "-", "timestamp": "2026-03-18T10:42:43.561964Z"} {"event": "Creating agent: name=Simple", "level": "info", "logger": "app.services.agent_service", "tenant": "-", "timestamp": "2026-03-18T10: | 393.9 ms |
| TestAgentCRUD | create with tools embeds tool objects | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:44.018797Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 469.1 ms |
| TestAgentCRUD | create with nonexistent tool returns 422 | ✅ 1/1 | — | — | {"event": "API: Create agent request: name=Researcher", "level": "info", "logger": "app.api.v1.agents", "tenant": "-", "timestamp": "2026-03-18T10:42:44.457000Z"} {"event": "Creating agent: name=Researcher", "level": "info", "logger": "app.services.agent_service", "tenant": "-", "timestamp": "2026-0 | 416.5 ms |
| TestAgentCRUD | create with malformed tool id returns 422 | ✅ 1/1 | — | — | {"event": "API: Create agent request: name=Researcher", "level": "info", "logger": "app.api.v1.agents", "tenant": "-", "timestamp": "2026-03-18T10:42:44.915791Z"} {"event": "Creating agent: name=Researcher", "level": "info", "logger": "app.services.agent_service", "tenant": "-", "timestamp": "2026-0 | 427.2 ms |
| TestAgentCRUD | create missing name returns 422 | ✅ 1/1 | — | — | ✓ assertions passed | 367.3 ms |
| TestAgentCRUD | list empty by default | ✅ 1/1 | — | — | ✓ assertions passed | 412.7 ms |
| TestAgentCRUD | list returns created agent | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:46.180778Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 496.6 ms |
| TestAgentCRUD | filter by tool name includes match | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:46.744544Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 574.0 ms |
| TestAgentCRUD | filter by tool name is case insensitive | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:47.442773Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 678.1 ms |
| TestAgentCRUD | filter by tool name no match returns empty | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:47.910184Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 460.5 ms |
| TestAgentCRUD | get returns correct agent | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:48.323606Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 409.0 ms |
| TestAgentCRUD | get nonexistent returns 404 | ✅ 1/1 | — | — | {"event": "Agent not found: id=000000000000000000000000", "level": "warning", "logger": "app.services.agent_service", "tenant": "-", "timestamp": "2026-03-18T10:42:48.767794Z"} | 414.0 ms |
| TestAgentCRUD | get malformed id returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 423.4 ms |
| TestAgentCRUD | update name | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:49.607599Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 451.7 ms |
| TestAgentCRUD | update does not touch omitted fields | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:50.038461Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 418.5 ms |
| TestAgentCRUD | update removes tools when empty list | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:50.449442Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 392.5 ms |
| TestAgentCRUD | update omitting tool ids leaves tools unchanged | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:50.818368Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 367.2 ms |
| TestAgentCRUD | update nonexistent returns 404 | ✅ 1/1 | — | — | {"event": "API: Update agent request: agent_id=000000000000000000000000", "level": "info", "logger": "app.api.v1.agents", "tenant": "-", "timestamp": "2026-03-18T10:42:51.197706Z"} {"event": "Updating agent: id=000000000000000000000000", "level": "info", "logger": "app.services.agent_service", "tena | 347.8 ms |
| TestAgentCRUD | delete returns 204 | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:51.589378Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 408.8 ms |
| TestAgentCRUD | delete makes agent unfetchable | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:52.006694Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 425.5 ms |
| TestAgentCRUD | delete nonexistent returns 404 | ✅ 1/1 | — | — | {"event": "API: Delete agent request: agent_id=000000000000000000000000", "level": "info", "logger": "app.api.v1.agents", "tenant": "-", "timestamp": "2026-03-18T10:42:52.358081Z"} {"event": "Deleting agent: id=000000000000000000000000", "level": "info", "logger": "app.services.agent_service", "tena | 314.0 ms |
| TestAgentTenantIsolation | agent invisible to other tenant | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:52.672385Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 329.2 ms |
| TestAgentTenantIsolation | list returns only own agents | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:53.041474Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 362.9 ms |
| TestAgentTenantIsolation | beta cannot update alpha agent | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:53.403758Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 364.1 ms |
| TestAgentTenantIsolation | beta cannot delete alpha agent | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:53.816910Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 413.7 ms |
| TestAgentTenantIsolation | tool from other tenant rejected | ✅ 1/1 | BETA's tool id must not be usable when creating an ALPHA agent. | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:54.261293Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 423.2 ms |
| TestAgentRun | run returns 202 with required fields | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:54.627563Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 690.3 ms |
| TestAgentRun | run 202 does not echo task | ✅ 1/1 | H2: raw task must not appear in the 202 response to prevent PII leakage. | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:55.325787Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 484.7 ms |
| TestAgentRun | poll run until completed | ✅ 1/1 | Submit a run, then poll GET /runs/{run_id} — FakeArqPool executes synchronously. | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:55.885928Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 556.6 ms |
| TestAgentRun | run with search keyword calls web search | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:56.566708Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 1087.4 ms |
| TestAgentRun | run tool call record has input and output | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:57.616721Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 681.6 ms |
| TestAgentRun | run without tool keyword returns no tool calls | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:58.348003Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 677.4 ms |
| TestAgentRun | run unsupported model returns 422 | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:58.992242Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 531.7 ms |
| TestAgentRun | run prompt injection returns 400 | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:59.374859Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 378.9 ms |
| TestAgentRun | run injection response does not leak matched text | ✅ 1/1 | H3: 400 detail must be generic — must not expose matched pattern or payload. | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:42:59.757390Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 371.8 ms |
| TestAgentRun | run task is anonymized in db | ✅ 1/1 | M6: raw PII in the task must not be persisted to the AgentRun document. | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:43:00.114300Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 400.9 ms |
| TestAgentRun | run on nonexistent agent returns 404 | ✅ 1/1 | — | — | {"event": "API: Run agent request: agent_id=000000000000000000000000 model=gpt-4o", "level": "info", "logger": "app.api.v1.agents", "tenant": "-", "timestamp": "2026-03-18T10:43:00.497986Z"} {"event": "Agent not found: id=000000000000000000000000", "level": "warning", "logger": "app.services.agent_s | 319.8 ms |
| TestAgentRunHistory | history empty before any run | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:43:00.879335Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 397.0 ms |
| TestAgentRunHistory | run appears in history | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:43:01.329219Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 504.6 ms |
| TestAgentRunHistory | pagination total and pages | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:43:01.794740Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 691.0 ms |
| TestAgentRunHistory | pagination last page has remainder | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:43:02.451847Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 581.3 ms |
| TestAgentRunHistory | history ordered most recent first | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:43:03.048521Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 466.9 ms |
| TestAgentRunHistory | history scoped to agent | ✅ 1/1 | Runs from agent A must not appear in agent B's history. | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:43:03.496422Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 408.0 ms |
| TestAgentRunHistory | history on nonexistent agent returns 404 | ✅ 1/1 | — | — | {"event": "Agent not found: id=000000000000000000000000", "level": "warning", "logger": "app.services.agent_service", "tenant": "-", "timestamp": "2026-03-18T10:43:03.964674Z"} | 380.7 ms |
| TestGlobalRunHistory | global runs empty before any run | ✅ 1/1 | — | — | ✓ assertions passed | 336.0 ms |
| TestGlobalRunHistory | global runs includes run after execution | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:43:04.630691Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 416.0 ms |
| TestGlobalRunHistory | global runs aggregates across agents | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:43:05.135921Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 550.5 ms |
| TestGlobalRunHistory | global runs scoped to tenant | ✅ 1/1 | ALPHA's runs must not appear in BETA's global history. | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:43:05.646540Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 463.3 ms |
| TestGlobalRunHistory | global runs pagination | ✅ 1/1 | — | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:43:06.203985Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 803.8 ms |

---

### 📁 `tests\test_audit.py`  —  9/9 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestAuditEventPersistence | successful run writes started and completed | ✅ 1/1 | A completed run produces exactly 2 audit events: started + completed. | — | {"event": "Worker: starting run_id=69ba81badd317528247b1280 agent_id=69ba81badd317528247b127f", "level": "info", "logger": "app.worker", "tenant": "t:alpha", "timestamp": "2026-03-18T10:43:06.935917Z"} {"event": "Running agent: id=69ba81badd317528247b127f name=Researcher model=gpt-4o", "level": "inf | 414.1 ms |
| TestAuditEventPersistence | completed event has steps in metadata | ✅ 1/1 | The 'completed' audit event carries metadata.steps. | — | {"event": "Worker: starting run_id=69ba81bbdd317528247b1286 agent_id=69ba81bbdd317528247b1285", "level": "info", "logger": "app.worker", "tenant": "t:alpha", "timestamp": "2026-03-18T10:43:07.300369Z"} {"event": "Running agent: id=69ba81bbdd317528247b1285 name=Researcher model=gpt-4o", "level": "inf | 361.8 ms |
| TestAuditEventPersistence | prompt injection writes started and failed | ✅ 1/1 | A prompt-injection failure produces exactly 2 events: started + failed. | — | {"event": "Worker: starting run_id=69ba81bbdd317528247b128c agent_id=69ba81bbdd317528247b128b", "level": "info", "logger": "app.worker", "tenant": "t:alpha", "timestamp": "2026-03-18T10:43:07.661034Z"} {"event": "Running agent: id=69ba81bbdd317528247b128b name=Researcher model=gpt-4o", "level": "inf | 331.6 ms |
| TestAuditEventPersistence | failed event has error message in metadata | ✅ 1/1 | The 'failed' audit event carries metadata.error_message. | — | {"event": "Worker: starting run_id=69ba81bcdd317528247b1292 agent_id=69ba81bcdd317528247b1291", "level": "info", "logger": "app.worker", "tenant": "t:alpha", "timestamp": "2026-03-18T10:43:08.019977Z"} {"event": "Running agent: id=69ba81bcdd317528247b1291 name=Researcher model=gpt-4o", "level": "inf | 356.6 ms |
| TestAuditEventPersistence | runtime error writes failed with generic message | ✅ 1/1 | An unexpected RuntimeError from run_agent() produces a 'failed' event | with the safe generic message, never the raw exception text. | {"event": "Worker: starting run_id=69ba81bcdd317528247b1298 agent_id=69ba81bcdd317528247b1297", "level": "info", "logger": "app.worker", "tenant": "t:alpha", "timestamp": "2026-03-18T10:43:08.435436Z"} {"event": "Worker: run_id=69ba81bcdd317528247b1298 unexpected error: Internal catastrophe", "level | 481.4 ms |
| TestAuditEventPersistence | all events have occurred at | ✅ 1/1 | Every audit event document has a non-None occurred_at timestamp. | — | {"event": "Worker: starting run_id=69ba81bcdd317528247b129e agent_id=69ba81bcdd317528247b129d", "level": "info", "logger": "app.worker", "tenant": "t:alpha", "timestamp": "2026-03-18T10:43:08.963555Z"} {"event": "Running agent: id=69ba81bcdd317528247b129d name=Researcher model=gpt-4o", "level": "inf | 508.0 ms |
| TestCreatedEventViaAPI | post run writes created event | ✅ 1/1 | POST /agents/{id}/run persists a 'created' AuditEvent for the tenant. | — | {"event": "API: Create tool request: name=web_search", "level": "info", "logger": "app.api.v1.tools", "tenant": "-", "timestamp": "2026-03-18T10:43:09.456617Z"} {"event": "Creating tool: name=web_search", "level": "info", "logger": "app.services.tool_service", "tenant": "-", "timestamp": "2026-03-18 | 484.8 ms |
| TestAuditNonBlocking | record event swallows insert failure | ✅ 1/1 | record_event() must not propagate DB exceptions to callers. | — | {"event": "Failed to write audit event: run_id=deadbeefdeadbeefdeadbeef event=created error=Simulated DB failure", "level": "error", "logger": "app.services.audit_service", "tenant": "-", "timestamp": "2026-03-18T10:43:09.863929Z"} | 333.9 ms |
| TestAuditNonBlocking | run completes when audit fails | ✅ 1/1 | A broken audit path must not prevent the run from reaching a terminal state. | We simulate DB failure at the insert level so record_event()'s own | {"event": "Worker: starting run_id=69ba81bedd317528247b12ac agent_id=69ba81bedd317528247b12ab", "level": "info", "logger": "app.worker", "tenant": "t:alpha", "timestamp": "2026-03-18T10:43:10.200652Z"} {"event": "Failed to write audit event: run_id=69ba81bedd317528247b12ac event=started error=Audit | 379.3 ms |

---

### 📁 `tests\test_audit_metadata.py`  —  11/11 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestTruncateMetadata | small metadata passes through | ✅ 1/1 | — | — | ✓ assertions passed | 346.3 ms |
| TestTruncateMetadata | empty metadata passes through | ✅ 1/1 | — | — | ✓ assertions passed | 330.2 ms |
| TestTruncateMetadata | metadata exactly at limit passes | ✅ 1/1 | — | — | ✓ assertions passed | 344.0 ms |
| TestTruncateMetadata | metadata one byte over limit is truncated | ✅ 1/1 | — | — | {"event": "Audit metadata exceeds 10000 bytes; truncating. original_size=10001", "level": "warning", "logger": "app.services.audit_service", "tenant": "-", "timestamp": "2026-03-18T10:43:11.600977Z"} | 311.9 ms |
| TestTruncateMetadata | large metadata is truncated | ✅ 1/1 | — | — | {"event": "Audit metadata exceeds 10000 bytes; truncating. original_size=20012", "level": "warning", "logger": "app.services.audit_service", "tenant": "-", "timestamp": "2026-03-18T10:43:11.936260Z"} | 329.5 ms |
| TestTruncateMetadata | non serializable metadata is replaced | ✅ 1/1 | — | — | {"event": "Audit metadata is not JSON-serializable; dropping payload.", "level": "warning", "logger": "app.services.audit_service", "tenant": "-", "timestamp": "2026-03-18T10:43:12.292410Z"} | 351.7 ms |
| TestTruncateMetadata | original dict is not mutated | ✅ 1/1 | — | — | {"event": "Audit metadata exceeds 10000 bytes; truncating. original_size=20012", "level": "warning", "logger": "app.services.audit_service", "tenant": "-", "timestamp": "2026-03-18T10:43:12.604283Z"} | 308.2 ms |
| TestRecordEventMetadataTruncation | oversized metadata stored as sentinel | ✅ 1/1 | — | — | {"event": "Audit metadata exceeds 10000 bytes; truncating. original_size=20012", "level": "warning", "logger": "app.services.audit_service", "tenant": "-", "timestamp": "2026-03-18T10:43:12.916074Z"} | 313.4 ms |
| TestRecordEventMetadataTruncation | normal metadata stored intact | ✅ 1/1 | — | — | ✓ assertions passed | 333.0 ms |
| TestTruncationWarningLogged | warning is emitted when truncated | ✅ 1/1 | — | — | {"event": "Audit metadata exceeds 10000 bytes; truncating. original_size=20012", "level": "warning", "logger": "app.services.audit_service", "tenant": "-", "timestamp": "2026-03-18T10:43:13.616674Z"} | 354.4 ms |
| TestTruncationWarningLogged | no warning for normal metadata | ✅ 1/1 | — | — | ✓ assertions passed | 311.8 ms |

---

### 📁 `tests\test_auth_rate_limit.py`  —  6/6 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| module-level | bad key returns 401 | ✅ 1/1 | First failed attempt must return 401, not 429. | — | ✓ assertions passed | 311.9 ms |
| module-level | bad key within limit returns 401 | ✅ 1/1 | Attempts within the failure threshold must each return 401. | — | ✓ assertions passed | 346.0 ms |
| module-level | exceeding auth failure limit returns 429 | ✅ 1/1 | 4th bad attempt within the window must return 429. | — | {"event": "Auth brute-force limit exceeded: ip=127.0.0.1", "level": "warning", "logger": "app.core.security", "tenant": "-", "timestamp": "2026-03-18T10:43:14.943759Z"} | 344.4 ms |
| module-level | 429 detail is generic | ✅ 1/1 | The 429 body must not leak any internal information (no key values, | no pattern matches, no IP address). | {"event": "Auth brute-force limit exceeded: ip=127.0.0.1", "level": "warning", "logger": "app.core.security", "tenant": "-", "timestamp": "2026-03-18T10:43:15.276435Z"} | 328.2 ms |
| module-level | valid key succeeds after bad attempts | ✅ 1/1 | Valid-key requests must succeed even if the same IP exceeded the failed-auth | threshold. The counter only throttles 401 paths — authenticated requests | {"event": "Auth brute-force limit exceeded: ip=127.0.0.1", "level": "warning", "logger": "app.core.security", "tenant": "-", "timestamp": "2026-03-18T10:43:15.662038Z"} | 391.5 ms |
| module-level | auth failure limit disabled by default | ✅ 1/1 | When RATE_LIMIT_ENABLED=false (default in .env.test) many bad requests | must all return 401 — never 429. | ✓ assertions passed | 500.2 ms |

---

### 📁 `tests\test_guardrail.py`  —  95/95 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestPromptInjectionError | str includes category and matched text | ✅ 1/1 | — | — | ✓ assertions passed | 350.7 ms |
| TestPromptInjectionError | attributes accessible | ✅ 1/1 | — | — | ✓ assertions passed | 373.4 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 333.0 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 331.3 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 329.7 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 350.6 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 355.8 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 323.4 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 383.8 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 390.7 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 385.7 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 368.8 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 363.2 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 289.1 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 302.5 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 320.7 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 291.5 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 308.5 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 326.0 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 343.4 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 356.0 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 305.6 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 301.8 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 304.6 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 362.7 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 363.1 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 376.6 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 357.7 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 335.6 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 344.7 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 395.4 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 328.3 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 383.4 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 387.8 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 333.9 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 410.6 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 343.3 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 329.7 ms |
| TestInvisibleCharacters | invisible char blocked | ✅ 1/1 | — | — | ✓ assertions passed | 295.2 ms |
| TestInvisibleCharacters | invisible char blocked | ✅ 1/1 | — | — | ✓ assertions passed | 463.1 ms |
| TestInvisibleCharacters | invisible char blocked | ✅ 1/1 | — | — | ✓ assertions passed | 379.9 ms |
| TestInvisibleCharacters | invisible char blocked | ✅ 1/1 | — | — | ✓ assertions passed | 362.4 ms |
| TestInvisibleCharacters | invisible char blocked | ✅ 1/1 | — | — | ✓ assertions passed | 328.3 ms |
| TestHomoglyphs | known homoglyph blocked | ✅ 1/1 | — | — | ✓ assertions passed | 334.5 ms |
| TestHomoglyphs | known homoglyph blocked | ✅ 1/1 | — | — | ✓ assertions passed | 325.2 ms |
| TestHomoglyphs | known homoglyph blocked | ✅ 1/1 | — | — | ✓ assertions passed | 347.0 ms |
| TestHomoglyphs | known homoglyph blocked | ✅ 1/1 | — | — | ✓ assertions passed | 340.6 ms |
| TestHomoglyphs | legitimate accented chars pass | ✅ 1/1 | — | — | ✓ assertions passed | 303.8 ms |
| TestHomoglyphs | legitimate accented chars pass | ✅ 1/1 | — | — | ✓ assertions passed | 341.7 ms |
| TestHomoglyphs | legitimate accented chars pass | ✅ 1/1 | — | — | ✓ assertions passed | 325.4 ms |
| TestHomoglyphs | legitimate accented chars pass | ✅ 1/1 | — | — | ✓ assertions passed | 307.1 ms |
| TestBase64Encoding | encoded override payload blocked | ✅ 1/1 | — | — | ✓ assertions passed | 319.6 ms |
| TestBase64Encoding | encoded exfiltration payload blocked | ✅ 1/1 | — | — | ✓ assertions passed | 319.1 ms |
| TestBase64Encoding | clean base64 passes | ✅ 1/1 | — | — | ✓ assertions passed | 384.2 ms |
| TestBase64Encoding | short base64 like string passes | ✅ 1/1 | — | — | ✓ assertions passed | 317.3 ms |
| TestCheckToolOutput | clean output returned unchanged | ✅ 1/1 | — | — | ✓ assertions passed | 332.0 ms |
| TestCheckToolOutput | long output truncated silently | ✅ 1/1 | — | — | ✓ assertions passed | 378.8 ms |
| TestCheckToolOutput | output at exact limit not truncated | ✅ 1/1 | — | — | ✓ assertions passed | 378.6 ms |
| TestCheckToolOutput | injection in tool output raises | ✅ 1/1 | — | — | ✓ assertions passed | 301.5 ms |
| TestCheckToolOutput | injection in truncated region does not raise | ✅ 1/1 | Malicious content that falls entirely beyond MAX_TOOL_OUTPUT_LENGTH | is truncated before pattern checks run — it never reaches the regex. | ✓ assertions passed | 356.1 ms |
| TestCheckToolOutput | tool name does not affect output check | ✅ 1/1 | tool_name is metadata only; the check is purely on content. | — | ✓ assertions passed | 395.5 ms |
| TestHarmfulOutputError | str includes category and matched text | ✅ 1/1 | — | — | ✓ assertions passed | 390.7 ms |
| TestHarmfulOutputError | attributes accessible | ✅ 1/1 | — | — | ✓ assertions passed | 342.0 ms |
| TestHarmfulOutputError | is subclass of value error | ✅ 1/1 | — | — | ✓ assertions passed | 354.2 ms |
| TestCheckOutputContent | safe response does not raise | ✅ 1/1 | — | — | ✓ assertions passed | 315.7 ms |
| TestCheckOutputContent | safe response does not raise | ✅ 1/1 | — | — | ✓ assertions passed | 350.4 ms |
| TestCheckOutputContent | safe response does not raise | ✅ 1/1 | — | — | ✓ assertions passed | 383.6 ms |
| TestCheckOutputContent | safe response does not raise | ✅ 1/1 | — | — | ✓ assertions passed | 353.1 ms |
| TestCheckOutputContent | safe response does not raise | ✅ 1/1 | — | — | ✓ assertions passed | 303.4 ms |
| TestCheckOutputContent | safe response does not raise | ✅ 1/1 | — | — | ✓ assertions passed | 290.7 ms |
| TestCheckOutputContent | harmful response raises with correct category | ✅ 1/1 | — | — | ✓ assertions passed | 350.1 ms |
| TestCheckOutputContent | harmful response raises with correct category | ✅ 1/1 | — | — | ✓ assertions passed | 490.3 ms |
| TestCheckOutputContent | harmful response raises with correct category | ✅ 1/1 | — | — | ✓ assertions passed | 728.9 ms |
| TestCheckOutputContent | harmful response raises with correct category | ✅ 1/1 | — | — | ✓ assertions passed | 464.8 ms |
| TestCheckOutputContent | harmful response raises with correct category | ✅ 1/1 | — | — | ✓ assertions passed | 392.3 ms |
| TestCheckOutputContent | harmful response raises with correct category | ✅ 1/1 | — | — | ✓ assertions passed | 398.5 ms |
| TestSecretLeakError | str includes category and matched text | ✅ 1/1 | — | — | ✓ assertions passed | 426.5 ms |
| TestSecretLeakError | attributes accessible | ✅ 1/1 | — | — | ✓ assertions passed | 409.6 ms |
| TestSecretLeakError | is subclass of value error | ✅ 1/1 | — | — | ✓ assertions passed | 512.6 ms |
| TestCheckToolOutputSecrets | clean output does not raise | ✅ 1/1 | — | — | ✓ assertions passed | 452.1 ms |
| TestCheckToolOutputSecrets | clean output does not raise | ✅ 1/1 | — | — | ✓ assertions passed | 477.2 ms |
| TestCheckToolOutputSecrets | clean output does not raise | ✅ 1/1 | — | — | ✓ assertions passed | 455.6 ms |
| TestCheckToolOutputSecrets | clean output does not raise | ✅ 1/1 | — | — | ✓ assertions passed | 516.6 ms |
| TestCheckToolOutputSecrets | aws key raises | ✅ 1/1 | — | — | ✓ assertions passed | 497.5 ms |
| TestCheckToolOutputSecrets | openai key raises | ✅ 1/1 | — | — | ✓ assertions passed | 503.9 ms |
| TestCheckToolOutputSecrets | bearer token raises | ✅ 1/1 | — | — | ✓ assertions passed | 486.9 ms |
| TestCheckToolOutputSecrets | pem rsa block raises | ✅ 1/1 | — | — | ✓ assertions passed | 495.9 ms |
| TestCheckToolOutputSecrets | pem ec block raises | ✅ 1/1 | — | — | ✓ assertions passed | 460.0 ms |
| TestCheckToolOutputSecrets | generic api key assignment raises | ✅ 1/1 | — | — | ✓ assertions passed | 428.5 ms |
| TestCheckToolOutputSecrets | github pat raises | ✅ 1/1 | — | — | ✓ assertions passed | 440.6 ms |
| TestCheckToolOutputSecrets | slack token raises | ✅ 1/1 | — | — | ✓ assertions passed | 399.7 ms |
| TestCheckToolOutputSecrets | google key raises | ✅ 1/1 | — | — | ✓ assertions passed | 378.8 ms |
| TestCheckToolOutputSecrets | injection phrase wins over secret | ✅ 1/1 | When both an injection phrase and a secret are present, _check_patterns | runs first so PromptInjectionError is raised, not SecretLeakError. | ✓ assertions passed | 387.7 ms |
| TestCheckToolOutputSecrets | secret past truncation boundary does not raise | ✅ 1/1 | A secret that falls entirely beyond MAX_TOOL_OUTPUT_LENGTH is truncated | before _check_secrets runs — it never reaches the regex scanner. | ✓ assertions passed | 474.9 ms |
| TestCheckToolOutputSecrets | secret leak error not caught by injection handler | ✅ 1/1 | Type isolation: SecretLeakError must not accidentally be caught by | an except PromptInjectionError clause (they are sibling classes). | ✓ assertions passed | 537.2 ms |

---

### 📁 `tests\test_health.py`  —  10/10 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| module-level | returns 200 ok | ✅ 1/1 | — | — | ✓ assertions passed | 487.0 ms |
| module-level | body status ok | ✅ 1/1 | — | — | ✓ assertions passed | 418.2 ms |
| module-level | body db ok | ✅ 1/1 | — | — | ✓ assertions passed | 410.1 ms |
| module-level | returns 503 when db down | ✅ 1/1 | — | — | ✓ assertions passed | 962.7 ms |
| module-level | body status degraded when db down | ✅ 1/1 | — | — | ✓ assertions passed | 972.0 ms |
| module-level | body db unavailable when db down | ✅ 1/1 | — | — | ✓ assertions passed | 945.5 ms |
| module-level | returns 503 when client is none | ✅ 1/1 | — | — | ✓ assertions passed | 471.8 ms |
| module-level | health within limit returns 200 | ✅ 1/1 | First two requests (within the 2/min limit) must succeed. | — | ✓ assertions passed | 456.2 ms |
| module-level | health exceeding limit returns 429 | ✅ 1/1 | Third request within the same minute must be rejected with 429. | — | {"event": "ratelimit 2 per 1 minute (127.0.0.1) exceeded at endpoint: /health", "level": "warning", "logger": "slowapi", "tenant": "-", "timestamp": "2026-03-18T10:43:57.994914Z"} | 434.8 ms |
| module-level | health 429 has retry after header | ✅ 1/1 | HTTP 429 on /health must include a Retry-After header. | — | {"event": "ratelimit 2 per 1 minute (127.0.0.1) exceeded at endpoint: /health", "level": "warning", "logger": "slowapi", "tenant": "-", "timestamp": "2026-03-18T10:43:58.514941Z"} | 515.2 ms |

---

### 📁 `tests\test_logging.py`  —  6/6 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestTenantContextFilter | filter sets tenant field | ✅ 1/1 | — | — | ✓ assertions passed | 482.9 ms |
| TestTenantContextFilter | filter default tenant | ✅ 1/1 | — | — | ✓ assertions passed | 564.5 ms |
| TestConfigLogging | config logging does not raise | ✅ 1/1 | Smoke test: config_logging() runs without exceptions. | — | ✓ assertions passed | 531.8 ms |
| TestConfigLogging | get logger returns stdlib logger | ✅ 1/1 | — | — | ✓ assertions passed | 501.0 ms |
| TestConfigLogging | json output contains required fields | ✅ 1/1 | Capture stdout, parse JSON line, assert required fields present. | — | ✓ assertions passed | 462.4 ms |
| TestConfigLogging | tenant field present in log output | ✅ 1/1 | Set tenant_ctx, capture JSON log, assert tenant key matches. | — | ✓ assertions passed | 405.0 ms |

---

### 📁 `tests\test_mock_llm.py`  —  23/23 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestBindTools | returns new instance | ✅ 1/1 | — | — | ✓ assertions passed | 414.1 ms |
| TestBindTools | bound model has correct tool names | ✅ 1/1 | — | — | ✓ assertions passed | 449.4 ms |
| TestBindTools | original instance is unaffected | ✅ 1/1 | bind_tools must not mutate the original (model_copy deep=True). | — | ✓ assertions passed | 446.5 ms |
| TestBindTools | llm type | ✅ 1/1 | — | — | ✓ assertions passed | 436.7 ms |
| TestToolCallDecision | keyword triggers correct tool | ✅ 1/1 | — | — | ✓ assertions passed | 454.6 ms |
| TestToolCallDecision | calculator keyword | ✅ 1/1 | — | — | ✓ assertions passed | 475.2 ms |
| TestToolCallDecision | weather keyword | ✅ 1/1 | — | — | ✓ assertions passed | 475.4 ms |
| TestToolCallDecision | no tool call when no tools bound | ✅ 1/1 | Keyword present but no tools registered → straight to final answer. | — | ✓ assertions passed | 458.4 ms |
| TestToolCallDecision | no tool call when keyword absent | ✅ 1/1 | — | — | ✓ assertions passed | 446.5 ms |
| TestToolCallDecision | keyword matches but tool not bound | ✅ 1/1 | 'search' keyword matches web_search rule, but only calculator is bound. | — | ✓ assertions passed | 494.9 ms |
| TestToolCallDecision | no tool call after tool result | ✅ 1/1 | Once a ToolMessage exists in history the model must produce a final answer. | — | ✓ assertions passed | 476.5 ms |
| TestToolCallDecision | system message does not trigger tool | ✅ 1/1 | SystemMessage alone must never cause a tool call. | — | ✓ assertions passed | 471.7 ms |
| TestToolCallArgKeys | web search uses query key | ✅ 1/1 | — | — | ✓ assertions passed | 456.1 ms |
| TestToolCallArgKeys | calculator uses expression key | ✅ 1/1 | — | — | ✓ assertions passed | 410.3 ms |
| TestToolCallArgKeys | weather uses location key | ✅ 1/1 | — | — | ✓ assertions passed | 406.4 ms |
| TestToolCallArgKeys | summarizer uses text key | ✅ 1/1 | — | — | ✓ assertions passed | 450.6 ms |
| TestToolCallArgKeys | translator uses text key | ✅ 1/1 | — | — | ✓ assertions passed | 453.8 ms |
| TestToolCallArgKeys | email sender uses message key | ✅ 1/1 | — | — | ✓ assertions passed | 430.3 ms |
| TestToolCallArgKeys | db query uses query key | ✅ 1/1 | — | — | ✓ assertions passed | 405.8 ms |
| TestFinalResponse | includes model name | ✅ 1/1 | — | — | ✓ assertions passed | 467.0 ms |
| TestFinalResponse | includes tool output in summary | ✅ 1/1 | — | — | ✓ assertions passed | 376.2 ms |
| TestFinalResponse | knowledge answer when no tool results | ✅ 1/1 | — | — | ✓ assertions passed | 425.5 ms |
| TestFinalResponse | tool call id is unique across invocations | ✅ 1/1 | Each call must mint a fresh ID — never reuse a previous one. | — | ✓ assertions passed | 414.0 ms |

---

### 📁 `tests\test_pii.py`  —  23/23 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestEdgeCases | empty string returned unchanged | ✅ 1/1 | — | — | ✓ assertions passed | 404.7 ms |
| TestEdgeCases | no pii text returned unchanged | ✅ 1/1 | — | — | ✓ assertions passed | 380.7 ms |
| TestEdgeCases | already anonymized text passes through | ✅ 1/1 | — | — | ✓ assertions passed | 341.7 ms |
| TestEdgeCases | whitespace only returned unchanged | ✅ 1/1 | — | — | ✓ assertions passed | 423.2 ms |
| TestPersonAnonymization | person name replaced | ✅ 1/1 | — | — | ✓ assertions passed | 478.9 ms |
| TestPersonAnonymization | person name replaced | ✅ 1/1 | — | — | ✓ assertions passed | 429.7 ms |
| TestPersonAnonymization | person name replaced | ✅ 1/1 | — | — | ✓ assertions passed | 353.2 ms |
| TestEmailAnonymization | email replaced | ✅ 1/1 | — | — | ✓ assertions passed | 367.0 ms |
| TestEmailAnonymization | multiple emails replaced | ✅ 1/1 | — | — | ✓ assertions passed | 356.4 ms |
| TestPhoneAnonymization | us phone replaced | ✅ 1/1 | — | — | ✓ assertions passed | 374.9 ms |
| TestPhoneAnonymization | phone with country code replaced | ✅ 1/1 | — | — | ✓ assertions passed | 372.4 ms |
| TestSSNAnonymization | ssn replaced | ✅ 1/1 | — | — | ✓ assertions passed | 436.8 ms |
| TestSSNAnonymization | ssn without dashes replaced | ✅ 1/1 | — | — | ✓ assertions passed | 377.9 ms |
| TestCreditCardAnonymization | credit card replaced | ✅ 1/1 | — | — | ✓ assertions passed | 316.3 ms |
| TestCreditCardAnonymization | amex credit card replaced | ✅ 1/1 | — | — | ✓ assertions passed | 340.9 ms |
| TestIPAddressAnonymization | ipv4 replaced | ✅ 1/1 | — | — | ✓ assertions passed | 349.4 ms |
| TestIPAddressAnonymization | public ipv4 replaced | ✅ 1/1 | — | — | ✓ assertions passed | 303.9 ms |
| TestMixedPII | multiple pii types replaced | ✅ 1/1 | — | — | ✓ assertions passed | 311.4 ms |
| TestMixedPII | pii in longer paragraph | ✅ 1/1 | — | — | ✓ assertions passed | 387.8 ms |
| TestPlaceholderFormat | result is str | ✅ 1/1 | — | — | ✓ assertions passed | 347.0 ms |
| TestPlaceholderFormat | anonymized result is str | ✅ 1/1 | — | — | ✓ assertions passed | 348.7 ms |
| TestPlaceholderFormat | placeholder uses angle bracket format | ✅ 1/1 | Placeholders must be <ENTITY>, not a hash, UUID, or *** format. | — | ✓ assertions passed | 329.8 ms |
| TestPlaceholderFormat | non pii text unmodified | ✅ 1/1 | Text with no PII entities must pass through byte-for-byte. | — | ✓ assertions passed | 314.2 ms |

---

### 📁 `tests\test_rate_limit.py`  —  6/6 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| module-level | below limit returns 202 | ✅ 1/1 | First request (well within the 3/min limit) must succeed with 202. | — | ✓ assertions passed | 364.0 ms |
| module-level | exceeding limit returns 429 | ✅ 1/1 | 4th request within the same minute must be rejected with 429. | — | ✓ assertions passed | 527.9 ms |
| module-level | 429 has retry after header | ✅ 1/1 | HTTP 429 response must include a Retry-After header. | — | ✓ assertions passed | 536.7 ms |
| module-level | 429 has x ratelimit headers | ✅ 1/1 | HTTP 429 response must include X-RateLimit-Limit and X-RateLimit-Remaining. | — | ✓ assertions passed | 487.6 ms |
| module-level | tenant isolation | ✅ 1/1 | Exhausting ALPHA's quota must NOT block BETA. | ALPHA submits 4 requests (exceeds limit=3). BETA submits 1 request | ✓ assertions passed | 577.1 ms |
| module-level | read endpoints not rate limited | ✅ 1/1 | GET /agents must never return 429 regardless of how many times it's called. | Rate limiting is applied only to the run submission endpoint. | ✓ assertions passed | 389.4 ms |

---

### 📁 `tests\test_redis_url_masking.py`  —  8/8 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestRedisUrlSafe | plain url unchanged | ✅ 1/1 | — | — | ✓ assertions passed | 382.6 ms |
| TestRedisUrlSafe | url without port | ✅ 1/1 | — | — | ✓ assertions passed | 398.6 ms |
| TestRedisUrlSafe | url with username only stripped | ✅ 1/1 | — | — | ✓ assertions passed | 430.1 ms |
| TestRedisUrlSafe | url with path ignored | ✅ 1/1 | — | — | ✓ assertions passed | 364.7 ms |
| TestRedisUrlSafe | safe url never contains credentials | ✅ 1/1 | — | — | ✓ assertions passed | 386.7 ms |
| TestRedisUrlPasswordRejected | password in url raises | ✅ 1/1 | — | — | ✓ assertions passed | 372.9 ms |
| TestRedisUrlPasswordRejected | error message is descriptive | ✅ 1/1 | — | — | ✓ assertions passed | 475.9 ms |
| TestRedisUrlPasswordRejected | plain url no password accepted | ✅ 1/1 | Sanity check: a plain URL without password must NOT raise. | — | ✓ assertions passed | 378.2 ms |

---

### 📁 `tests\test_security_headers.py`  —  12/12 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestSecurityHeaders | headers on 200 | ✅ 1/1 | Security headers present on a successful 200 response. | — | ✓ assertions passed | 394.0 ms |
| TestSecurityHeaders | headers on 401 | ✅ 1/1 | Security headers present even on unauthenticated 401 responses. | — | ✓ assertions passed | 375.0 ms |
| TestSecurityHeaders | headers on 404 | ✅ 1/1 | Security headers present on 404 responses. | — | ✓ assertions passed | 332.8 ms |
| TestSecurityHeaders | x content type options value | ✅ 1/1 | X-Content-Type-Options must be exactly 'nosniff'. | — | ✓ assertions passed | 471.8 ms |
| TestSecurityHeaders | x frame options value | ✅ 1/1 | X-Frame-Options must be exactly 'DENY'. | — | ✓ assertions passed | 393.6 ms |
| TestSecurityHeaders | hsts max age | ✅ 1/1 | HSTS header must include max-age of 1 year and includeSubDomains. | — | ✓ assertions passed | 439.8 ms |
| TestSecurityHeaders | xss protection disabled | ✅ 1/1 | X-XSS-Protection must be '0' (disables the legacy filter). | — | ✓ assertions passed | 390.0 ms |
| TestCORSWildcard | cors origin echoed for any origin | ✅ 1/1 | With CORS_ALLOWED_ORIGINS=["*"], any Origin header is echoed back. | — | ✓ assertions passed | 368.0 ms |
| TestCORSWildcard | cors preflight returns security headers | ✅ 1/1 | CORS preflight OPTIONS also receives security headers. | — | ✓ assertions passed | 347.9 ms |
| TestCORSRestrictedOrigins | allowed origin gets header | ✅ 1/1 | Allowed origin receives Access-Control-Allow-Origin in response. | — | ✓ assertions passed | 314.5 ms |
| TestCORSRestrictedOrigins | disallowed origin no acao header | ✅ 1/1 | Disallowed origin does NOT receive Access-Control-Allow-Origin. | — | ✓ assertions passed | 342.0 ms |
| TestCORSRestrictedOrigins | security headers present for disallowed origin | ✅ 1/1 | Security hardening headers are present even when CORS rejects the origin. | — | ✓ assertions passed | 388.8 ms |

---

### 📁 `tests\test_tools_api.py`  —  26/26 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestAuth | missing key returns 401 | ✅ 1/1 | — | — | ✓ assertions passed | 334.9 ms |
| TestAuth | invalid key returns 401 | ✅ 1/1 | — | — | ✓ assertions passed | 331.0 ms |
| TestAuth | valid key returns 200 | ✅ 1/1 | — | — | ✓ assertions passed | 347.7 ms |
| TestToolCRUD | create returns 201 with body | ✅ 1/1 | — | — | ✓ assertions passed | 335.1 ms |
| TestToolCRUD | create empty name returns 422 | ✅ 1/1 | — | — | ✓ assertions passed | 346.5 ms |
| TestToolCRUD | create missing description returns 422 | ✅ 1/1 | — | — | ✓ assertions passed | 338.0 ms |
| TestToolCRUD | list empty by default | ✅ 1/1 | — | — | ✓ assertions passed | 331.4 ms |
| TestToolCRUD | list returns all own tools | ✅ 1/1 | — | — | ✓ assertions passed | 315.6 ms |
| TestToolCRUD | get returns correct tool | ✅ 1/1 | — | — | ✓ assertions passed | 347.1 ms |
| TestToolCRUD | get nonexistent returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 334.4 ms |
| TestToolCRUD | get malformed id returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 424.8 ms |
| TestToolCRUD | update description | ✅ 1/1 | — | — | ✓ assertions passed | 472.2 ms |
| TestToolCRUD | update does not touch omitted fields | ✅ 1/1 | — | — | ✓ assertions passed | 574.3 ms |
| TestToolCRUD | update nonexistent returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 432.6 ms |
| TestToolCRUD | delete returns 204 | ✅ 1/1 | — | — | ✓ assertions passed | 412.5 ms |
| TestToolCRUD | delete makes tool unfetchable | ✅ 1/1 | — | — | ✓ assertions passed | 380.0 ms |
| TestToolCRUD | delete nonexistent returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 357.5 ms |
| TestToolListAgentNameFilter | filter returns tools of matching agent | ✅ 1/1 | Tools linked to a matching agent are returned; unlinked tools are not. | — | ✓ assertions passed | 411.7 ms |
| TestToolListAgentNameFilter | filter is case insensitive | ✅ 1/1 | — | — | ✓ assertions passed | 451.2 ms |
| TestToolListAgentNameFilter | filter no matching agent returns empty | ✅ 1/1 | — | — | ✓ assertions passed | 375.0 ms |
| TestToolListAgentNameFilter | filter agent with no tools returns empty | ✅ 1/1 | — | — | ✓ assertions passed | 362.7 ms |
| TestToolListAgentNameFilter | filter scoped to tenant | ✅ 1/1 | BETA's agent with the same name must not expose ALPHA's tools. | — | ✓ assertions passed | 358.6 ms |
| TestTenantIsolation | tool invisible to other tenant | ✅ 1/1 | A tool created by ALPHA must not be visible to BETA. | — | ✓ assertions passed | 323.4 ms |
| TestTenantIsolation | list returns only own tools | ✅ 1/1 | BETA's list must be empty even when ALPHA has tools. | — | ✓ assertions passed | 332.8 ms |
| TestTenantIsolation | beta cannot update alpha tool | ✅ 1/1 | — | — | ✓ assertions passed | 351.2 ms |
| TestTenantIsolation | beta cannot delete alpha tool | ✅ 1/1 | — | — | ✓ assertions passed | 321.2 ms |

---

### 📁 `tests\test_tracing.py`  —  11/11 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| module-level | run agent emits agent run span | ✅ 1/1 | A completed run must produce at least one 'agent.run' span. | — | ✓ assertions passed | 450.2 ms |
| module-level | agent run span has agent id attribute | ✅ 1/1 | 'agent.run' span must carry agent.id and tenant.id attributes. | — | ✓ assertions passed | 390.1 ms |
| module-level | graph invoke span nested in agent run | ✅ 1/1 | 'agent.graph_invoke' parent span_id must equal 'agent.run' span_id. | — | ✓ assertions passed | 387.1 ms |
| module-level | run span has steps attribute | ✅ 1/1 | 'agent.run' span must carry run.steps and run.id attributes after execution. | — | ✓ assertions passed | 398.3 ms |
| module-level | no pii in span attributes | ✅ 1/1 | Task text must never appear in any span attribute value. | — | ✓ assertions passed | 464.6 ms |
| module-level | worker emits worker span | ✅ 1/1 | FakeArqPool runs the worker synchronously — worker span must be captured. | — | ✓ assertions passed | 440.6 ms |
| module-level | worker span has run and agent attributes | ✅ 1/1 | worker.run_agent_task span must carry run.id, agent.id, tenant.id. | — | ✓ assertions passed | 409.0 ms |
| module-level | trace context propagated via carrier | ✅ 1/1 | Worker span's trace_id must match the API's agent.run span trace_id. | This proves the W3C traceparent carrier was injected (agents.py) and | ✓ assertions passed | 372.3 ms |
| module-level | log contains trace id when span active | ✅ 1/1 | When a log line is emitted inside an active OTel span, the JSON output | must include a 32-char hex 'trace_id' field. | ✓ assertions passed | 345.0 ms |
| module-level | log omits trace id when no span active | ✅ 1/1 | Outside any span, _add_otel_trace_context must not inject trace_id. | — | ✓ assertions passed | 338.6 ms |
| module-level | configure tracing is idempotent | ✅ 1/1 | Calling configure_tracing() while _provider is already set must be a no-op. | The test provider installed by otel_test_provider must remain untouched. | ✓ assertions passed | 436.3 ms |

---

### 📁 `tests\test_worker.py`  —  8/8 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestWorkerSuccessPath | successful run sets completed | ✅ 1/1 | — | — | ✓ assertions passed | 500.3 ms |
| TestWorkerSuccessPath | started at set before completion | ✅ 1/1 | — | — | ✓ assertions passed | 613.4 ms |
| TestWorkerFailurePaths | prompt injection sets failed | ✅ 1/1 | A prompt injection in the task causes the worker to store status=failed. | — | ✓ assertions passed | 507.0 ms |
| TestWorkerFailurePaths | unknown exception sets failed with generic message | ✅ 1/1 | An unexpected exception from run_agent() stores a safe generic message. | — | ✓ assertions passed | 405.9 ms |
| TestWorkerFailurePaths | missing run id returns cleanly | ✅ 1/1 | Calling with a non-existent run_id logs and returns without raising. | — | ✓ assertions passed | 443.5 ms |
| TestWorkerContextVarReset | ctx reset after successful run | ✅ 1/1 | tenant_ctx returns to its prior value after a normal run. | — | ✓ assertions passed | 381.3 ms |
| TestWorkerContextVarReset | ctx reset after failed run | ✅ 1/1 | tenant_ctx returns to its prior value even when the run fails. | — | ✓ assertions passed | 382.4 ms |
| TestWorkerContextVarReset | ctx reset after missing run | ✅ 1/1 | tenant_ctx returns to its prior value when run_id does not exist (early return). | — | ✓ assertions passed | 377.5 ms |

---

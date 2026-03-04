# 🧪 Test Report

## Summary

| | |
|---|---|
| **Score** | `158 / 158` |
| **Passed** | 158 ✅ |
| **Failed** | 0 — |
| **Skipped** | 0 — |
| **Duration** | 24,263 ms |
| **Pass rate** | 100% |

## Results

### 📁 `tests/test_agents_runs_api.py`  —  48/48 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestAuth | missing key returns 401 | ✅ 1/1 | — | — | ✓ assertions passed | 3659.1 ms |
| TestAuth | invalid key returns 401 | ✅ 1/1 | — | — | ✓ assertions passed | 105.8 ms |
| TestAuth | valid key returns 200 | ✅ 1/1 | — | — | ✓ assertions passed | 204.3 ms |
| TestAgentCRUD | create without tools returns 201 | ✅ 1/1 | — | — | ✓ assertions passed | 115.4 ms |
| TestAgentCRUD | create with tools embeds tool objects | ✅ 1/1 | — | — | ✓ assertions passed | 107.4 ms |
| TestAgentCRUD | create with nonexistent tool returns 422 | ✅ 1/1 | — | — | ✓ assertions passed | 105.9 ms |
| TestAgentCRUD | create with malformed tool id returns 422 | ✅ 1/1 | — | — | ✓ assertions passed | 113.5 ms |
| TestAgentCRUD | create missing name returns 422 | ✅ 1/1 | — | — | ✓ assertions passed | 105.0 ms |
| TestAgentCRUD | list empty by default | ✅ 1/1 | — | — | ✓ assertions passed | 103.0 ms |
| TestAgentCRUD | list returns created agent | ✅ 1/1 | — | — | ✓ assertions passed | 106.5 ms |
| TestAgentCRUD | filter by tool name includes match | ✅ 1/1 | — | — | ✓ assertions passed | 121.5 ms |
| TestAgentCRUD | filter by tool name is case insensitive | ✅ 1/1 | — | — | ✓ assertions passed | 127.1 ms |
| TestAgentCRUD | filter by tool name no match returns empty | ✅ 1/1 | — | — | ✓ assertions passed | 140.5 ms |
| TestAgentCRUD | get returns correct agent | ✅ 1/1 | — | — | ✓ assertions passed | 146.7 ms |
| TestAgentCRUD | get nonexistent returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 114.4 ms |
| TestAgentCRUD | get malformed id returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 106.5 ms |
| TestAgentCRUD | update name | ✅ 1/1 | — | — | ✓ assertions passed | 109.0 ms |
| TestAgentCRUD | update does not touch omitted fields | ✅ 1/1 | — | — | ✓ assertions passed | 114.7 ms |
| TestAgentCRUD | update removes tools when empty list | ✅ 1/1 | — | — | ✓ assertions passed | 127.6 ms |
| TestAgentCRUD | update omitting tool ids leaves tools unchanged | ✅ 1/1 | — | — | ✓ assertions passed | 121.2 ms |
| TestAgentCRUD | update nonexistent returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 121.5 ms |
| TestAgentCRUD | delete returns 204 | ✅ 1/1 | — | — | ✓ assertions passed | 189.5 ms |
| TestAgentCRUD | delete makes agent unfetchable | ✅ 1/1 | — | — | ✓ assertions passed | 339.0 ms |
| TestAgentCRUD | delete nonexistent returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 120.7 ms |
| TestAgentTenantIsolation | agent invisible to other tenant | ✅ 1/1 | — | — | ✓ assertions passed | 126.3 ms |
| TestAgentTenantIsolation | list returns only own agents | ✅ 1/1 | — | — | ✓ assertions passed | 131.8 ms |
| TestAgentTenantIsolation | beta cannot update alpha agent | ✅ 1/1 | — | — | ✓ assertions passed | 125.9 ms |
| TestAgentTenantIsolation | beta cannot delete alpha agent | ✅ 1/1 | — | — | ✓ assertions passed | 134.5 ms |
| TestAgentTenantIsolation | tool from other tenant rejected | ✅ 1/1 | BETA's tool id must not be usable when creating an ALPHA agent. | — | ✓ assertions passed | 152.8 ms |
| TestAgentRun | run returns 200 with required fields | ✅ 1/1 | — | — | ✓ assertions passed | 176.9 ms |
| TestAgentRun | run with search keyword calls web search | ✅ 1/1 | — | — | ✓ assertions passed | 185.9 ms |
| TestAgentRun | run tool call record has input and output | ✅ 1/1 | — | — | ✓ assertions passed | 147.8 ms |
| TestAgentRun | run without tool keyword returns no tool calls | ✅ 1/1 | — | — | ✓ assertions passed | 142.3 ms |
| TestAgentRun | run unsupported model returns 422 | ✅ 1/1 | — | — | ✓ assertions passed | 135.6 ms |
| TestAgentRun | run prompt injection returns 400 | ✅ 1/1 | — | — | ✓ assertions passed | 147.7 ms |
| TestAgentRun | run on nonexistent agent returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 211.0 ms |
| TestAgentRunHistory | history empty before any run | ✅ 1/1 | — | — | ✓ assertions passed | 153.9 ms |
| TestAgentRunHistory | run appears in history | ✅ 1/1 | — | — | ✓ assertions passed | 149.9 ms |
| TestAgentRunHistory | pagination total and pages | ✅ 1/1 | — | — | ✓ assertions passed | 175.4 ms |
| TestAgentRunHistory | pagination last page has remainder | ✅ 1/1 | — | — | ✓ assertions passed | 185.8 ms |
| TestAgentRunHistory | history ordered most recent first | ✅ 1/1 | — | — | ✓ assertions passed | 157.6 ms |
| TestAgentRunHistory | history scoped to agent | ✅ 1/1 | Runs from agent A must not appear in agent B's history. | — | ✓ assertions passed | 193.9 ms |
| TestAgentRunHistory | history on nonexistent agent returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 119.3 ms |
| TestGlobalRunHistory | global runs empty before any run | ✅ 1/1 | — | — | ✓ assertions passed | 157.1 ms |
| TestGlobalRunHistory | global runs includes run after execution | ✅ 1/1 | — | — | ✓ assertions passed | 130.6 ms |
| TestGlobalRunHistory | global runs aggregates across agents | ✅ 1/1 | — | — | ✓ assertions passed | 175.9 ms |
| TestGlobalRunHistory | global runs scoped to tenant | ✅ 1/1 | ALPHA's runs must not appear in BETA's global history. | — | ✓ assertions passed | 121.7 ms |
| TestGlobalRunHistory | global runs pagination | ✅ 1/1 | — | — | ✓ assertions passed | 142.5 ms |

---

### 📁 `tests/test_guardrail.py`  —  61/61 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestPromptInjectionError | str includes category and matched text | ✅ 1/1 | — | — | ✓ assertions passed | 102.9 ms |
| TestPromptInjectionError | attributes accessible | ✅ 1/1 | — | — | ✓ assertions passed | 102.6 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 157.9 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 103.5 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 95.8 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 98.0 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 99.8 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 96.4 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 95.4 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 94.4 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 99.2 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 93.9 ms |
| TestSafeInputs | clean text passes | ✅ 1/1 | — | — | ✓ assertions passed | 107.8 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 129.7 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 103.7 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 94.2 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 93.0 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 144.3 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 96.1 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 95.2 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 95.3 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 94.7 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 102.0 ms |
| TestOverridePatterns | override pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 197.1 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 105.8 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 112.7 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 137.0 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 93.6 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 106.5 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 116.7 ms |
| TestExfiltrationPatterns | exfiltration pattern blocked | ✅ 1/1 | — | — | ✓ assertions passed | 101.0 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 100.1 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 103.8 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 147.7 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 93.6 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 96.4 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 106.6 ms |
| TestDelimiterInjection | delimiter injection blocked | ✅ 1/1 | — | — | ✓ assertions passed | 102.1 ms |
| TestInvisibleCharacters | invisible char blocked | ✅ 1/1 | — | — | ✓ assertions passed | 102.2 ms |
| TestInvisibleCharacters | invisible char blocked | ✅ 1/1 | — | — | ✓ assertions passed | 101.5 ms |
| TestInvisibleCharacters | invisible char blocked | ✅ 1/1 | — | — | ✓ assertions passed | 103.4 ms |
| TestInvisibleCharacters | invisible char blocked | ✅ 1/1 | — | — | ✓ assertions passed | 99.4 ms |
| TestInvisibleCharacters | invisible char blocked | ✅ 1/1 | — | — | ✓ assertions passed | 96.8 ms |
| TestHomoglyphs | known homoglyph blocked | ✅ 1/1 | — | — | ✓ assertions passed | 195.8 ms |
| TestHomoglyphs | known homoglyph blocked | ✅ 1/1 | — | — | ✓ assertions passed | 97.8 ms |
| TestHomoglyphs | known homoglyph blocked | ✅ 1/1 | — | — | ✓ assertions passed | 99.7 ms |
| TestHomoglyphs | known homoglyph blocked | ✅ 1/1 | — | — | ✓ assertions passed | 102.2 ms |
| TestHomoglyphs | legitimate accented chars pass | ✅ 1/1 | — | — | ✓ assertions passed | 98.0 ms |
| TestHomoglyphs | legitimate accented chars pass | ✅ 1/1 | — | — | ✓ assertions passed | 102.0 ms |
| TestHomoglyphs | legitimate accented chars pass | ✅ 1/1 | — | — | ✓ assertions passed | 120.3 ms |
| TestHomoglyphs | legitimate accented chars pass | ✅ 1/1 | — | — | ✓ assertions passed | 102.8 ms |
| TestBase64Encoding | encoded override payload blocked | ✅ 1/1 | — | — | ✓ assertions passed | 108.2 ms |
| TestBase64Encoding | encoded exfiltration payload blocked | ✅ 1/1 | — | — | ✓ assertions passed | 101.1 ms |
| TestBase64Encoding | clean base64 passes | ✅ 1/1 | — | — | ✓ assertions passed | 193.3 ms |
| TestBase64Encoding | short base64 like string passes | ✅ 1/1 | — | — | ✓ assertions passed | 105.7 ms |
| TestCheckToolOutput | clean output returned unchanged | ✅ 1/1 | — | — | ✓ assertions passed | 105.1 ms |
| TestCheckToolOutput | long output truncated silently | ✅ 1/1 | — | — | ✓ assertions passed | 104.4 ms |
| TestCheckToolOutput | output at exact limit not truncated | ✅ 1/1 | — | — | ✓ assertions passed | 95.0 ms |
| TestCheckToolOutput | injection in tool output raises | ✅ 1/1 | — | — | ✓ assertions passed | 96.6 ms |
| TestCheckToolOutput | injection in truncated region does not raise | ✅ 1/1 | Malicious content that falls entirely beyond MAX_TOOL_OUTPUT_LENGTH | is truncated before pattern checks run — it never reaches the regex. | ✓ assertions passed | 99.9 ms |
| TestCheckToolOutput | tool name does not affect output check | ✅ 1/1 | tool_name is metadata only; the check is purely on content. | — | ✓ assertions passed | 117.4 ms |

---

### 📁 `tests/test_mock_llm.py`  —  23/23 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestBindTools | returns new instance | ✅ 1/1 | — | — | ✓ assertions passed | 102.6 ms |
| TestBindTools | bound model has correct tool names | ✅ 1/1 | — | — | ✓ assertions passed | 97.0 ms |
| TestBindTools | original instance is unaffected | ✅ 1/1 | bind_tools must not mutate the original (model_copy deep=True). | — | ✓ assertions passed | 159.0 ms |
| TestBindTools | llm type | ✅ 1/1 | — | — | ✓ assertions passed | 101.0 ms |
| TestToolCallDecision | keyword triggers correct tool | ✅ 1/1 | — | — | ✓ assertions passed | 101.6 ms |
| TestToolCallDecision | calculator keyword | ✅ 1/1 | — | — | ✓ assertions passed | 105.6 ms |
| TestToolCallDecision | weather keyword | ✅ 1/1 | — | — | ✓ assertions passed | 100.9 ms |
| TestToolCallDecision | no tool call when no tools bound | ✅ 1/1 | Keyword present but no tools registered → straight to final answer. | — | ✓ assertions passed | 102.0 ms |
| TestToolCallDecision | no tool call when keyword absent | ✅ 1/1 | — | — | ✓ assertions passed | 109.4 ms |
| TestToolCallDecision | keyword matches but tool not bound | ✅ 1/1 | 'search' keyword matches web_search rule, but only calculator is bound. | — | ✓ assertions passed | 103.8 ms |
| TestToolCallDecision | no tool call after tool result | ✅ 1/1 | Once a ToolMessage exists in history the model must produce a final answer. | — | ✓ assertions passed | 102.6 ms |
| TestToolCallDecision | system message does not trigger tool | ✅ 1/1 | SystemMessage alone must never cause a tool call. | — | ✓ assertions passed | 160.8 ms |
| TestToolCallArgKeys | web search uses query key | ✅ 1/1 | — | — | ✓ assertions passed | 176.3 ms |
| TestToolCallArgKeys | calculator uses expression key | ✅ 1/1 | — | — | ✓ assertions passed | 108.3 ms |
| TestToolCallArgKeys | weather uses location key | ✅ 1/1 | — | — | ✓ assertions passed | 102.3 ms |
| TestToolCallArgKeys | summarizer uses text key | ✅ 1/1 | — | — | ✓ assertions passed | 102.8 ms |
| TestToolCallArgKeys | translator uses text key | ✅ 1/1 | — | — | ✓ assertions passed | 106.5 ms |
| TestToolCallArgKeys | email sender uses message key | ✅ 1/1 | — | — | ✓ assertions passed | 104.7 ms |
| TestToolCallArgKeys | db query uses query key | ✅ 1/1 | — | — | ✓ assertions passed | 107.3 ms |
| TestFinalResponse | includes model name | ✅ 1/1 | — | — | ✓ assertions passed | 105.3 ms |
| TestFinalResponse | includes tool output in summary | ✅ 1/1 | — | — | ✓ assertions passed | 102.9 ms |
| TestFinalResponse | knowledge answer when no tool results | ✅ 1/1 | — | — | ✓ assertions passed | 94.7 ms |
| TestFinalResponse | tool call id is unique across invocations | ✅ 1/1 | Each call must mint a fresh ID — never reuse a previous one. | — | ✓ assertions passed | 113.8 ms |

---

### 📁 `tests/test_tools_api.py`  —  26/26 passed

| Functionality | Test name | Score | Input | Expected output | Actual output | Time |
|---|---|:---:|---|---|---|---:|
| TestAuth | missing key returns 401 | ✅ 1/1 | — | — | ✓ assertions passed | 137.9 ms |
| TestAuth | invalid key returns 401 | ✅ 1/1 | — | — | ✓ assertions passed | 136.3 ms |
| TestAuth | valid key returns 200 | ✅ 1/1 | — | — | ✓ assertions passed | 112.2 ms |
| TestToolCRUD | create returns 201 with body | ✅ 1/1 | — | — | ✓ assertions passed | 110.8 ms |
| TestToolCRUD | create empty name returns 422 | ✅ 1/1 | — | — | ✓ assertions passed | 117.2 ms |
| TestToolCRUD | create missing description returns 422 | ✅ 1/1 | — | — | ✓ assertions passed | 109.3 ms |
| TestToolCRUD | list empty by default | ✅ 1/1 | — | — | ✓ assertions passed | 107.1 ms |
| TestToolCRUD | list returns all own tools | ✅ 1/1 | — | — | ✓ assertions passed | 119.8 ms |
| TestToolCRUD | get returns correct tool | ✅ 1/1 | — | — | ✓ assertions passed | 125.6 ms |
| TestToolCRUD | get nonexistent returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 185.0 ms |
| TestToolCRUD | get malformed id returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 109.7 ms |
| TestToolCRUD | update description | ✅ 1/1 | — | — | ✓ assertions passed | 135.3 ms |
| TestToolCRUD | update does not touch omitted fields | ✅ 1/1 | — | — | ✓ assertions passed | 116.7 ms |
| TestToolCRUD | update nonexistent returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 111.3 ms |
| TestToolCRUD | delete returns 204 | ✅ 1/1 | — | — | ✓ assertions passed | 114.9 ms |
| TestToolCRUD | delete makes tool unfetchable | ✅ 1/1 | — | — | ✓ assertions passed | 126.9 ms |
| TestToolCRUD | delete nonexistent returns 404 | ✅ 1/1 | — | — | ✓ assertions passed | 113.1 ms |
| TestToolListAgentNameFilter | filter returns tools of matching agent | ✅ 1/1 | Tools linked to a matching agent are returned; unlinked tools are not. | — | ✓ assertions passed | 129.2 ms |
| TestToolListAgentNameFilter | filter is case insensitive | ✅ 1/1 | — | — | ✓ assertions passed | 177.6 ms |
| TestToolListAgentNameFilter | filter no matching agent returns empty | ✅ 1/1 | — | — | ✓ assertions passed | 115.0 ms |
| TestToolListAgentNameFilter | filter agent with no tools returns empty | ✅ 1/1 | — | — | ✓ assertions passed | 115.1 ms |
| TestToolListAgentNameFilter | filter scoped to tenant | ✅ 1/1 | BETA's agent with the same name must not expose ALPHA's tools. | — | ✓ assertions passed | 121.1 ms |
| TestTenantIsolation | tool invisible to other tenant | ✅ 1/1 | A tool created by ALPHA must not be visible to BETA. | — | ✓ assertions passed | 114.1 ms |
| TestTenantIsolation | list returns only own tools | ✅ 1/1 | BETA's list must be empty even when ALPHA has tools. | — | ✓ assertions passed | 114.2 ms |
| TestTenantIsolation | beta cannot update alpha tool | ✅ 1/1 | — | — | ✓ assertions passed | 119.7 ms |
| TestTenantIsolation | beta cannot delete alpha tool | ✅ 1/1 | — | — | ✓ assertions passed | 119.9 ms |

---

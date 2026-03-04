"""
Deterministic mock LLM that implements LangChain's BaseChatModel interface.

Why BaseChatModel?
- LangGraph's create_react_agent expects a chat model, not a raw callable
- bind_tools() is the standard LangChain contract for tool-capable models
- Returning AIMessage(tool_calls=[...]) integrates with LangGraph's built-in
  ToolNode without any custom plumbing
"""

from __future__ import annotations

import uuid
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import PrivateAttr

# Keywords that trigger a specific tool (checked in order; first match wins)
_TRIGGER_RULES: list[tuple[str, str]] = [
    ("search",    "web_search"),
    ("web",       "web_search"),
    ("browse",    "web_search"),
    ("summarize", "summarizer"),
    ("summary",   "summarizer"),
    ("analys",    "summarizer"),  # matches "analyse" and "analyze"
    ("calculat",  "calculator"),
    ("compute",   "calculator"),
    ("math",      "calculator"),
    ("database",  "db_query"),
    ("sql",       "db_query"),
    ("translat",  "translator"),
    ("weather",   "weather"),
    ("email",     "email_sender"),
    ("send",      "email_sender"),
]

# Maps tool name → the argument key it expects.
# Keeps _generate free of nested conditionals and makes new tools trivial to add.
_TOOL_ARG_KEY: dict[str, str] = {
    "web_search":   "query",
    "weather":      "location",
    "db_query":     "query",
    "summarizer":   "text",
    "translator":   "text",
    "email_sender": "message",
    "calculator":   "expression",
}

class MockChatModel(BaseChatModel):
    """
    A deterministic mock that simulates a tool-calling LLM.

    On the first call, if the task contains a keyword matching an
    available tool, it returns a tool-call request. After tool results
    appear in the message history, it always returns a final response.
    """
    model_name: str = "mock"

    # PrivateAttr — not a Pydantic field, so it won't appear in the schema
    # or be validated. Required for mutable state that shouldn't be serialized.
    _bound_tool_names: list[str] = PrivateAttr(default_factory=list)

    def bind_tools(self, tools: list, **kwargs: Any) -> "MockChatModel":
        """
        Return a copy of the model with the given tools registered.

        LangGraph calls this during agent setup to tell the model which
        tools are available. We store just the names — enough for
        `_should_call_tool` to check availability in O(1).

        Example:
            model = MockChatModel(model_name="mock")
            #### _bound_tool_names is empty at this point: []

            bound = model.bind_tools([web_search, calculator])
            #### bound._bound_tool_names → ["web_search", "calculator"]

            #### original is unaffected (model_copy deep=True)
            #### model._bound_tool_names → []
        """
        copy = self.model_copy(deep=True)
        copy._bound_tool_names = [
            tool.name for tool in tools
        ]
        return copy
    
    def _should_call_tool(self, messages: list[BaseMessage]) -> tuple[str, str] | None:
        """
        Scan the message history and return (tool_name, task_text) if a tool
        should be invoked, or None if we should move straight to a final answer.

        Three conditions must all be true to trigger a tool call:
        1. No ToolMessage exists yet (we haven't called a tool this turn).
        2. A trigger keyword from _TRIGGER_RULES appears in the user's message text.
        3. The matched tool is in _bound_tool_names (the agent actually has it).

        Example:
            #### ── Scenario A: keyword matches a bound tool → call it ────────────
            messages = [HumanMessage(content="Search the web for AI news")]
            model._bound_tool_names = ["web_search", "calculator"]

            #### full_text = "search the web for ai news"
            #### "search" hits the first _TRIGGER_RULES entry → "web_search"
            #### "web_search" is in _bound_tool_names ✓

            result = model._should_call_tool(messages)
            #### → ("web_search", "search the web for ai news")


            #### ── Scenario B: keyword matches but tool not bound → skip ─────────
            model._bound_tool_names = ["calculator"]  # web_search not available

            result = model._should_call_tool(messages)
            #### "search" matches "web_search", but "web_search" not in bound list
            #### loop continues — no other keyword matches
            #### → None


            #### ── Scenario C: ToolMessage already present → final answer ────────
            messages = [
                HumanMessage(content="Search the web for AI news"),
                ToolMessage(content="[web-search] Found 10 results...", tool_call_id="mock-abc123"),
            ]

            result = model._should_call_tool(messages)
            #### already_called = True → returns None immediately
            #### → None
        """
        already_called = any(isinstance(message, ToolMessage) for message in messages)

        if already_called:
            return None

        full_text = " ".join(
            message.content for message in messages 
            if isinstance(message, HumanMessage) and isinstance(message.content, str)
        ).lower()

        for keyword, tool_name in _TRIGGER_RULES:
            if keyword in full_text and tool_name in self._bound_tool_names:
                return tool_name, full_text[:200]
            
        return None
    
    def _generate(self, 
                  messages: list[BaseMessage],
                  stop: list[str] | None = None,
                  run_manager: Any = None,
                  **kwargs: Any
    ) -> ChatResult:
        """
        Core LangChain hook — called by LangGraph on every agent step.
        Delegates to `_should_call_tool` to decide between two response types:
        a tool-call request or a final answer.

        Example:
            #### ── Scenario A: first step, keyword triggers a tool call ──────────
            messages = [HumanMessage(content="Search the web for AI news")]
            model._bound_tool_names = ["web_search"]

            result = model._generate(messages)
            #### _should_call_tool → ("web_search", "search the web for ai news")
            #### arg_key = _TOOL_ARG_KEY["web_search"] → "query"

            #### OUTPUT
            ChatResult(generations=[ChatGeneration(message=
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "web_search",
                        "args": {"query": "search the web for ai news"},
                        "id":   "mock-a1b2c3d4",
                        "type": "tool_call",
                    }]
                )
            )])


            #### ── Scenario B: tool result present → synthesise final answer ─────
            messages = [
                HumanMessage(content="Search the web for AI news"),
                ToolMessage(
                    content="[web-search] Found 10 results for 'search the web for ai news'.",
                    tool_call_id="mock-a1b2c3d4",
                ),
            ]

            result = model._generate(messages)
            #### _should_call_tool → None (ToolMessage already present)
            #### tool_results = ["[web-search] Found 10 results..."]
            #### task = "Search the web for AI news"

            #### OUTPUT
            ChatResult(generations=[ChatGeneration(message=
                AIMessage(content=(
                    "[mock] Task complete: 'Search the web for AI news'. "
                    "Tools returned: [web-search] Found 10 results.... "
                    "Result: operation was carried out successfully and data has been synthesized."
                ))
            )])


            #### ── Scenario C: no keyword, no tool results → knowledge answer ────
            messages = [HumanMessage(content="What is the capital of France?")]
            model._bound_tool_names = ["web_search"]

            result = model._generate(messages)
            #### _should_call_tool → None (no keyword match)
            #### tool_results = []
            #### task = "What is the capital of France?"

            #### OUTPUT
            ChatResult(generations=[ChatGeneration(message=
                AIMessage(content=(
                    "[mock] Task evaluated: 'What is the capital of France?'. "
                    "Result: comprehensive response generated from the agent's knowledge and role."
                ))
            )])
        """
        result = self._should_call_tool(messages)

        if result:
            tool_name, task_text = result
            arg_key = _TOOL_ARG_KEY.get(tool_name, "query")
            ai_message = AIMessage(
                content="",
                tool_calls=[{
                    "name": tool_name,
                    "args": {arg_key: task_text},
                    "id": f"mock-{uuid.uuid4().hex[:8]}",
                    "type": "tool_call",
                }],
            )
        else:
            tool_results = [
                message.content for message in messages if isinstance(message, ToolMessage)
            ]

            task = next(
                (message.content for message in messages if hasattr(message, "type") and message.type == "human"),
                "your task"
            )

            if isinstance(task, list):
                task = str(task)

            if tool_results:
                summary = "; ".join(str(result)[:80] for result in tool_results)
                content = (
                    f"[{self.model_name}] Task complete: \"{task}\". "
                    f"Tools returned: {summary}. "
                    "Result: operation was carried out successfully and data has been synthesized."
                )
            else:
                content = (
                    f"[{self.model_name}] Task evaluated: \"{task}\". "
                    "Result: comprehensive response generated from the agent's knowledge and role."
                )

            ai_message = AIMessage(content=content)

        return ChatResult(generations=[ChatGeneration(message=ai_message)])
    
    @property
    def _llm_type(self) -> str:
        return "mock"
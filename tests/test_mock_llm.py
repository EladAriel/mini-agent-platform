"""Unit tests for MockChatModel — no DB or HTTP needed."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatGeneration

from app.services.runner.mock_llm import MockChatModel
from app.services.runner.tools import ALL_TOOLS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def invoke(model: MockChatModel, *messages) -> AIMessage:
    """Call _generate and return the unwrapped AIMessage."""
    result = model._generate(list(messages))
    gen = result.generations[0]
    assert isinstance(gen, ChatGeneration)
    assert isinstance(gen.message, AIMessage)
    return gen.message


def bound(*tool_names: str) -> MockChatModel:
    """Return a MockChatModel pre-bound to the named tools."""
    return MockChatModel().bind_tools([ALL_TOOLS[n] for n in tool_names])


# ---------------------------------------------------------------------------
# bind_tools
# ---------------------------------------------------------------------------

class TestBindTools:

    def test_returns_new_instance(self):
        model = MockChatModel()
        bound_model = model.bind_tools([ALL_TOOLS["web_search"]])
        assert bound_model is not model

    def test_bound_model_has_correct_tool_names(self):
        bound_model = bound("web_search", "calculator")
        assert set(bound_model._bound_tool_names) == {"web_search", "calculator"}

    def test_original_instance_is_unaffected(self):
        """bind_tools must not mutate the original (model_copy deep=True)."""
        model = MockChatModel()
        model.bind_tools([ALL_TOOLS["web_search"]])
        assert model._bound_tool_names == []

    def test_llm_type(self):
        assert MockChatModel()._llm_type == "mock"


# ---------------------------------------------------------------------------
# Tool-call decision
# ---------------------------------------------------------------------------

class TestToolCallDecision:

    def test_keyword_triggers_correct_tool(self):
        msg = invoke(bound("web_search"), HumanMessage(content="Search for AI trends."))
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0]["name"] == "web_search"

    def test_calculator_keyword(self):
        msg = invoke(bound("calculator"), HumanMessage(content="Calculate the total."))
        assert msg.tool_calls[0]["name"] == "calculator"

    def test_weather_keyword(self):
        msg = invoke(bound("weather"), HumanMessage(content="What is the weather in Paris?"))
        assert msg.tool_calls[0]["name"] == "weather"

    def test_no_tool_call_when_no_tools_bound(self):
        """Keyword present but no tools registered → straight to final answer."""
        msg = invoke(MockChatModel(), HumanMessage(content="Search for something."))
        assert not msg.tool_calls
        assert msg.content

    def test_no_tool_call_when_keyword_absent(self):
        msg = invoke(bound("web_search"), HumanMessage(content="Write a haiku about mountains."))
        assert not msg.tool_calls

    def test_keyword_matches_but_tool_not_bound(self):
        """'search' keyword matches web_search rule, but only calculator is bound."""
        msg = invoke(bound("calculator"), HumanMessage(content="Search for the weather."))
        assert not msg.tool_calls

    def test_no_tool_call_after_tool_result(self):
        """Once a ToolMessage exists in history the model must produce a final answer."""
        tool_msg = ToolMessage(
            content="result", tool_call_id="mock-001", name="web_search"
        )
        msg = invoke(
            bound("web_search"),
            HumanMessage(content="Search for AI."),
            tool_msg,
        )
        assert not msg.tool_calls
        assert msg.content

    def test_system_message_does_not_trigger_tool(self):
        """SystemMessage alone must never cause a tool call."""
        msg = invoke(
            bound("web_search"),
            SystemMessage(content="You are a helpful assistant."),
        )
        assert not msg.tool_calls


# ---------------------------------------------------------------------------
# Tool-call argument keys
# ---------------------------------------------------------------------------

class TestToolCallArgKeys:
    """
    Each tool expects a specific argument key in its schema.
    Passing the wrong key causes a runtime TypeError when the tool executes.
    """

    def _arg_key(self, tool_name: str, keyword: str) -> str:
        msg = invoke(bound(tool_name), HumanMessage(content=keyword))
        assert msg.tool_calls, f"Expected a tool call for keyword '{keyword}'"
        args = msg.tool_calls[0]["args"]
        assert len(args) == 1, f"Expected exactly one arg, got {args}"
        return next(iter(args))

    def test_web_search_uses_query_key(self):
        assert self._arg_key("web_search", "search for news") == "query"

    def test_calculator_uses_expression_key(self):
        assert self._arg_key("calculator", "calculate 2+2") == "expression"

    def test_weather_uses_location_key(self):
        assert self._arg_key("weather", "weather in London") == "location"

    def test_summarizer_uses_text_key(self):
        assert self._arg_key("summarizer", "summarize this report") == "text"

    def test_translator_uses_text_key(self):
        assert self._arg_key("translator", "translate this sentence") == "text"

    def test_email_sender_uses_message_key(self):
        assert self._arg_key("email_sender", "send an email to the team") == "message"

    def test_db_query_uses_query_key(self):
        assert self._arg_key("db_query", "database records for Q3") == "query"


# ---------------------------------------------------------------------------
# Final response content
# ---------------------------------------------------------------------------

class TestFinalResponse:

    def test_includes_model_name(self):
        msg = invoke(MockChatModel(model_name="gpt-4o"), HumanMessage(content="Hello."))
        assert "gpt-4o" in msg.content

    def test_includes_tool_output_in_summary(self):
        tool_msg = ToolMessage(
            content="some data found", tool_call_id="mock-001", name="web_search"
        )
        msg = invoke(MockChatModel(), HumanMessage(content="Search."), tool_msg)
        assert "some data found" in msg.content

    def test_knowledge_answer_when_no_tool_results(self):
        msg = invoke(MockChatModel(), HumanMessage(content="What is 2 + 2?"))
        assert not msg.tool_calls
        assert "knowledge" in msg.content or "evaluated" in msg.content

    def test_tool_call_id_is_unique_across_invocations(self):
        """Each call must mint a fresh ID — never reuse a previous one."""
        model = bound("web_search")
        human = HumanMessage(content="Search for cats.")
        id1 = invoke(model, human).tool_calls[0]["id"]
        id2 = invoke(model, human).tool_calls[0]["id"]
        assert id1 != id2
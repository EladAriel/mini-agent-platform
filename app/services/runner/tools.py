"""
Mock tool implementations using LangChain's @tool decorator.
"""

from langchain_core.tools import BaseTool, tool

@tool(parse_docstring=True)
def web_search(query: str) -> str:
    """
    Search the web for up-to-date information on any topic.

    Args:
        query: The search query to look up (e.g. 'latest AI news 2024').
    """
    return f"[web-search] Found 10 results for '{query}'. Top: Example Domain — a representative placeholder result."

@tool(parse_docstring=True)
def summarizer(text: str) -> str:
    """
    Summarise a body of text, extracting the key points.

    Args:
        text: The full text to summarise.
    """
    return f"[summarizer] Key points from '{text[:60]}...': topic is relevant, data is structured, conclusions are actionable."

@tool(parse_docstring=True)
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression and return the result.

    Args:
        expression: A valid mathematical expression (e.g. '(4 + 5) * 3').
    """
    return f"[calculator] Result for '{expression}': 42 (mock numeric output)."

@tool(parse_docstring=True)
def db_query(query: str) -> str:
    """
    Run a read-only database query and return matching records.

    Args:
        query: The query string or filter description to run against the database.
    """
    return f"[db-query] Query '{query[:60]}' returned 5 rows of mock data."

@tool(parse_docstring=True)
def translator(text: str) -> str:
    """
    Translate text into the requested target language.

    Args:
        text: The text to translate, prefixed with the target language (e.g. 'French: Hello world').
    """
    return f"[translator] Translation of '{text[:60]}': (mock output in target language)."

@tool(parse_docstring=True)
def weather(location: str) -> str:
    """
    Get the current weather for a given location.

    Args:
        location: The city or region to get weather for (e.g. 'London, UK').
    """
    return f"[weather] {location}: 22°C, partly cloudy, humidity 60%."

@tool(parse_docstring=True)
def email_sender(message: str) -> str:
    """
    Draft or send an email with the provided message content.

    Args:
        message: The full email body to draft or send.
    """
    return f"[email-sender] Message '{message[:60]}' has been drafted and sent successfully."

# Registry: tool name → LangChain tool object.
# Centralised here so the executor can look up tools by name in O(1).
ALL_TOOLS: dict[str, BaseTool] = {
    tool.name: tool for tool in [
        web_search,
        summarizer,
        calculator,
        db_query,
        translator,
        weather,
        email_sender,
    ]
}
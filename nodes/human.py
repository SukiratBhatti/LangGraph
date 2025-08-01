from langgraph.types import Command, interrupt
from langchain_core.tools import tool

@tool
def human_assistance(query: str) -> str:
    """Request human assistance for a specific query or task."""
    # Use interrupt to request human input
    human_response = interrupt({"query": query})
    return human_response["data"]


    
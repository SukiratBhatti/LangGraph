import os 
import json
# os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode, tools_condition

from nodes.human import human_assistance # for human assistance

# Initialize tools - following official documentation
tool = TavilySearch(max_results=2)
tools = [tool, human_assistance]

# Use official LangGraph ToolNode
tool_node = ToolNode(tools=tools)

# Use official LangGraph tools_condition for routing
route_tools = tools_condition

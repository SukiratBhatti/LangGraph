import os 
import json
# os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

from langchain_tavily import TavilySearch
from langchain_core.messages import ToolMessage
from langgraph.graph import END

from nodes.human import human_assistance # for human assistance

# Initialize tools
tool = TavilySearch(max_results=2)
tools = [tool, human_assistance]

class BasicToolNode:
    # node that runs tools requested in last message
    def __init__(self, tools:list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs:dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No messages found in input")
        
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call['name'],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

# Create tool node instance
tool_node = BasicToolNode(tools=tools)

# Routing function for conditional edges
def route_tools(state):
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No msgs found in input state to tool_edge: {state}")
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END

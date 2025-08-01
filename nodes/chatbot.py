from langchain.chat_models import init_chat_model
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

# Define state type
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Set up model
llm = init_chat_model("anthropic:claude-3-5-sonnet-20240620")

# Chatbot node function
def chatbot_node(state: State, llm_with_tools=None):
    # Claude internally decides if tools are needed, otehrwise provide answer via training.

    model = llm_with_tools if llm_with_tools else llm
    return {"messages": [model.invoke(state["messages"])]}

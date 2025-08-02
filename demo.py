# alternative to main.py due to not caring about customize state.

import os
from typing import Annotated

from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize LLM
llm = init_chat_model("anthropic:claude-3-5-sonnet-20240620")

class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    birthday: str

@tool
def human_assistance(
    name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """Request assistance from a human."""
    human_response = interrupt(
        {
            "question": "Is this correct?",
            "name": name,
            "birthday": birthday,
        },
    )
    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"

    state_update = {
        "name": verified_name,
        "birthday": verified_birthday,
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
    }
    return Command(update=state_update)

tool = TavilySearch(max_results=2)
tools = [tool, human_assistance]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    assert(len(message.tool_calls) <= 1)
    return {"messages": [message]}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# Configuration
config = {"configurable": {"thread_id": "1"}}

# Main execution - following the official documentation exactly
if __name__ == "__main__":
    print("LangGraph Demo - Testing Time Travel Feature")
    print("=" * 50)
    
    # Step 1: Build up state history with multiple interactions
    print("\nStep 1: Building state history...")
    
    # First interaction
    print("\n--- First Interaction ---")
    user_input1 = "Hello, can you tell me about LangGraph?"
    print(f"User: {user_input1}")
    
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input1}]},
        config,
        stream_mode="values",
    )
    
    for event in events:
        if "messages" in event:
            last_msg = event["messages"][-1]
            if hasattr(last_msg, 'content') and last_msg.content:
                print(f"Assistant: {last_msg.content}")
    
    # Second interaction
    print("\n--- Second Interaction ---")
    user_input2 = "Can you look up when LangGraph was released? When you have the answer, use the human_assistance tool for review."
    print(f"User: {user_input2}")
    
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input2}]},
        config,
        stream_mode="values",
    )
    
    for event in events:
        if "messages" in event:
            last_msg = event["messages"][-1]
            if hasattr(last_msg, 'content') and last_msg.content:
                print(f"Assistant: {last_msg.content}")
    
    # Handle interrupt if needed
    snapshot = graph.get_state(config)
    if snapshot.next == ("tools",):
        print("\nHandling interrupt...")
        human_command = Command(
            resume={
                "name": "LangGraph",
                "birthday": "Jan 17, 2024",
            },
        )
        
        events = graph.stream(human_command, config, stream_mode="values")
        for event in events:
            if "messages" in event:
                last_msg = event["messages"][-1]
                if hasattr(last_msg, 'content') and last_msg.content:
                    print(f"Assistant: {last_msg.content}")
    
    # Third interaction
    print("\n--- Third Interaction ---")
    user_input3 = "What are the main features of LangGraph?"
    print(f"User: {user_input3}")
    
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input3}]},
        config,
        stream_mode="values",
    )
    
    for event in events:
        if "messages" in event:
            last_msg = event["messages"][-1]
            if hasattr(last_msg, 'content') and last_msg.content:
                print(f"Assistant: {last_msg.content}")
    
    # Step 2: Demonstrate Time Travel
    print("\n" + "="*50)
    print("Step 2: Time Travel Demonstration")
    print("="*50)
    
    print("\nFull State History:")
    print("-" * 30)
    
    # Show all checkpoints
    for i, state in enumerate(graph.get_state_history(config)):
        print(f"Checkpoint {i}: Messages: {len(state.values['messages'])}, Next: {state.next}")
        if 'name' in state.values and 'birthday' in state.values:
            print(f"  State: name='{state.values['name']}', birthday='{state.values['birthday']}'")
        print()
    
    # Find a specific checkpoint to replay from
    print("Finding checkpoint to replay from...")
    to_replay = None
    for state in graph.get_state_history(config):
        if len(state.values["messages"]) == 4:  # After first interaction
            to_replay = state
            print(f"Selected checkpoint with {len(state.values['messages'])} messages")
            break
    
    if to_replay:
        print(f"\nReplaying from checkpoint: {to_replay.config}")
        print("This will resume execution from that point in time...")
        print("-" * 50)
        
        # Replay from the selected checkpoint
        for event in graph.stream(None, to_replay.config, stream_mode="values"):
            if "messages" in event:
                last_msg = event["messages"][-1]
                if hasattr(last_msg, 'content') and last_msg.content:
                    print(f"Assistant: {last_msg.content}")
    
    print("\n" + "="*50)
    print("Time Travel Demo Completed!")
    print("="*50)
    
    # Show final state
    final_snapshot = graph.get_state(config)
    print(f"Final state - Messages: {len(final_snapshot.values['messages'])}")
    if 'name' in final_snapshot.values and 'birthday' in final_snapshot.values:
        print(f"Final state - Name: {final_snapshot.values['name']}, Birthday: {final_snapshot.values['birthday']}")
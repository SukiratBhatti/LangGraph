"""
LangGraph Chatbot - Following Official Documentation

This chatbot follows the official LangGraph documentation pattern:
1. Basic chatbot with tools
2. Memory/checkpointing
3. Human-in-the-loop functionality
4. Simple interaction loop
"""

import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
import re # for transcripts

# Load environment variables
load_dotenv()

# Import node definitions
from nodes.chatbot import State, chatbot_node, llm
from nodes.tools import tool_node, tools, route_tools
from nodes.memory import config, memory
from nodes.human import Command, interrupt

# Bind tools to the chatbot model
llm_with_tools = llm.bind_tools(tools)

# Create graph - following official documentation exactly
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("chatbot", lambda state: chatbot_node(state, llm_with_tools))
graph_builder.add_node("tools", tool_node)

# Wire the graph - following official documentation
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
)
graph_builder.add_edge("tools", "chatbot")

# Compile the graph
graph = graph_builder.compile(checkpointer=memory)

# Main interaction loop - following official documentation
transcript_lines = []

while True:
    try:
        # Check if we're waiting for human input (interrupt state)
        snapshot = graph.get_state(config)
        next_node = snapshot.next

        # Case 1: waiting for human tool via interrupt
        if next_node == ("tools",):
            print("\n🤖 Assistant is requesting human assistance...")
            
            # Check if this is a human_assistance tool call
            messages = snapshot.values.get("messages", [])
            if messages and hasattr(messages[-1], 'tool_calls'):
                tool_calls = messages[-1].tool_calls
                for tool_call in tool_calls:
                    if tool_call.get("name") == "human_assistance":
                        query = tool_call.get("args", {}).get("query", "Please provide assistance")
                        print(f"🤖 Assistant asks: {query}")
                        break

            human_input = input("👤 Human response: ")
            command = Command(resume={"data": human_input})
            transcript_lines.append(f"Human (assistance): {human_input}")

            events = graph.stream(command, config, stream_mode="values")

        # Case 2: standard human input
        else: 
            user_input = input("👤 User: ")
            if user_input.lower() in ["quit", "q", "exit"]:
                print("🤖 Assistant going offline.")
                
                # Save final transcript
                if transcript_lines:
                    os.makedirs("transcripts", exist_ok=True)
                    filename = re.sub(r"[^\w\d\-_. ]", "", transcript_lines[0])[:40].strip().replace(" ", "_")
                    filepath = f"transcripts/{filename}.txt"
                    with open(filepath, "w") as f:
                        f.write("\n".join(transcript_lines))
                break

            # Add user input to transcript
            transcript_lines.append(f"User: {user_input}")

            # Stream response - following official documentation exactly
            events = graph.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config,
                stream_mode="values",
            )

        # Process events - following official documentation
        for event in events:
            if "messages" in event:
                last_msg = event["messages"][-1]
                if hasattr(last_msg, 'content') and last_msg.content:
                    print(f"\n🤖 Assistant: {last_msg.content}")
                    transcript_lines.append(f"Assistant: {last_msg.content}")

    except Exception as e:
        print(f"❌ Error: {e}")
        break

# Generate graph visualization
graph_bytes = graph.get_graph().draw_mermaid_png()

with open("graph.png", "wb") as f:
    f.write(graph_bytes)

print("Graph saved to graph.png")
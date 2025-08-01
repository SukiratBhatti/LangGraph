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

# Bind tools to the chatbot model
llm_with_tools = llm.bind_tools(tools)

# Create graph
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("chatbot", lambda state: chatbot_node(state, llm_with_tools))
graph_builder.add_node("tools", tool_node)

# Wire the graph
graph_builder.add_edge(START, "chatbot")

# Conditional routing to tools
graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    {"tools": "tools", END: END}
)

graph_builder.add_edge("tools", "chatbot")

# Compile the graph
graph = graph_builder.compile()

# Stream function
def stream_graph_updates(user_input: str):

    os.makedirs("transcripts", exist_ok=True)
    transcript_lines = [f"User: {user_input}"]

    for event in graph.stream({
        "messages": [
            {"role": "system", "content": "You are an assistant who can use tools to search up information."},
            {"role": "user", "content": user_input}
            ]
        }):
        for value in event.values():
            ai_message = value["messages"][-1].content
            print("Assistant:", value["messages"][-1].content)
            transcript_lines.append(f"Assistant: {ai_message}")

    filename = re.sub(r"[^\w\d\-_. ]", "", user_input)[:40].strip().replace(" ", "_")
    filepath = f"transcripts/{filename}.txt"
    
    with open(filepath, "w") as f:
        f.write("\n".join(transcript_lines))

# Main interaction loop
while True:
    try:
        user_input = input("user: ")
        if user_input.lower() in ["quit", "q", "no"]:
            print("Jarvis going offline.")
            break
        stream_graph_updates(user_input)
    except:
        user_input = "How does this robot work?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break

# Generate graph visualization
graph_bytes = graph.get_graph().draw_mermaid_png()

with open("graph.png", "wb") as f:
    f.write(graph_bytes)

print("Graph saved to graph.png")
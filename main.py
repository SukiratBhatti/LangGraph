import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
import re # for transcripts
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage


# Load environment variables
load_dotenv()

# Import node definitions
from nodes import human
from nodes.chatbot import State, chatbot_node, llm
from nodes.tools import tool_node, tools, route_tools
from nodes.memory import config, memory
from nodes.human import Command, interrupt


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
graph = graph_builder.compile(checkpointer=memory)

# Main interaction loop
transcript_lines = []  # <- Accumulate whole transcript here

while True:
    try:

        snapshot = graph.get_state(config)
        next_node = snapshot.next


        #case 1: waiting for human tool via interrupt
        if next_node == ("tools",):
            print("Waiting for human to resume tool")

            human_input = input("Human (tool response): ")
            command = Command(resume={"data":human_input})
            transcript_lines.append(f"Human: {human_input}")

            events = graph.stream(command, config, stream_mode="values")


        #case 2: standrad human input
        else: 
            user_input = input("User: ")
            if user_input.lower() in ["quit", "q", "no"]:
                print("Jarvis going offline.")

                # Save final transcript
                os.makedirs("transcripts", exist_ok=True)
                filename = re.sub(r"[^\w\d\-_. ]", "", transcript_lines[0])[:40].strip().replace(" ", "_")
                filepath = f"transcripts/{filename}.txt"
                with open(filepath, "w") as f:
                    f.write("\n".join(transcript_lines))
                break

            # Add user input to transcript
            transcript_lines.append(f"User: {user_input}")

            # Stream response and append to transcript
            events = graph.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config,
                stream_mode="values",
            )

        # shared msg handling:
        for event in events:
            # print("\n🔍 Raw event:")
            # print(event)
            if "messages" in event:
                last_msg = event["messages"][-1]
                if last_msg.type == "text":
                    print("\n 🧠 Assistant:", last_msg.content)
                    transcript_lines.append(f"Assistant: {last_msg.content}")
                    found_assistant_response = True
                # if isinstance(last_msg, AIMessage):
                #     content = last_msg.content
                #     print("Assistant:")


    except Exception as e:
        print("Error:", e)
        break


snapshot = graph.get_state(config)
if snapshot.next == ("tools",):
    print("⏸️  Paused: waiting for human input. Run help.py to resume.")
    exit()


# viewing full memory for debugging purposes:
# print("\n 🧠 Current Memory")
# if "messages" in snapshot.values:
#     for m in snapshot.values["messages"]:
#         print(f"{m.__class__.__name__}: {m.content}")
# else:
#     print("NO msgs found in state.")
#     print("full snapshot vlaues:", snapshot.values)

# Generate graph visualization
graph_bytes = graph.get_graph().draw_mermaid_png()

with open("graph.png", "wb") as f:
    f.write(graph_bytes)

print("Graph saved to graph.png")
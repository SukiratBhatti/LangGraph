import os
from langchain.chat_models import init_chat_model

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from IPython.display import Image, display

from dotenv import load_dotenv
load_dotenv()
# os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

#1. define state
class State(TypedDict):
    # messages appended to list via add_messages
    messages: Annotated[list, add_messages]

#2. create graph
graph_builder = StateGraph(State)

#3. set up model
llm = init_chat_model("anthropic:claude-3-5-sonnet-20240620")

# 4. add chatbot node (intersection)
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)


#5. add + exit entries before compiling
graph_builder.add_edge(START, "chatbot")

graph_builder.add_edge("chatbot", END)


#6. compile since nodes + edges are done.
graph = graph_builder.compile()

#7. run test:

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content":user_input}]}):
        for value in event.values():
            print("Assistant", value["messages"][-1].content)

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


# 8. create chart
graph_bytes = graph.get_graph().draw_mermaid_png()

with open("graph.png", "wb") as f:
    f.write(graph_bytes)

print("✅ Graph saved to graph.png")

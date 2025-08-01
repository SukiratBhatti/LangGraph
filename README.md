## Langgraph Demo

# 2 branches:
main: basic chatbot with tool capabilty
memory: chatbot with short term memory. human in the loop to be added, soon.

# project structure:

```
LangGraph/
├── main.py                    # Main application with LangGraph workflow
│   ├── Graph orchestration    # StateGraph setup and compilation
│   ├── Main interaction loop  # Handles user input and tool interrupts
│   ├── Transcript logging     # Saves conversations to transcripts/
│   └── Graph visualization    # Generates graph.png
│
├── nodes/
│   ├── chatbot.py            # Chatbot node with Claude 3.5 Sonnet
│   │   ├── State definition  # TypedDict for message history
│   │   ├── LLM setup         # init_chat_model with tools binding
│   │   └── Node function     # Processes messages and decides tool usage
│   │
│   ├── tools.py              # Tool handling and routing logic
│   │   ├── Tool definitions  # TavilySearch + human_assistance
│   │   ├── BasicToolNode     # Executes tool calls from AI
│   │   └── route_tools       # Conditional routing function
│   │
│   ├── human.py              # Human assistance tool
│   │   ├── interrupt usage   # LangGraph interrupt mechanism
│   │   └── @tool decorator   # Makes function available to LLM
│   │
│   └── memory.py             # Memory/checkpointing configuration
│       ├── InMemorySaver     # RAM-based memory storage
│       └── Thread config     # Configurable thread IDs
│
├── requirements.txt          # Python dependencies
│   ├── langchain            # Core LangChain framework
│   ├── langgraph            # Graph orchestration
│   ├── anthropic            # Claude API client
│   ├── langchain-tavily     # Web search integration
│   └── python-dotenv        # Environment variable loading
│
├── transcripts/             # Conversation storage
│   └── *.txt               # Auto-generated transcript files
│
├── .env                     # Environment variables (not tracked)
├── .gitignore              # Git exclusions
└── graph.png               # Generated graph visualization
```

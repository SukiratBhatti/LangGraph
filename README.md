# LangGraph Chatbot with Human-in-the-Loop

A conversational AI chatbot built with LangGraph that supports tools, memory, and human assistance.

## Features

- **Basic Chatbot**: Claude 3.5 Sonnet integration
- **Tool Integration**: Web search via Tavily
- **Memory/Checkpointing**: Persistent conversation state
- **Human-in-the-Loop**: Request human assistance via interrupts
- **Transcript Logging**: Automatic conversation storage

## Project Structure

```
LangGraph/
├── main.py                    # Main application with LangGraph workflow
├── nodes/
│   ├── chatbot.py            # Chatbot node with Claude 3.5 Sonnet
│   ├── tools.py              # Tool handling and routing logic
│   ├── human.py              # Human assistance tool with interrupts
│   └── memory.py             # Memory/checkpointing configuration
├── requirements.txt          # Python dependencies
├── transcripts/             # Conversation storage
├── .env                     # Environment variables
└── graph.png               # Generated graph visualization
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables in `.env`:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   TAVILY_API_KEY=your_tavily_key_here
   ```

3. Run the chatbot:
   ```bash
   python main.py
   ```

## Usage

- **Normal Chat**: Type your message and get AI responses
- **Human Assistance**: Ask the AI to request human help (e.g., "Can you ask a human to help me find my phone?")
- **Exit**: Type `quit`, `q`, or `exit` to end the session

## Architecture

- **StateGraph**: Manages conversation flow and state
- **ToolNode**: Handles tool execution including human assistance
- **InMemorySaver**: Provides conversation memory across sessions
- **Interrupt Mechanism**: Pauses execution for human input when needed

## Dependencies

- langchain: Core framework
- langgraph: Graph orchestration
- anthropic: Claude API client
- langchain-tavily: Web search integration
- python-dotenv: Environment management

# LangGraph Chatbot with Human-in-the-Loop and Time Travel

A conversational AI chatbot built with LangGraph that supports tools, memory, human assistance, and time travel capabilities.

## Features

- **Basic Chatbot**: Claude 3.5 Sonnet integration
- **Tool Integration**: Web search via Tavily
- **Memory/Checkpointing**: Persistent conversation state
- **Human-in-the-Loop**: Request human assistance via interrupts
- **Custom State Management**: Name and birthday fields with state updates
- **Time Travel**: Rewind and replay from any previous checkpoint
- **Transcript Logging**: Automatic conversation storage

## Project Structure

```
LangGraph/
├── main.py                    # Main application with human-in-the-loop
├── demo.py                    # got bored --> Time travel demonstration
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

3. Run the applications:
   ```bash
   python main.py      # Interactive chatbot with human assistance
   python demo.py      # Time travel demonstration
   ```

## Usage

### Main Application (main.py)
- **Normal Chat**: Type your message and get AI responses
- **Human Assistance**: Ask the AI to request human help
- **Exit**: Type `quit`, `q`, or `exit` to end the session

### Time Travel Demo (demo.py)
- Builds conversation history with multiple interactions
- Demonstrates checkpointing and state persistence
- Shows time travel capability to replay from any checkpoint

## Architecture

- **StateGraph**: Manages conversation flow and state
- **ToolNode**: Handles tool execution including human assistance
- **InMemorySaver**: Provides conversation memory across sessions
- **Interrupt Mechanism**: Pauses execution for human input when needed
- **Checkpointing**: Automatic state persistence for time travel
- **Custom State**: Name and birthday fields with Command updates

## Dependencies

- langchain: Core framework
- langgraph: Graph orchestration and time travel
- anthropic: Claude API client
- langchain-tavily: Web search integration
- python-dotenv: Environment management

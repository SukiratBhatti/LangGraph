from langgraph.checkpoint.memory import InMemorySaver

#change to SQLite/postgres in production
memory = InMemorySaver()

config = {"configurable": {"thread_id": "1"}}
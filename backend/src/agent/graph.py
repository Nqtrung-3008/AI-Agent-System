from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition

from backend.src.agent.state import AgentState
from backend.src.agent.chatbot_node import chatbot_node
from backend.src.agent.nodes import tools_node

builder = StateGraph(AgentState)

builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", tools_node)
builder.add_edge(START, "chatbot")
builder.add_conditional_edges(
    "chatbot",
    tools_condition
)
builder.add_edge("tools", "chatbot")

graph = builder.compile()
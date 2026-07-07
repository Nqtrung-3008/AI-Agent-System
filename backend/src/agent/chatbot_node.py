# agent/chatbot_node.py

from backend.src.agent.state import AgentState
from backend.src.agent.nodes import tools
from backend.src.agent.prompt import SYSTEM_PROMPT
from backend.src.llm.client import llm

from langchain_core.messages import SystemMessage

llm_with_tools = llm.bind_tools(tools)


async def chatbot_node(state: AgentState):

    response = await llm_with_tools.ainvoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]
    )

    return {
        "messages": [response]
    }
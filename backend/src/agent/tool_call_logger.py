import json
from sqlmodel.ext.asyncio.session import AsyncSession
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage
from backend.src.schemas.schemas import ToolCallCreate
from backend.src.services import tool_call_services

def get_context(config: RunnableConfig):
    configurable = config.get("configurable", {})
    user_id = configurable.get("user_id")
    conversation_id = configurable.get("conversation_id")
    session = configurable.get("session")

    if user_id is None or conversation_id is None or session is None:
        raise ValueError("Agent tool context requires user_id, conversation_id and session")
    return user_id, conversation_id, session

def to_json_string(value):
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except TypeError:
        return str(value)

async def save_tool_calls_from_messages(messages, conversation_id: int, session: AsyncSession):
    pending = {}

    for message in messages:
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            for call in tool_calls:
                pending[call["id"]] = call

        if isinstance(message, ToolMessage):
            call = pending.get(message.tool_call_id)
            if not call:
                continue

            await tool_call_services.create_tool_call(
                ToolCallCreate(
                    conversation_id=conversation_id,
                    tool_name=call["name"],
                    tool_input=to_json_string(call.get("args", {})),
                    tool_output=to_json_string(message.content),
                    status="success"
                ),
                session=session
            )
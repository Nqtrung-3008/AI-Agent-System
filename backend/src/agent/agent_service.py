from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.services import message_services
from backend.src.agent.graph import graph
from backend.src.schemas.schemas import MessageCreate
from backend.src.agent.tool_call_logger import save_tool_calls_from_messages
from langchain_core.messages import HumanMessage, AIMessage

async def chat_with_agent(content: str,
                          conversation_id: int,
                          user_id: int,
                          session: AsyncSession):
    
    user_msg = MessageCreate(conversation_id=conversation_id, role="user", content=content)
    await message_services.create_message(
        message_data = user_msg, 
        session = session)

    history = await message_services.get_last_messages(conversation_id=conversation_id, user_id=user_id, session=session)

    messages = []

    for m in history:
        if m.role == "user":
            messages.append(HumanMessage(content=m.content))
        else:
            messages.append(AIMessage(content=m.content))
    
    result = await graph.ainvoke(
        {
            "messages": messages,
        },
        config={"configurable": {"user_id": user_id, "conversation_id": conversation_id, "session": session}}
    )

    await save_tool_calls_from_messages(
        messages=result["messages"],
        conversation_id=conversation_id,
        session=session
    )

    answer = result["messages"][-1].content

    assisstant_msg = MessageCreate(conversation_id=conversation_id, role='assistant', content=answer)

    await message_services.create_message(
        message_data=assisstant_msg,
        session=session
    )

    return answer
from fastapi import APIRouter
from backend.src.api.v1.endpoints import auth, conversation, message, user, note, tool_call, health

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(message.router, prefix="/messages", tags=["messages"])
router.include_router(conversation.router, prefix="/conversations", tags=["conversation"])
router.include_router(user.router, prefix="/users", tags=["users"])
router.include_router(note.router, prefix="/notes", tags=["notes"])
router.include_router(tool_call.router, prefix="/tool-calls", tags=["tool-calls"])
router.include_router(health.router, tags=["health"])
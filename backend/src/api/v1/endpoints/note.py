from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.src.dependencies import get_session, get_current_user
from backend.src.services import note_services
from backend.src.schemas.schemas import NoteCreate, NotePublic, NoteDelete

router = APIRouter()

@router.get('/{note_id}', response_model = NotePublic)
async def read_note(note_id: int,
                    session: AsyncSession=Depends(get_session),
                    user=Depends(get_current_user)):
    return await note_services.read_note_service(note_id=note_id, user_id=user.user_id, session=session)

@router.delete('/{note_id}', response_model = NoteDelete)
async def delete_sessions(note_id: int,
                          session: AsyncSession=Depends(get_session),
                          user=Depends(get_current_user)):
    deleted =  await note_services.delete_note_service(note_id=note_id, user_id=user.user_id, session=session)
    if not deleted:
      raise HTTPException(status_code=404, detail="Note not found")
    return {"deleted": True}

@router.get('/', response_model = List[NotePublic])
async def get_notes(session: AsyncSession=Depends(get_session),
                    user=Depends(get_current_user)):
    return await note_services.list_note_service(user_id=user.user_id, session=session)


from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from backend.src.models.models import Note
from backend.src.schemas.schemas import NoteCreate
from datetime import datetime, timezone

async def create_note_service(note_data: NoteCreate, user_id: int, session: AsyncSession) -> Note:
    note_dict = note_data.model_dump()
    db_note = Note(**note_dict, user_id=user_id)

    session.add(db_note)
    await session.flush()
    await session.refresh(db_note)
    return db_note

async def read_note_service(note_id: int, user_id: int, session: AsyncSession) -> Note | None:
    statement = select(Note).where(Note.note_id == note_id, Note.user_id == user_id, Note.deleted_at.is_(None))
    result = await session.exec(statement)
    return result.one_or_none()

async def update_note_service(note_id: int, content: str, user_id: int, session: AsyncSession) -> Note | None:
    note = await read_note_service(note_id, user_id, session)
    if not note:
        return None
    note.content = content
    note.updated_at = datetime.now(timezone.utc)
    session.add(note)
    await session.flush()
    await session.refresh(note)
    return note
    
async def delete_note_service(note_id: int, user_id: int, session: AsyncSession) -> bool:
    note = await read_note_service(note_id, user_id, session)
    if not note:
        return False
    
    note.deleted_at = datetime.now(timezone.utc)
    session.add(note)
    await session.flush()
    return True
    
async def list_note_service(user_id: int, session: AsyncSession) -> List[Note] | None:
    statement = select(Note).where(Note.user_id == user_id, Note.deleted_at.is_(None))

    result =await session.exec(statement)
    return result.all()
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from backend.src.schemas.schemas import NoteCreate
from backend.src.services.note_services import create_note_service, read_note_service, update_note_service, delete_note_service, list_note_service
from backend.src.agent.tool_call_logger import get_context

@tool
async def note_create(title: str, content: str, config: RunnableConfig):
    """
    Create a new note
    Args:
        note_data: The data for the new note
        user_id: The ID of the user creating the note
        content: The content of the note
    Returns:
        Information about the created note
    """

    user_id, _, session = get_context(config)
    note = await create_note_service(NoteCreate(title=title, content=content), user_id, session)
    return f"Created note {note.note_id}: {note.title}"

@tool
async def note_read(note_id: int, config: RunnableConfig) -> str:
    """
    Read a note by ID
    Args:
        note_id: The ID of the note
        user_id: The ID of the user reading the note
    Returns:
        The content of the note
    """

    user_id, _, session = get_context(config)
    note = await read_note_service(note_id, user_id, session)
    if not note:
          return "Note not found."
    return f"{note.title}\n{note.content}"

@tool
async def note_update(note_id: int, content: str, config: RunnableConfig) -> str:
    """
    Update an existing note
    Args:
        note_id: The ID of the note
        content: The new content of the note
    Returns:
        Information about the updated note.
    """

    user_id, _, session = get_context(config)
    updated_note = await update_note_service(note_id, content, user_id, session)
    if not updated_note:
          return "Note not found."
    return f"Updated note {updated_note.note_id}: {updated_note.title}"
    
@tool
async def note_delete(note_id: int, config: RunnableConfig) -> str:
    """
    Delete a note by ID
    Args:
        note_id: The ID of the note
    Returns:
        A confirmation message that the note was deleted
    """

    user_id, _, session = get_context(config)
    deleted_note = await delete_note_service(note_id, user_id, session)
    if not deleted_note:
          return "Note not found."
    return f"Deleted note {note_id}."
    
@tool
async def note_list(config: RunnableConfig) -> str:
    """
    List all notes
    Returns:
        A list of all notes with their IDs and titles
    """

    user_id, _, session = get_context(config)
    notes = await list_note_service(user_id, session)
    if not notes:
          return "No notes found."
    return "\n".join(f"{n.note_id}. {n.title}" for n in notes)
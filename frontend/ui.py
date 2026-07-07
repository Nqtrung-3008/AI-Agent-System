from __future__ import annotations

import os
from typing import Any

import httpx
import streamlit as st
import streamlit.components.v1 as components


PAGE_TITLE = "AI Agent"
BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"
AUTH_COOKIE_NAME = "ai_agent_access_token"
AUTH_COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 7


class ApiError(Exception):
    def __init__(self, status_code: int, detail: Any) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


def api_url(path: str) -> str:
    path = path if path.startswith("/") else f"/{path}"
    return f"{BASE_URL.rstrip('/')}{API_PREFIX}{path}"


def init_state() -> None:
    defaults = {
        "access_token": None,
        "user": None,
        "conversations": [],
        "active_conversation_id": None,
        "message_history": {},
        "notes": [],
        "selected_note": None,
        "tool_calls": {},
        "is_answering": False,
        "last_error": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "api_client" not in st.session_state:
        st.session_state.api_client = httpx.Client(timeout=120.0)


def browser_cookie_value(name: str) -> str | None:
    context = getattr(st, "context", None)
    cookies = getattr(context, "cookies", {}) if context else {}
    value = cookies.get(name) if cookies else None
    return value or None


def set_browser_cookie(name: str, value: str, max_age: int = AUTH_COOKIE_MAX_AGE_SECONDS) -> None:
    components.html(
        f"""
        <script>
        document.cookie = "{name}=" + encodeURIComponent({value!r})
          + "; max-age={max_age}; path=/; SameSite=Lax";
        </script>
        """,
        height=0,
        width=0,
    )


def delete_browser_cookie(name: str) -> None:
    components.html(
        f"""
        <script>
        document.cookie = "{name}=; max-age=0; path=/; SameSite=Lax";
        </script>
        """,
        height=0,
        width=0,
    )


def parse_response(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


def raise_for_api_error(response: httpx.Response) -> None:
    if response.is_success:
        return

    data = parse_response(response)
    detail = data.get("detail", data) if isinstance(data, dict) else data
    raise ApiError(response.status_code, detail)


def api_request(method: str, path: str, **kwargs: Any) -> Any:
    client: httpx.Client = st.session_state.api_client
    headers = dict(kwargs.pop("headers", {}) or {})
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = client.request(method, api_url(path), headers=headers, **kwargs)
    raise_for_api_error(response)
    return parse_response(response)


def set_error(exc: Exception) -> None:
    if isinstance(exc, ApiError):
        st.session_state.last_error = str(exc.detail)
    else:
        st.session_state.last_error = str(exc)


def clear_error() -> None:
    st.session_state.last_error = None


def backend_register(username: str, password: str) -> dict[str, Any]:
    return api_request(
        "POST",
        "/auth/register",
        json={"username": username, "password": password},
    )


def backend_login(username: str, password: str) -> dict[str, Any]:
    token_data = api_request(
        "POST",
        "/auth/login",
        json={"username": username, "password": password},
    )
    token = token_data["access_token"]
    st.session_state.access_token = token
    user = api_request("GET", "/users/me")
    return {
        "access_token": token,
        "token_type": token_data.get("token_type", "bearer"),
        "user": user,
    }


def backend_current_user() -> dict[str, Any]:
    return api_request("GET", "/users/me")


def restore_auth_from_cookie() -> None:
    if st.session_state.user or st.session_state.access_token:
        return

    token = browser_cookie_value(AUTH_COOKIE_NAME)
    if not token:
        return

    st.session_state.access_token = token
    try:
        st.session_state.user = backend_current_user()
        refresh_conversations()
        clear_error()
    except Exception:
        st.session_state.access_token = None
        st.session_state.user = None
        delete_browser_cookie(AUTH_COOKIE_NAME)


def backend_list_conversations() -> list[dict[str, Any]]:
    return api_request("GET", "/conversations/")


def backend_create_conversation() -> dict[str, Any]:
    return api_request("POST", "/conversations/", json={})


def backend_delete_conversation(conversation_id: int) -> bool:
    result = api_request("DELETE", f"/conversations/{conversation_id}")
    return bool(result.get("deleted")) if isinstance(result, dict) else False


def backend_load_messages(conversation_id: int) -> list[dict[str, Any]]:
    return api_request("GET", f"/messages/messages/{conversation_id}")


def backend_list_notes() -> list[dict[str, Any]]:
    return api_request("GET", "/notes/")


def backend_read_note(note_id: int) -> dict[str, Any]:
    return api_request("GET", f"/notes/{note_id}")


def backend_delete_note(note_id: int) -> bool:
    result = api_request("DELETE", f"/notes/{note_id}")
    return bool(result.get("deleted")) if isinstance(result, dict) else False


def backend_list_tool_calls(conversation_id: int) -> list[dict[str, Any]]:
    return api_request("GET", f"/tool-calls/{conversation_id}")


def backend_chat(conversation_id: int, content: str) -> list[dict[str, Any]]:
    api_request(
        "POST",
        "/messages/chat",
        json={"conversation_id": conversation_id, "content": content},
    )
    return backend_load_messages(conversation_id)


def refresh_conversations() -> None:
    if not st.session_state.user:
        st.session_state.conversations = []
        st.session_state.active_conversation_id = None
        return

    conversations = backend_list_conversations()
    st.session_state.conversations = conversations
    active_id = st.session_state.active_conversation_id
    ids = {item["conversation_id"] for item in conversations}
    if active_id not in ids:
        st.session_state.active_conversation_id = conversations[0]["conversation_id"] if conversations else None


def load_active_messages() -> None:
    conversation_id = st.session_state.active_conversation_id
    if conversation_id is None:
        return

    history = st.session_state.message_history
    if conversation_id not in history:
        history[conversation_id] = backend_load_messages(conversation_id)


def select_conversation(conversation_id: int) -> None:
    st.session_state.active_conversation_id = conversation_id
    load_active_messages()


def create_conversation() -> None:
    conversation = backend_create_conversation()
    st.session_state.conversations = [conversation, *st.session_state.conversations]
    st.session_state.active_conversation_id = conversation["conversation_id"]
    st.session_state.message_history[conversation["conversation_id"]] = []


def delete_active_conversation() -> None:
    conversation_id = st.session_state.active_conversation_id
    if conversation_id is None:
        return

    deleted = backend_delete_conversation(conversation_id)
    if not deleted:
        raise ApiError(404, "Conversation not found")

    st.session_state.message_history.pop(conversation_id, None)
    st.session_state.tool_calls.pop(conversation_id, None)
    refresh_conversations()


def refresh_notes() -> None:
    if not st.session_state.user:
        st.session_state.notes = []
        st.session_state.selected_note = None
        return

    st.session_state.notes = backend_list_notes()


def read_selected_note(note_id: int) -> None:
    st.session_state.selected_note = backend_read_note(note_id)


def delete_selected_note(note_id: int) -> None:
    deleted = backend_delete_note(note_id)
    if not deleted:
        raise ApiError(404, "Note not found")
    if st.session_state.selected_note and st.session_state.selected_note.get("note_id") == note_id:
        st.session_state.selected_note = None
    refresh_notes()


def refresh_tool_calls() -> None:
    conversation_id = st.session_state.active_conversation_id
    if conversation_id is None:
        return

    st.session_state.tool_calls[conversation_id] = backend_list_tool_calls(conversation_id)


def logout() -> None:
    client: httpx.Client | None = st.session_state.get("api_client")
    if client:
        client.cookies.clear()
        client.headers.clear()

    delete_browser_cookie(AUTH_COOKIE_NAME)
    st.session_state.access_token = None
    st.session_state.user = None
    st.session_state.conversations = []
    st.session_state.active_conversation_id = None
    st.session_state.message_history = {}
    st.session_state.notes = []
    st.session_state.selected_note = None
    st.session_state.tool_calls = {}
    st.session_state.is_answering = False
    clear_error()


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 980px;
            padding-top: 1.2rem;
            padding-bottom: 6rem;
        }
        [data-testid="stSidebar"] {
            min-width: 280px;
        }
        div[data-testid="stChatMessage"] {
            background: transparent;
            padding: 0.25rem 0;
        }
        div[data-testid="stChatMessageContent"] {
            border-radius: 18px;
            padding: 0.75rem 1rem;
            max-width: 78%;
            border: 1px solid rgba(49, 51, 63, 0.12);
        }
        div[data-testid="stChatMessage"]:has(svg[aria-label="user avatar"]) {
            flex-direction: row-reverse;
        }
        div[data-testid="stChatMessage"]:has(svg[aria-label="user avatar"]) div[data-testid="stChatMessageContent"] {
            margin-left: auto;
            background: #f3f4f6;
        }
        div[data-testid="stChatMessage"]:has(svg[aria-label="assistant avatar"]) div[data-testid="stChatMessageContent"] {
            margin-right: auto;
            background: #ffffff;
        }
        .chat-empty {
            min-height: 48vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #6b7280;
            text-align: center;
        }
        @media (max-width: 700px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            div[data-testid="stChatMessageContent"] {
                max-width: 92%;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_auth() -> None:
    st.sidebar.header(PAGE_TITLE)
    st.sidebar.caption(BASE_URL)

    user = st.session_state.user
    if user:
        st.sidebar.caption("Signed in")
        st.sidebar.write(user["username"])
        if st.sidebar.button("Log out", use_container_width=True):
            logout()
        return

    login_tab, register_tab = st.sidebar.tabs(["Login", "Register"])
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login", use_container_width=True)
        if submitted:
            clear_error()
            try:
                result = backend_login(username.strip(), password)
                st.session_state.access_token = result["access_token"]
                st.session_state.user = result["user"]
                set_browser_cookie(AUTH_COOKIE_NAME, result["access_token"])
                refresh_conversations()
            except Exception as exc:
                set_error(exc)

    with register_tab:
        with st.form("register_form"):
            username = st.text_input("Username", key="register_username")
            password = st.text_input("Password", type="password", key="register_password")
            submitted = st.form_submit_button("Register", use_container_width=True)
        if submitted:
            clear_error()
            try:
                backend_register(username.strip(), password)
                st.sidebar.success("Account created. You can log in now.")
            except Exception as exc:
                set_error(exc)


def render_sidebar_conversations() -> None:
    if not st.session_state.user:
        return

    st.sidebar.divider()
    if st.sidebar.button("New chat", use_container_width=True):
        clear_error()
        try:
            create_conversation()
            st.rerun()
        except Exception as exc:
            set_error(exc)

    if st.sidebar.button("Refresh chats", use_container_width=True):
        clear_error()
        try:
            refresh_conversations()
            st.rerun()
        except Exception as exc:
            set_error(exc)

    st.sidebar.caption("Conversations")
    for item in st.session_state.conversations:
        conversation_id = item["conversation_id"]
        label = f"Chat {conversation_id}"
        selected = conversation_id == st.session_state.active_conversation_id
        if selected:
            label = f"> {label}"
        if st.sidebar.button(label, key=f"conversation_{conversation_id}"):
            select_conversation(conversation_id)
            st.rerun()

    if st.session_state.active_conversation_id is not None:
        st.sidebar.divider()
        if st.sidebar.button("Delete current chat", use_container_width=True):
            clear_error()
            try:
                delete_active_conversation()
                st.rerun()
            except Exception as exc:
                set_error(exc)


def render_sidebar_notes() -> None:
    if not st.session_state.user:
        return

    with st.sidebar.expander("Notes", expanded=False):
        if st.button("Refresh notes", use_container_width=True):
            clear_error()
            try:
                refresh_notes()
            except Exception as exc:
                set_error(exc)

        notes = st.session_state.notes
        if not notes:
            st.caption("No notes loaded.")
        else:
            options = {f"{item['note_id']}: {item['title']}": item["note_id"] for item in notes}
            selected = st.selectbox("Note", list(options), key="selected_note_label")
            note_id = options[selected]

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Read", use_container_width=True):
                    clear_error()
                    try:
                        read_selected_note(note_id)
                    except Exception as exc:
                        set_error(exc)
            with col_b:
                if st.button("Delete", use_container_width=True):
                    clear_error()
                    try:
                        delete_selected_note(note_id)
                        st.rerun()
                    except Exception as exc:
                        set_error(exc)

        note = st.session_state.selected_note
        if note:
            st.divider()
            st.markdown(f"**{note['title']}**")
            st.markdown(note["content"])


def render_sidebar_tool_calls() -> None:
    if not st.session_state.user:
        return

    conversation_id = st.session_state.active_conversation_id
    with st.sidebar.expander("Tool calls", expanded=False):
        if conversation_id is None:
            st.caption("Select a conversation first.")
            return

        if st.button("Refresh tool calls", use_container_width=True):
            clear_error()
            try:
                refresh_tool_calls()
            except Exception as exc:
                set_error(exc)

        calls = st.session_state.tool_calls.get(conversation_id, [])
        if not calls:
            st.caption("No tool calls loaded.")
            return

        for call in calls:
            st.markdown(f"**#{call['id']} {call['tool_name']}**")
            st.caption(f"{call['status']} - {call['created_at']}")
            st.code(call["tool_input"] or "", language="json")
            if call["tool_output"]:
                st.code(call["tool_output"], language="json")
            st.divider()


def render_messages() -> None:
    conversation_id = st.session_state.active_conversation_id
    if conversation_id is None:
        st.markdown("<div class='chat-empty'>Start a new chat from the sidebar.</div>", unsafe_allow_html=True)
        return

    load_active_messages()
    messages = st.session_state.message_history.get(conversation_id, [])
    if not messages:
        st.markdown("<div class='chat-empty'>Ask anything.</div>", unsafe_allow_html=True)
        return

    for message in messages:
        role = "assistant" if message["role"] == "assistant" else "user"
        with st.chat_message(role):
            st.markdown(message["content"])

    st.markdown(
        """
        <div id="chat-bottom"></div>
        <script>
        const bottom = window.parent.document.getElementById("chat-bottom");
        if (bottom) bottom.scrollIntoView({ behavior: "smooth", block: "end" });
        </script>
        """,
        unsafe_allow_html=True,
    )


def handle_prompt(prompt: str) -> None:
    conversation_id = st.session_state.active_conversation_id
    if not st.session_state.user:
        st.warning("Please log in first.")
        return

    if conversation_id is None:
        create_conversation()
        conversation_id = st.session_state.active_conversation_id

    if conversation_id is None:
        st.warning("Could not create a conversation.")
        return

    st.session_state.message_history.setdefault(conversation_id, []).append(
        {
            "message_id": None,
            "conversation_id": conversation_id,
            "role": "user",
            "content": prompt,
            "created_at": None,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.is_answering = True
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                messages = backend_chat(conversation_id, prompt)
                st.session_state.message_history[conversation_id] = messages
                st.session_state.tool_calls.pop(conversation_id, None)
                st.session_state.notes = []
                st.session_state.selected_note = None
                clear_error()
            except Exception as exc:
                set_error(exc)
            finally:
                st.session_state.is_answering = False
    st.rerun()


def render_main() -> None:
    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    if not st.session_state.user:
        st.markdown("<div class='chat-empty'>Log in or register to start chatting.</div>", unsafe_allow_html=True)
        return

    render_messages()
    prompt = st.chat_input("Message AI Agent", disabled=st.session_state.is_answering)
    if prompt:
        handle_prompt(prompt)


def main() -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon="AI", layout="wide")
    init_state()
    restore_auth_from_cookie()
    inject_styles()
    render_auth()
    render_sidebar_conversations()
    render_sidebar_notes()
    render_sidebar_tool_calls()
    render_main()


if __name__ == "__main__":
    main()

# AI Agent System

Ung dung AI agent gom FastAPI backend, Streamlit frontend, PostgreSQL, Alembic migrations, LangGraph agent va Ollama LLM.

## Project Structure

```text
.
|-- backend/
|   |-- Dockerfile
|   |-- requirements.txt
|   `-- src/
|       |-- main.py
|       |-- dependencies.py
|       |-- api/
|       |   `-- v1/endpoints/
|       |-- agent/
|       |-- core/
|       |-- llm/
|       |-- models/
|       |-- schemas/
|       |-- services/
|       `-- tools/
|-- frontend/
|   |-- Dockerfile
|   |-- requirements.txt
|   `-- ui.py
|-- alembic/
|-- alembic.ini
|-- docker-compose.yml
|-- .env.example
`-- .gitignore
```

## Main Components

- Backend: FastAPI app in `backend/src/main.py`, API prefix `/api/v1`.
- Frontend: Streamlit app in `frontend/ui.py`, calls backend via HTTP using `httpx`.
- Database: PostgreSQL, schema managed by Alembic.
- Agent: LangGraph workflow in `backend/src/agent/graph.py`.
- LLM: Ollama via `langchain_ollama.ChatOllama`.
- Tools: calculator, datetime, weather, and notes tools.

## Environment

Sample file: `.env.example`

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/ai_agent
SECRET_KEY=replace-with-a-long-random-secret
SQL_ECHO=False
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_LLM_MODEL=qwen3.5:2b
BACKEND_BASE_URL=http://backend:8000
```

For local non-Docker usage, create `.env` from `.env.example` and adjust hosts:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ai_agent
OLLAMA_BASE_URL=http://localhost:11434
BACKEND_BASE_URL=http://localhost:8000
```

## Run With Docker Compose

```powershell
docker compose up --build
```

Services:

- Backend: http://localhost:8000
- Frontend: http://localhost:8501
- PostgreSQL: localhost:5432
- Ollama: http://localhost:11434

The backend container runs migrations before starting the API:

```sh
alembic upgrade head
uvicorn backend.src.main:app --host 0.0.0.0 --port 8000
```

Pull the Ollama model if it is not available:

```powershell
docker compose exec ollama ollama pull qwen3.5:2b
```

## Run Locally

Backend:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
alembic upgrade head
uvicorn backend.src.main:app --reload
```

Frontend:

```powershell
pip install -r frontend\requirements.txt
streamlit run frontend\ui.py
```

## API

Base path:

```text
/api/v1
```

Public endpoints:

- `GET /health`
- `POST /auth/register`
- `POST /auth/login`

Protected endpoints require:

```text
Authorization: Bearer <token>
```

Protected endpoints:

- `GET /users/me`
- `GET /users/{user_id}`
- `POST /conversations/`
- `GET /conversations/`
- `DELETE /conversations/{conversation_id}`
- `POST /messages/chat`
- `GET /messages/messages/{conversation_id}`
- `GET /notes/`
- `GET /notes/{note_id}`
- `DELETE /notes/{note_id}`
- `GET /tool-calls/{conversation_id}`

## Chat Workflow

1. User sends a message from the frontend.
2. Frontend calls `POST /api/v1/messages/chat`.
3. Backend verifies the conversation belongs to the current user.
4. `chat_with_agent` saves the user message to the database.
5. Backend loads recent messages as context.
6. LangGraph runs the agent with the LLM and tools.
7. Tool calls are saved into `tool_calls`.
8. Assistant answer is saved into `messages`.
9. Frontend reloads message history via `GET /messages/messages/{conversation_id}`.

## Agent Tools

The agent is wired with:

- `calculator_tool`: evaluates math expressions.
- `datetime_tool`: handles simple datetime expressions.
- `weather_tool`: gets current weather through Open-Meteo.
- `note_create`
- `note_read`
- `note_update`
- `note_delete`
- `note_list`

Note create/update are exposed through agent tools. The current HTTP router exposes note list/read/delete only.

## Database Models

Main tables:

- `users`
- `conversations`
- `messages`
- `notes`
- `tool_calls`

Initial migration:

```text
alembic/versions/c40b98efa89a_initial.py
```

## Authentication

- Backend uses JWT HS256.
- Login returns `access_token`.
- Protected endpoints use OAuth2 Bearer token.
- Frontend stores token in `st.session_state` and browser cookie `ai_agent_access_token` to restore login state after reload.
- Frontend cookie is not HTTPOnly because the backend currently does not set cookies.

## Docker Files

- `backend/Dockerfile`: installs backend requirements and runs Uvicorn.
- `frontend/Dockerfile`: installs frontend requirements and runs Streamlit.
- `docker-compose.yml`: starts PostgreSQL, backend, frontend, and Ollama.

## Operational Notes

- Docker Compose currently loads backend/frontend environment from `.env.example`.
- If `OLLAMA_LLM_MODEL` changes, pull the same model in the Ollama container.
- If a PostgreSQL volume already exists with old credentials, recreate the volume or keep matching credentials.

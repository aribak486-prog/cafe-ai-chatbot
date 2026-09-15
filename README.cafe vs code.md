# CafeAI

CafeAI is a full-stack, cafe-specialized assistant: a Vite + React/TypeScript marketing site and custom chat interface, paired with a FastAPI service that uses structured cafe data and a configurable Hugging Face Transformer.

## Architecture

`React UI → FastAPI → ConversationManager → cafe system prompt + CAFE_DATA → tokenizer → Transformer → response → UI`

Exact cafe facts are resolved from `CAFE_DATA` before model generation. This guardrail ensures known menu items, prices, ingredients, hours, and recommendations are accurate; unavailable facts are explicitly reported as unavailable.

## Structure

```text
frontend/                 React + TypeScript + Vite application
backend/app/api/          FastAPI routes
backend/app/core/         Cafe data and system prompt
backend/app/models/       Pydantic request/response schemas
backend/app/services/     Conversation manager and Transformer abstraction
```

## Technologies

- Frontend: React, TypeScript, Vite, custom CSS, Lucide icons
- Backend: Python, FastAPI, Pydantic, Uvicorn, PyTorch, Hugging Face Transformers

## Run locally

Backend (Python 3.10+ recommended):

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows; use cp on macOS/Linux
uvicorn app.main:app --reload
```

Frontend (Node 18+):

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The API runs at `http://localhost:8000`.

## Environment variables

Set these in `backend/.env` (see `.env.example`): `MODEL_NAME` (default `google/flan-t5-small`), `MAX_NEW_TOKENS`, `TEMPERATURE`, `TOP_P`, and `FRONTEND_URL`. Optionally set `VITE_API_URL` in the frontend environment for a hosted API.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Health check |
| POST | `/api/conversations` | Create temporary conversation |
| POST | `/api/chat` | Send `{ conversation_id, message }` |
| GET | `/api/conversations/{id}` | Retrieve messages |
| DELETE | `/api/conversations/{id}` | Remove conversation |

## Cafe data and model

`backend/app/core/cafe_data.py` contains the single source of truth for the demo cafe's menu, price, ingredients, dietary labels, popularity, location, and hours. `CafeAdvisorModel` lazily loads the configurable Hugging Face model for fallback generation; data questions are directly grounded first to prevent fabrication. On an offline or unavailable model, grounded cafe answers still work.

## Conversation storage

Conversation history is intentionally stored only in temporary in-memory storage. There is no permanent database. Restarting the backend clears the conversation data. The chat UI history panel keeps session conversation snapshots while the page remains open.

## Troubleshooting

- Ensure backend starts before opening chat; confirm `GET /api/health` returns `{"status":"ok"}`.
- If CORS fails, set `FRONTEND_URL` to your Vite origin and restart FastAPI.
- The first Transformer fallback request can download the configured model. Internet access is required for that initial download; cafe-data answers do not require it.
- If frontend compilation fails, remove `node_modules`, run `npm install`, then `npm run build`.

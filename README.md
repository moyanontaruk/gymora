# Gymora

**Repping with Reason — A RAG-Enhanced Workout Tracking and Exercise Discovery Platform**

MSc Information Technology project, University of Glasgow, 2026.

Gymora is a web application for people who are new to the gym. It combines exercise
discovery, workout logging and routine generation with an assistant that answers
questions using only the workouts a user has actually logged — so every answer can
be traced back to real data rather than guesswork.

---

## Live demo

| | |
|---|---|
| Frontend | https://gymora-train.netlify.app |
| API docs | https://gymora-3qgg.onrender.com/docs |

> The backend runs on a free hosting tier and sleeps after inactivity. The first
> request after an idle period may take up to a minute to respond.

---

## Features

**Exercise library** — browse and filter over 500 exercises by muscle group,
equipment, difficulty and free-text search, with detail pages showing muscle
groups, equipment, description and imagery.

**Workout logging** — record sessions with date, title, notes and any number of
exercises with sets, reps and weight. Full history view, scoped to the logged-in user.

**Routine generation** — answer five questions about goal, experience level,
equipment, days per week and session length. A rule-based generator selects
exercises and splits them across training days; an LLM then writes a plain-English explanation of why the routine looks the way it does.

**Assistant** — ask questions about your own training. The assistant retrieves the user's workout history from the database, sends it as context alongside the
question, and answers only from that data. Where the data cannot answer a question,
it says so explicitly rather than inventing a response.

**Accounts** — registration and login with JWT authentication, bcrypt-hashed
passwords, and per-user data isolation enforced at the API layer.

---

## Tech stack

**Backend**
- FastAPI (Python)
- SQLAlchemy ORM with Alembic migrations
- PostgreSQL
- JWT authentication (PyJWT) with bcrypt password hashing
- Groq API for LLM features

**Frontend**
- React with Vite
- React Router
- Plain CSS with custom properties (no UI framework)

**Deployment**
- Backend and database: Render
- Frontend: Netlify

---

## Project structure

```
gymora/
├── backend/
│   ├── app/
│   │   ├── core/           auth dependencies, JWT and password hashing
│   │   ├── models/         SQLAlchemy models (11 tables)
│   │   ├── routers/        API endpoints
│   │   ├── schemas/        Pydantic request/response schemas
│   │   ├── services/       LLM client, RAG retrieval, routine generator
│   │   ├── config.py       settings loaded from .env
│   │   ├── database.py     engine, session factory, Base
│   │   └── main.py         app setup, CORS, router registration
│   ├── migrations/         Alembic migration history
│   ├── tests/              pytest suite (routes, RAG retrieval, routine generator, security)
│   ├── seed.py             manual seed data
│   ├── import_wger.py      wger API import and difficulty classification
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/            API client
        ├── components/     shared components (nav bar, route guard, background effects)
        ├── context/        authentication context
        └── pages/          one component per screen, each with its own CSS
```

---

## Running locally

### Prerequisites

- Python 3.13
- Node.js
- PostgreSQL
- A Groq API key (free tier: https://console.groq.com)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create `backend/.env`:

```
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gymora

JWT_SECRET_KEY=generate_with_secrets_token_hex_32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

GROQ_API_KEY=your_groq_key
GROQ_MODEL=openai/gpt-oss-120b
```

Generate a JWT secret with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Create the database in PostgreSQL, then:

```bash
alembic upgrade head
python seed.py
python import_wger.py
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`, with interactive documentation at `/docs`.

> `import_wger.py` classifies exercise difficulty using the LLM, one call per
> exercise. On Groq's free tier this is rate-limited and takes some time. The
> script paces its requests and retries on rate-limit errors, and is safe to
> re-run — already-imported exercises are skipped.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

---

## Testing

**Backend** (`backend/tests/`, pytest): route tests for auth, workout logs, routines and the
assistant, plus unit tests for the routine generator's rule logic, the Groq client, and the
security helpers (hashing, JWT).

```bash
cd backend
pytest
```

**Frontend** (Vitest + Testing Library): the API client, `ProtectedRoute`, and the login page.

```bash
cd frontend
npm test
```

---

## Data sources

Exercise data is imported from [wger](https://wger.de), an open-source fitness
database, and is licensed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

wger's anatomical muscle names (for example *Rectus abdominis*) are mapped during
import onto Gymora's ten plain-English muscle groups, so users are not shown
clinical terminology. wger does not provide difficulty ratings, so these are
classified during import using an LLM.

---

## How the assistant works

The assistant uses retrieval-augmented generation with **structured database
retrieval** rather than vector search.

1. The user asks a question.
2. The backend queries that user's own rows: recent workouts, muscle group
   frequency, weight progression, and a sample of the exercise library.
3. Those results are formatted as labelled text blocks.
4. The blocks and the question are sent to the LLM, with system instructions
   requiring it to answer only from the supplied data.
5. Where the data cannot answer the question, the model emits a marker phrase,
   which the backend detects and records as an insufficient-information flag.
6. The question, answer and the exact context used are stored, so any answer can
   be audited afterwards.

Vector search was considered and rejected: the relevant subset of data is defined
by user identity and date range, which SQL selects exactly, and exact retrieval
makes the grounding requirement verifiable in a way that similarity matching
would not.

---

## Known limitations

- **Third-party rate limits.** The assistant depends on a free-tier LLM provider
  limited to 30 requests per minute and 8,000 tokens per minute. The retrieval
  context is capped to fit within this ceiling, and bulk difficulty classification
  during import requires pacing and retry logic.
- **Free-tier data handling.** Prompts sent to the provider's free tier may be
  retained for model improvement. Only training data is transmitted; no account
  identifiers are included.
- **Routine parameters.** Sets, reps, rest periods and training splits follow
  conventional gym practice. They are not clinically validated.
- **Client-side validation.** Password length is enforced in the browser only;
  the API does not currently impose a minimum.
- **Sleeping backend.** The free hosting tier suspends the service after
  inactivity, delaying the first request.

---

## Author

Maggie — MSc Information Technology, University of Glasgow.

README.md file was AI generated 

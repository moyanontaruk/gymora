# Gymora — Project Snapshot

_Generated 2026-07-30, branch `api-endpoints`._

## What it is

A RAG-enhanced workout tracking and exercise discovery platform (per README). Split into a FastAPI backend and a React (Vite) frontend, backed by PostgreSQL.

## Backend (`backend/`)

**Stack:** FastAPI 0.139, SQLAlchemy 2.0 (psycopg3), Alembic, Pydantic Settings, JWT auth (PyJWT) + bcrypt via passlib/bcrypt, PostgreSQL.

**Entry point:** `app/main.py` — creates the FastAPI app, mounts `equipment`, `exercise`, and `auth` routers, root `GET /` health check.

**Config (`app/config.py`):** `Settings` (pydantic-settings) loads `db_user`, `db_password`, `db_host`, `db_port`, `db_name`, `jwt_secret_key`, `jwt_algorithm`, `jwt_access_token_expire_minutes` from `backend/.env`.

**Database (`app/database.py`):** SQLAlchemy engine over `postgresql+psycopg`, `SessionLocal` factory, declarative `Base`, `get_db()` FastAPI dependency.

**Auth (`app/core/security.py`, `app/core/dependencies.py`):**
- `hash_password` / `verify_password` — bcrypt.
- `create_access_token` / `decode_access_token` — JWT with `sub` (user id) + `exp` claims.
- `get_current_user` — OAuth2 bearer dependency, resolves the token to a `User` row.

### API routes

| Method | Path | Notes |
|---|---|---|
| GET | `/` | health check |
| POST | `/auth/register` | create user, hashes password, rejects duplicate (case-insensitive) email |
| POST | `/auth/login` | JSON login → `Token` |
| POST | `/auth/token` | OAuth2 form login (for Swagger `/docs` Authorize button) |
| GET | `/auth/me` | current user from bearer token |
| POST/GET/GET `{id}`/PUT `{id}`/DELETE `{id}` | `/equipment` | full CRUD |
| POST/GET/GET `{id}`/PUT `{id}`/DELETE `{id}` | `/exercises` | full CRUD; list supports `difficult_level` and `exercise_type` query filters |

Equipment and exercise routers follow the same pattern: Pydantic schema in → SQLAlchemy model → schema out, with 404s on missing IDs and 201/204 status codes where appropriate.

### Data model (`app/models/`)

- **User** — `user_id, username, email(unique), password_hash, role, experience_level, created_at, updated_at`
- **Equipment** — `equipment_id, name, description`
- **MuscleGroup** — `muscle_group_id, name, description`
- **Exercise** — `exercise_id, name, description, instructions, difficulty_level, exercise_type, source, source_external_id, media_url, is_active, created_by_user_id → users, created_at, updated_at`
- **ExerciseMuscleGroup** (join) — `exercise_id, muscle_group_id, is_primary`
- **ExerciseEquipment** (join) — `exercise_id, equipment_id`
- **Routine** — `routine_id, user_id → users, name, goal, experience_level, target_muscle_group_id → muscle_groups, days_per_week, session_length_minutes, is_saved, created_at, updated_at`
- **RoutineExercise** (join) — `routine_id, exercise_id, day_number, exercise_order, suggested_sets, suggested_reps, rest_seconds, notes`
- **WorkoutLog** — `workout_log_id, user_id → users, workout_date, title, notes, created_at, updated_at`
- **WorkoutLogExercise** (join) — `workout_log_id, exercise_id, sets, reps, weight, duration_minutes, exercise_order, notes`
- **AssistantMessage** — `message_id, user_id → users, question, response, context_used, insufficient_information_flag, created_at` (this is presumably the RAG chat log)

Schemas (`app/schemas/`) exist for `user`, `equipment`, `exercise` (Create/Read/Update variants + `Token`). No schemas yet for routine, workout log, or assistant message — those models exist but have no endpoints.

### Migrations (`backend/migrations/versions/`)

Chain, oldest → newest:
1. `f8a80b71b4fe` — create difficulties table
2. `5db40a6f050b` — remove difficulties table
3. `bbac6d7fd9e7` — create users table
4. `61cf083c7602` — create equipment, muscle_group, exercise tables
5. `5c58dffd9aed` — create ExerciseMuscleGroup and ExerciseEquipment
6. `5234aeb81644` — create tables (head)

No migration yet for `routine`, `routine_exercise`, `workout_log`, `workout_log_exercise`, or `assistant_message` — those models are defined in code but not reflected in the DB schema yet.

**Other backend files:** `seed.py` (manual seed data for muscle groups/equipment/exercises, ahead of a planned wger API integration), `test_hash.py`, `test_token.py` (ad hoc scripts, not a pytest suite), `alembic.ini`, `requirements.txt`.

## Frontend (`frontend/`)

Vite + React 19 scaffold, still at the default "Get started" template (`App.jsx` is unmodified Vite boilerplate with a counter button) — no real UI built yet. Plain CSS (`App.css`, `index.css`), no router or state library installed, no API client wired up to the backend.

## Not yet started / open gaps

- Frontend has no real screens or backend integration.
- No routers/schemas for routines, workout logs, or the assistant/RAG feature, despite models existing.
- No automated test suite (only manual scripts).
- The RAG piece described in the README (exercise discovery via retrieval) isn't represented in code yet beyond the `AssistantMessage` log table.

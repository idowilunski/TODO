# TODO Web App – Spec (v0)
## Goal
A minimal, fast web app to manage personal tasks.

## User Stories (MVP)
- As a user, I can create a task with title (required) and optional note.
- I can list tasks.
- I can mark a task done/undone.
- I can edit/delete a task.

## Non-Goals (MVP)
- No auth/users.
- No recurring tasks, no due dates (yet).

## Functional Requirements
- CRUD for tasks via HTTP API.
- Frontend page that uses the API.

## Data Model
Task(id:int, title:str<=120, note:str?, done:bool, created_at:datetime)

## API (MVP)
- `GET /api/tasks` → list
- `POST /api/tasks` → {title, note?}
- `PATCH /api/tasks/:id` → {title?, note?, done?}
- `DELETE /api/tasks/:id`

## Acceptance Criteria
- Creating invalid task (empty title) returns 400.
- All endpoints return JSON and proper status codes.
- Page shows tasks without reload after add/edit/delete.

## Tech
- Backend: Flask + SQLite (SQLAlchemy), Alembic migrations
- Frontend: minimal HTML + JS (Fetch API)
- Tests: pytest + requests/flask test client
- Style: black, isort, flake8; pre-commit hooks

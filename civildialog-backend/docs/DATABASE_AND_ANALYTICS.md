# Database & Analytics (Member 5)

Covers the PostgreSQL schema, migrations, and analytics/history APIs added
to `civildialog-backend`. Read this before touching `app/models/`,
`app/db/`, `app/services/analytics_service.py`, `app/services/civility_service.py`,
`app/api/analytics.py`, or `app/api/history.py`.

## 1. PostgreSQL setup & Docker startup

PostgreSQL runs in Docker; nothing else does (FastAPI, the NLP module and
the LLM service all stay local — see `docker-compose.yml` for why).

```bash
cd civildialog-backend
docker compose up -d          # starts postgres:16-alpine on localhost:5432
docker compose ps             # wait for STATUS: healthy
```

Data persists in the named volume `civildialog_pgdata` across restarts.
`docker compose down` stops the container and keeps the volume;
`docker compose down -v` also destroys the data.

## 2. Environment variables

Copy the template and fill it in — the app will not start without these:

```bash
cp .env.example .env
```

| Variable | Owner | Notes |
|---|---|---|
| `DATABASE_URL` | Member 5 | `postgresql+psycopg://civildialog:civildialog@localhost:5432/civildialog` for the Docker setup above. Must use the `psycopg` (v3) driver. |
| `JWT_SECRET_KEY` | Member 1 | No default — generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `NLP_MODULE_PATH` | Member 3 | Path to `CivilDialog-AI/` so `app/services/nlp_service.py` can import `src.pipeline` |
| `LLM_SERVICE_URL` | Member 4 | Defaults to `http://127.0.0.1:8001` |

`.env` is git-ignored. Never commit it.

## 3. Alembic commands

Run from `civildialog-backend/` with `DATABASE_URL` set (via `.env` or the shell):

```bash
alembic current              # show the applied migration
alembic history               # list all migrations in order
alembic upgrade head          # apply any pending migrations
alembic check                 # compare live schema vs. models (no DB required to fail loudly if they differ)
alembic revision --autogenerate -m "description"   # generate a new migration after changing a model
```

**Always read a generated migration before applying it** — autogenerate
is a diff tool, not a guarantee of correctness (e.g. it does not detect
column renames; it will drop and recreate).

Current migration chain (oldest → newest):

```
eedc60aafff6  create_users_table
5acacd6025ae  create_conversations_table
71471d157002  create_messages_table
ea36927a8e80  create_message_analyses_table
6fe4ab84621a  create_analysis_issues_table
62fbe9dd3b5a  create_rewrite_suggestions_table
51284b34f287  add_messages_user_id_created_at_index   (head)
```

## 4. Schema & relationships

```mermaid
erDiagram
    USERS ||--o{ CONVERSATIONS : owns
    USERS ||--o{ MESSAGES : writes
    CONVERSATIONS ||--o{ MESSAGES : contains
    MESSAGES ||--|| MESSAGE_ANALYSES : "has one"
    MESSAGE_ANALYSES ||--o{ ANALYSIS_ISSUES : "0..N"
    MESSAGE_ANALYSES ||--o{ REWRITE_SUGGESTIONS : "0..N"

    USERS {
        bigint id PK
        varchar name
        varchar email UK
        varchar password_hash
        varchar role "user|admin"
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }
    CONVERSATIONS {
        bigint id PK
        bigint user_id FK
        varchar title
        varchar status
        int message_count "denormalized"
        numeric avg_civility_score "denormalized"
        timestamptz started_at
        timestamptz ended_at
    }
    MESSAGES {
        bigint id PK
        bigint conversation_id FK
        bigint user_id FK
        text original_text
        text final_text
        boolean was_rewritten
        timestamptz created_at
    }
    MESSAGE_ANALYSES {
        bigint id PK
        bigint message_id FK "unique, 1-to-1"
        numeric civility_score
        varchar score_version
        float toxicity_score
        boolean is_toxic
        float hate_speech_score
        boolean is_hate_speech
        varchar sentiment
        boolean llm_is_problematic
        int num_tokens
        jsonb raw_data
        timestamptz analyzed_at
    }
    ANALYSIS_ISSUES {
        bigint id PK
        bigint analysis_id FK
        varchar issue_type
        varchar severity
        double confidence
        text evidence
    }
    REWRITE_SUGGESTIONS {
        bigint id PK
        bigint analysis_id FK
        text rewrite_text
        jsonb suggestions
        boolean was_accepted
        timestamptz accepted_at
    }
```

All foreign keys are `ON DELETE CASCADE`: deleting a user removes their
conversations, messages, analyses, issues and rewrite suggestions.

**Civility Score formula** (see `app/services/civility_service.py`, the
single source of truth — do not reimplement it elsewhere):

```
penalty = toxicity_score * 70 + hate_speech_score * 30
score   = clamp(round(100 - penalty), 0, 100)     # 0-100, higher = more civil
```

Current `score_version`: `"1.0.0"`.

## 5. Authentication requirements

Every endpoint below requires `Authorization: Bearer <access_token>`
(obtained from `POST /api/v1/auth/login`), same as the existing
`/api/v1/moderation/analyze` endpoint.

**Scope rule**: a regular user (`role: "user"`) only ever sees their own
data. An admin (`role: "admin"`) sees platform-wide data on the endpoints
marked *admin-only* below, and can view any conversation's summary.
There is no way for a regular user to see another user's data through
any of these endpoints.

## 6. Analytics & History API reference

Base path: `/api/v1/analytics` (except message history, at
`/api/v1/history/messages`). Every response uses the project's standard
envelope: `{"success": true, "data": ...}`.

---

### `GET /api/v1/analytics/overview` — *admin only*

Platform-wide KPIs.

```json
{
  "success": true,
  "data": {
    "total_users": 6,
    "total_conversations": 13,
    "total_messages": 49,
    "avg_civility_score": 50.53,
    "toxic_message_count": 26,
    "toxic_message_rate": 0.5306,
    "hate_speech_count": 12,
    "hate_speech_rate": 0.2449,
    "rewrite_offered_count": 31,
    "rewrite_accepted_count": 13,
    "rewrite_adoption_rate": 0.4194
  }
}
```

### `GET /api/v1/analytics/civility-trend`

Query: `date_from`, `date_to` (ISO date, optional), `granularity`
(`day` | `week` | `month`, default `day`). Admins get the platform trend;
regular users get their own.

```json
{"success": true, "data": [
  {"date": "2026-09-01", "message_count": 5, "avg_civility_score": 63.0}
]}
```

### `GET /api/v1/analytics/civility-distribution`

Query: `date_from`, `date_to` (optional). Same admin/self scoping as above.

```json
{"success": true, "data": [
  {"range": "0-20", "count": 18, "percentage": 36.73},
  {"range": "21-40", "count": 5, "percentage": 10.2},
  {"range": "41-60", "count": 3, "percentage": 6.12},
  {"range": "61-80", "count": 5, "percentage": 10.2},
  {"range": "81-100", "count": 18, "percentage": 36.73}
]}
```

### `GET /api/v1/analytics/users/me/summary`

Always the caller's own data — no `user_id` parameter exists.

```json
{"success": true, "data": {
  "user_id": 7, "message_count": 12, "conversation_count": 3,
  "avg_civility_score": 61.4, "toxic_count": 4, "hate_speech_count": 1,
  "rewrite_count": 5, "accepted_rewrite_count": 2
}}
```

### `GET /api/v1/analytics/conversations/{conversation_id}/summary`

Owner or admin only — `403` otherwise, `404` if the conversation doesn't exist.

```json
{"success": true, "data": {
  "conversation_id": 12, "message_count": 4, "avg_civility_score": 55.25,
  "toxic_count": 2, "hate_speech_count": 0,
  "sentiment_distribution": {"NEGATIVE": 3, "POSITIVE": 1},
  "rewrite_count": 2
}}
```

### `GET /api/v1/analytics/issues/distribution`

Query: `date_from`, `date_to`, `limit` (default 10, max 100). Admin/self scoped.

```json
{"success": true, "data": [
  {"issue_type": "ad_hominem", "count": 14, "percentage": 45.16}
]}
```

### `GET /api/v1/analytics/rewrites/adoption`

Query: `date_from`, `date_to`. Admin/self scoped.

```json
{"success": true, "data": {
  "total_suggestions": 31, "accepted": 13, "rejected": 7, "adoption_percentage": 41.94
}}
```

### `GET /api/v1/analytics/reports/export?format=csv` — *admin only*

Query: `format` (only `csv` is supported — anything else is `400`),
`date_from`, `date_to`. Returns `text/csv` with
`Content-Disposition: attachment`. Columns: `date, message_count,
avg_civility_score, toxic_count, toxic_rate, hate_speech_count,
hate_speech_rate, rewrite_count`.

### `GET /api/v1/history/messages`

Query: `conversation_id` (optional filter), `limit` (default 20, max
100), `offset`. Always the caller's own messages, newest first.

```json
{"success": true, "data": {
  "total": 12, "limit": 20, "offset": 0,
  "items": [{
    "message_id": 88, "conversation_id": 12,
    "original_text": "...", "final_text": null, "was_rewritten": false,
    "created_at": "2026-09-08T10:12:00+00:00",
    "civility_score": 72.0, "is_toxic": false, "is_hate_speech": false,
    "sentiment": "NEGATIVE"
  }]
}}
```

## 7. How the frontend should consume these APIs

- **Dashboard charts** (line/bar/donut): `civility-trend`,
  `civility-distribution`, `issues/distribution`, `rewrites/adoption`.
  All accept `date_from`/`date_to` — drive a date-range picker off these.
- **"My stats" widget**: `users/me/summary` — one call, no parameters.
- **Conversation view**: `conversations/{id}/summary` alongside
  `history/messages?conversation_id={id}` for the message list itself.
- **History / activity log page**: `history/messages` with `limit`/`offset`
  pagination — `total` in the response tells you when to stop paginating.
- **Admin dashboard**: `overview` + the CSV export button
  (`reports/export?format=csv`) — both require an admin-role JWT; hide
  these from regular users in the UI, but the backend enforces it
  regardless (403 on a non-admin token).
- **Continuing a conversation**: `POST /api/v1/moderation/analyze` now
  accepts an optional `conversation_id` in the request body and always
  returns `conversation_id` + `message_id` in the response — store the
  first response's `conversation_id` and pass it on subsequent messages
  in the same conversation. Omitting it starts a new conversation.
- **Accepting a rewrite suggestion**: not yet wired to an endpoint — flag
  for Member 5/Member 1 if the frontend needs to mark a rewrite as
  accepted/rejected (this is what feeds `rewrite_adoption_rate`); see
  "Remaining issues" in the implementation report.

## 8. Seed data

```bash
.venv/Scripts/python scripts/seed_data.py
```

Creates 6 users (`*.seed` emails, password `SeedPassword123!` — a fixed,
public, development-only credential, not a secret), spread across
conversations with a realistic mix of civil/toxic/hate-speech messages,
sentiments, issues and rewrite suggestions (accepted/rejected/pending).
Safe to re-run — it deletes its own previous rows (by the fixed seed
emails) before reinserting.

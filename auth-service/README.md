# Auth Service

Standalone FastAPI authentication microservice with registration, login, JWT access/refresh tokens, Redis-backed session control, and role-based access control (RBAC).

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 (async) + Alembic |
| Database | PostgreSQL (`auth_db`) |
| Cache / sessions | Redis |
| Validation | Pydantic v2 (strict mode) |
| JWT | python-jose (HS256) |
| Passwords | passlib + bcrypt (cost factor 12) |

## Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Redis 7+

## Project Structure

```
auth-service/
├── app/
│   ├── core/           # config, database, security, redis
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # business logic
│   ├── routers/        # API endpoints
│   ├── dependencies/   # auth & RBAC dependencies
│   └── main.py
├── migrations/         # Alembic migrations
├── tests/
├── .env.example
├── requirements.txt
└── pyproject.toml
```

---

## Installation (Local)

### 1. Clone and enter the service directory

```bash
cd auth-service
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` for your machine.

**macOS Homebrew PostgreSQL** (no `postgres` user — uses your macOS username):

```env
DATABASE_URL=postgresql+asyncpg://YOUR_MAC_USERNAME@localhost:5432/auth_db
```

**Redis:**

```env
REDIS_URL=redis://localhost:6379/0
```

**JWT** (must match product-service):

```env
JWT_SECRET_KEY=change-me-in-production-use-a-long-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 5. Create the database

**Homebrew Postgres:**

```bash
createdb auth_db
```

**psql:**

```bash
psql -h localhost -U YOUR_MAC_USERNAME -d postgres -c 'CREATE DATABASE auth_db'
```

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Start Redis

```bash
# macOS Homebrew
brew services start redis
```

### 8. Start the API

```bash
uvicorn app.main:app --reload --port 8000
```

- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/auth_db` | Async Postgres connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `JWT_SECRET_KEY` | (required in prod) | Shared secret with product-service |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `BCRYPT_ROUNDS` | `12` | Password hashing cost |
| `LOGIN_MAX_ATTEMPTS` | `5` | Failed logins before lockout |
| `LOGIN_LOCKOUT_MINUTES` | `15` | Lockout duration |

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | Public | Register a new customer |
| POST | `/auth/login` | Public | Login; returns access + refresh tokens |
| POST | `/auth/refresh` | Refresh token (body) | Rotate tokens |
| POST | `/auth/logout` | Bearer + refresh body | Revoke access & refresh tokens |
| GET | `/auth/me` | Bearer | Current user profile |
| PATCH | `/auth/me` | Bearer | Update own full name |
| GET | `/auth/users` | Admin+ | Paginated user list |
| PATCH | `/auth/users/{id}/role` | Super admin | Update user role |
| GET | `/health` | Public | Health check |

### Logout request format

```http
POST /auth/logout
Authorization: Bearer <access_token>
Content-Type: application/json

{ "refresh_token": "<refresh_token>" }
```

---

## Roles

| Role | Level | Capabilities |
|------|-------|--------------|
| `customer` | 0 | Default on registration |
| `admin` | 1 | List users, admin product routes (via JWT) |
| `super_admin` | 2 | Change user roles |

### Promote a user (SQL)

```bash
psql -d auth_db -c "UPDATE users SET role = 'admin' WHERE email = 'you@example.com';"
psql -d auth_db -c "UPDATE users SET role = 'super_admin' WHERE email = 'you@example.com';"
```

---

## Redis Keys

| Key pattern | Purpose |
|-------------|---------|
| `refresh_token:{jti}` | Active refresh token (7 days) |
| `refresh_blacklist:{jti}` | Revoked refresh token |
| `access_blacklist:{jti}` | Revoked access token (logout) |
| `login_fail:{email}` | Failed login counter (15 min) |

---

## Running Tests

Uses isolated DB `auth_db_test` and Redis DB `15`.

**Prerequisites:** PostgreSQL and Redis running locally.

```bash
source .venv/bin/activate
pip install -r requirements.txt
pytest --cov=app/routers --cov=app/services --cov-report=term-missing --cov-fail-under=75
```

### Test layout

| Path | Coverage |
|------|----------|
| `tests/unit/test_password.py` | Password policy + bcrypt |
| `tests/unit/test_security.py` | JWT encode/decode |
| `tests/unit/test_role_hierarchy.py` | Role levels |
| `tests/integration/test_auth_flow.py` | Register → login → logout |
| `tests/integration/test_refresh_rotation.py` | Refresh token rotation |
| `tests/integration/test_rate_limiting.py` | Login lockout |
| `tests/integration/test_role_enforcement.py` | RBAC enforcement |
| `tests/integration/test_services_and_admin.py` | Services + admin APIs |

---

## Troubleshooting

### `role "postgres" does not exist`

Homebrew Postgres uses your macOS username, not `postgres`. Update `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql+asyncpg://anandchitikela@localhost:5432/auth_db
```

### `connection refused` on Redis

Start Redis: `brew services start redis`

### Product-service rejects tokens

Ensure `JWT_SECRET_KEY` is **identical** in auth-service and product-service `.env` files.

### CORS errors from UI

The API allows `http://localhost:5173` by default. Restart the service after pulling latest `main.py` if needed.

---

## Password Policy

Registration passwords must:

- Be at least 8 characters
- Include one uppercase letter
- Include one number

Example: `Password1`

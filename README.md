# Kalo Microservices

Assessment monorepo with **Auth Service**, **Product Service**, and **React UI**.

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.12+ |
| PostgreSQL | 14+ |
| Redis | 7+ |
| Node.js | 20+ (UI only) |

## Services

| Service | Port | URL |
|---------|------|-----|
| auth-service | 8000 | http://localhost:8000/docs |
| product-service | 8001 | http://localhost:8001/docs |
| ui | 5173 | http://localhost:5173 |

You need **three terminals** for the APIs and UI, plus Postgres and Redis running in the background.

### 1. Start Postgres and Redis

**macOS (Homebrew):**

```bash
brew services start postgresql@16
brew services start redis
```

Verify:

```bash
redis-cli ping          # PONG
psql -d postgres -c "SELECT 1"
```

### 2. Create databases

```bash
createdb auth_db
createdb product_db
```

If `createdb` fails:

```bash
psql -d postgres -c "CREATE DATABASE auth_db;"
psql -d postgres -c "CREATE DATABASE product_db;"
```

> **Homebrew Postgres** uses your macOS username (no password), not `postgres:postgres`.  
> Example: `postgresql+asyncpg://jane@localhost:5432/auth_db`

### 3. Auth service (terminal 1)

```bash
cd auth-service

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

Edit `auth-service/.env` — set `YOUR_MAC_USERNAME` and a shared secret:

```env
DATABASE_URL=postgresql+asyncpg://YOUR_MAC_USERNAME@localhost:5432/auth_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-shared-secret
ENVIRONMENT=development
```

Start the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Health check: http://localhost:8000/health

### 4. Product service (terminal 2)

```bash
cd product-service

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

Edit `product-service/.env` — **same `JWT_SECRET_KEY` as auth**:

```env
DATABASE_URL=postgresql+asyncpg://YOUR_MAC_USERNAME@localhost:5432/product_db
REDIS_URL=redis://localhost:6379/1
JWT_SECRET_KEY=your-shared-secret
ENVIRONMENT=development
```

Start the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

Health check: http://localhost:8001/health

### 5. UI (terminal 3)

```bash
cd ui

npm install
cp .env.example .env
```

`ui/.env` (defaults are usually fine):

```env
VITE_AUTH_API_URL=http://localhost:8000
VITE_PRODUCT_API_URL=http://localhost:8001
```

```bash
npm run dev
```

Open http://localhost:5173

### 6. Promote admin

After registering in the UI:

```bash
psql -d auth_db -c "UPDATE users SET role = 'admin' WHERE email = 'you@example.com';"
```

Log out and log back in.

### Troubleshooting

| Issue | Fix |
|-------|-----|
| `role "postgres" does not exist` | Use your macOS username in `DATABASE_URL` |
| `ModuleNotFoundError` | Activate `.venv` and run `pip install -r requirements.txt` |
| Product API returns 401 | Ensure `JWT_SECRET_KEY` matches in both `.env` files |
| Port already in use | Stop other processes on 8000 / 8001 / 5173 |

More detail: `auth-service/README.md`, `product-service/README.md`, `ui/README.md`.

---

## Environment files

| File | Purpose |
|------|---------|
| `auth-service/.env.example` | Template → copy to `.env` |
| `product-service/.env.example` | Template → copy to `.env` |
| `ui/.env.example` | Template → copy to `.env` |

**Required keys (minimum):** `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `ENVIRONMENT` (auth); product also needs matching `JWT_*` and `ENVIRONMENT`.

---

## Tests

```bash
cd auth-service && source .venv/bin/activate && pytest
cd product-service && source .venv/bin/activate && pytest --cov=app/routers --cov=app/services --cov-fail-under=75
```

---

## Pending items

- **Dockerization** — containerize auth-service, product-service, UI, Postgres, and Redis for one-command local setup.
- **Validating the test cases** — review and run the full test suite across services to confirm coverage and behavior.
- **Swagger comments** — add richer OpenAPI descriptions to `/docs` (endpoint summaries, parameter docs, and response details).
- **UI validations and review** — To Review UI validation and changes

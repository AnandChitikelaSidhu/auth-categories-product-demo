# Product Service

Standalone FastAPI product catalog microservice. Validates JWTs issued by the Auth Service (shared secret — no Auth DB calls), applies role-based rules, and provides a Redis-cached catalog with inventory management.

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 (async) + Alembic |
| Database | PostgreSQL (`product_db`) |
| Cache | Redis (product detail cache) |
| Auth | JWT validation only (python-jose) |
| Validation | Pydantic v2 (strict mode) |

## Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Redis 7+
- Auth Service running (for obtaining JWTs) — or same `JWT_SECRET_KEY` for token validation

## Project Structure

```
product-service/
├── app/
│   ├── core/           # config, database, security, redis, slug
│   ├── models/         # Category, Product
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # business logic + cache
│   ├── routers/        # products, categories
│   ├── dependencies/   # JWT auth deps
│   └── main.py
├── migrations/
├── tests/
├── .env.example
└── requirements.txt
```

---

## Installation (Local)

### 1. Enter the service directory

```bash
cd product-service
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

**macOS Homebrew PostgreSQL:**

```env
DATABASE_URL=postgresql+asyncpg://YOUR_MAC_USERNAME@localhost:5432/product_db
```

**Redis** (uses DB `1` — auth-service uses DB `0`):

```env
REDIS_URL=redis://localhost:6379/1
```

**JWT** (must match auth-service exactly):

```env
JWT_SECRET_KEY=change-me-in-production-use-a-long-random-string
JWT_ALGORITHM=HS256
PRODUCT_CACHE_TTL_SECONDS=300
```

### 5. Create the database

```bash
createdb product_db
```

Or:

```bash
psql -h localhost -U YOUR_MAC_USERNAME -d postgres -c 'CREATE DATABASE product_db'
```

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Start Redis

```bash
brew services start redis
```

### 8. Start the API

```bash
uvicorn app.main:app --reload --port 8001
```

- Swagger UI: http://localhost:8001/docs
- Health: http://localhost:8001/health

> **Important:** Run on port **8001**, not 8000. Port 8000 is the auth-service.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/product_db` | Async Postgres connection |
| `REDIS_URL` | `redis://localhost:6379/1` | Redis for product cache |
| `JWT_SECRET_KEY` | (required) | Must match auth-service |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `PRODUCT_CACHE_TTL_SECONDS` | `300` | Product cache TTL (5 min) |

---

## API Endpoints

### Categories

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/categories` | Public | List categories (paginated) |
| POST | `/categories` | Admin+ | Create category |

### Products

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/products` | Public | List products (filters, pagination) |
| GET | `/products?include_inactive=true` | Admin+ | Include soft-deleted products |
| GET | `/products/{id\|slug}` | Public | Product detail (`X-Cache: HIT/MISS`) |
| POST | `/products` | Admin+ | Create product |
| PUT | `/products/{id\|slug}` | Admin+ | Update product |
| PATCH | `/products/{id\|slug}/stock` | Admin+ | Update stock by delta |
| DELETE | `/products/{id\|slug}` | Admin+ | Soft delete |
| GET | `/health` | Public | Health check |

### Query parameters (GET `/products`)

| Param | Type | Description |
|-------|------|-------------|
| `page` | int | Page number (default 1) |
| `page_size` | int | Items per page (default 20, max 100) |
| `category_id` | UUID | Filter by category |
| `min_price` | decimal | Minimum price |
| `max_price` | decimal | Maximum price |
| `include_inactive` | bool | Admin only — show inactive products |

### Stock update (PATCH `/products/{id}/stock`)

```json
{ "delta": -5 }
```

- Positive `delta` = restock
- Negative `delta` = sell / remove stock
- Returns 400 if stock would go below 0

---

## Authentication

Product-service does **not** call auth-service. It validates JWTs locally:

```http
Authorization: Bearer <access_token from /auth/login>
```

The token must be signed with the same `JWT_SECRET_KEY` and have `type: "access"`.

### Get a token

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"Password1"}'
```

Use `access_token` from the response for product API calls.

---

## Redis Cache

| Key | Value | TTL |
|-----|-------|-----|
| `product:{uuid}` | Product JSON | 300 seconds |

- **SET** on `GET /products/{id}` cache miss
- **DEL** on PUT, PATCH stock, DELETE
- Response header `X-Cache: HIT` or `MISS` on product detail

---

## Running Tests

Uses isolated DB `product_db_test` and fakeredis (no real Redis required for tests).

```bash
source .venv/bin/activate
pip install -r requirements.txt
pytest --cov=app/routers --cov=app/services --cov-report=term-missing --cov-fail-under=75
```

### Test layout

| Path | Coverage |
|------|----------|
| `tests/integration/test_catalog.py` | Public catalog endpoints |
| `tests/integration/test_admin_routes.py` | Admin CRUD |
| `tests/integration/test_stock.py` | Stock delta + locking |
| `tests/integration/test_cache.py` | Redis cache HIT/MISS |
| `tests/integration/test_auth_and_soft_delete.py` | JWT + soft delete |
| `tests/unit/test_security.py` | JWT decode |

---

## Troubleshooting

### `role "postgres" does not exist`

Create `product-service/.env` (not just `.env.example`):

```env
DATABASE_URL=postgresql+asyncpg://YOUR_MAC_USERNAME@localhost:5432/product_db
```

### Both ports show Auth Swagger

You likely started auth-service twice. Product-service must run on **8001**:

```bash
uvicorn app.main:app --reload --port 8001
```

### 401 on admin routes

- Token expired — login again or refresh
- User is `customer` — promote to `admin` in auth DB
- `JWT_SECRET_KEY` mismatch between services

### CORS errors from UI

Product-service exposes `X-Cache` and allows `http://localhost:5173`. Restart after pulling latest code.

---

## Example Workflow

```bash
# 1. Login (auth-service)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Password1"}' | jq -r .access_token)

# 2. Create category
curl -X POST http://localhost:8001/categories \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Electronics"}'

# 3. List products (public)
curl http://localhost:8001/products
```

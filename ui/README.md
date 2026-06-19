# Kalo UI

Production-ready React 19 + TypeScript frontend for the Kalo auth and product microservices.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Build | Vite 6 |
| UI | React 19 + TypeScript (strict) |
| Routing | React Router v7 |
| Styling | Tailwind CSS v4 |
| Components | shadcn/ui-style (Radix primitives) |
| Server state | TanStack Query |
| HTTP | Axios (JWT + auto refresh) |
| Client state | Zustand (persisted auth) |
| Forms | React Hook Form + Zod |
| Toasts | Sonner |

## Prerequisites

- **Node.js 20+** (recommended: 22.x via nvm)
- Auth service running at http://localhost:8000
- Product service running at http://localhost:8001
- Same `JWT_SECRET_KEY` in both backend `.env` files

---

## Installation

### 1. Enter the UI directory

```bash
cd ui
```

### 2. Use a supported Node version

```bash
nvm use 22        # or nvm use 20
node --version    # should be v20+ or v22+
```

### 3. Install dependencies

```bash
npm install
```

### 4. Configure environment

```bash
cp .env.example .env
```

Default `.env`:

```env
VITE_AUTH_API_URL=http://localhost:8000
VITE_PRODUCT_API_URL=http://localhost:8001
```

### 5. Start the dev server

```bash
npm run dev
```

Open http://localhost:5173

---

## Running the Full Stack

Use **three terminals**:

**Terminal 1 — Auth Service**

```bash
cd auth-service
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Product Service**

```bash
cd product-service
source .venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

**Terminal 3 — UI**

```bash
cd ui
npm run dev
```

| App | URL |
|-----|-----|
| UI | http://localhost:5173 |
| Auth API / Swagger | http://localhost:8000/docs |
| Product API / Swagger | http://localhost:8001/docs |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_AUTH_API_URL` | `http://localhost:8000` | Auth service base URL |
| `VITE_PRODUCT_API_URL` | `http://localhost:8001` | Product service base URL |

> Vite only exposes variables prefixed with `VITE_`.

---

## Project Structure

```
ui/src/
├── features/
│   ├── auth/
│   │   ├── api/          # auth API client
│   │   ├── hooks/        # useLogin, useLogout, useProfile, ...
│   │   ├── store/        # Zustand auth store
│   │   ├── schemas/      # Zod validation schemas
│   │   ├── components/   # AuthBootstrap
│   │   └── pages/        # Login, Register, Profile
│   ├── products/
│   │   ├── api/ hooks/ schemas/ types/ components/ pages/
│   ├── categories/
│   │   ├── api/ hooks/ schemas/ types/ pages/
│   └── users/
│       ├── api/ hooks/ pages/
├── routes/
│   ├── guards.tsx        # ProtectedRoute, AdminRoute, SuperAdminRoute
│   └── AppRoutes.tsx
└── shared/
    ├── components/       # layout, ui, ErrorBoundary, ThemeProvider
    ├── lib/              # api-client, utils
    └── types/
```

---

## Features

### Authentication

- Register, login, profile, logout
- JWT stored in Zustand (localStorage persist)
- Axios interceptors attach `Authorization: Bearer ...`
- Automatic refresh on 401 via `/auth/refresh`
- Logout revokes both tokens (header + body)

### Route Guards

| Guard | Access |
|-------|--------|
| Public | Anyone |
| `ProtectedRoute` | Logged-in users |
| `AdminRoute` | `admin`, `super_admin` |
| `SuperAdminRoute` | `super_admin` only |

### Products (Public)

- Product list with search, category filter, price range, pagination
- Product detail page
- Cache status badge (`X-Cache: HIT` / `MISS`)

### Admin

- Product table: create, edit, stock delta, soft delete
- Category creation
- User list (admin)
- Role management (super admin)

### UI/UX

- Responsive sidebar + navbar
- Dark / light mode
- Skeleton loaders, empty states, error boundary
- Toast notifications (Sonner)
- Confirmation dialogs for destructive actions

---

## Pages & Routes

| Path | Access | Description |
|------|--------|-------------|
| `/` | Public | Product catalog |
| `/products/:slug` | Public | Product detail |
| `/categories` | Public | Category list |
| `/login` | Public | Sign in |
| `/register` | Public | Create account |
| `/profile` | Authenticated | User profile |
| `/admin/products` | Admin+ | Manage products |
| `/admin/categories` | Admin+ | Create categories |
| `/admin/users` | Admin+ | User list |
| `/admin/roles` | Super admin | Update roles |

---

## Scripts

```bash
npm run dev       # Start dev server (port 5173)
npm run build     # TypeScript check + production build
npm run preview   # Preview production build
npm run lint      # ESLint
```

---

## Admin Setup

1. Register at http://localhost:5173/register
2. Promote your user in Postgres:

```bash
psql -d auth_db -c "UPDATE users SET role = 'admin' WHERE email = 'you@example.com';"
```

For role management UI:

```bash
psql -d auth_db -c "UPDATE users SET role = 'super_admin' WHERE email = 'you@example.com';"
```

3. Log out and log back in to refresh the JWT role claim.

---

## Auth Flow (Technical)

```
Login → store access_token + refresh_token in Zustand
      → fetch /auth/me → store user + role

API call → Axios adds Bearer token
         → 401? → POST /auth/refresh → retry request
         → refresh fails? → clear session → redirect to /login

Logout → POST /auth/logout
         Header: Bearer <access_token>
         Body:   { refresh_token }
       → clear Zustand + query cache
```

---

## Troubleshooting

### `Network Error` / CORS

Ensure auth-service and product-service are running and include CORS for `http://localhost:5173`. Restart both backends after pulling latest code.

### `401` on admin pages

- Token expired — log in again
- User role is `customer` — promote to `admin` in DB
- `JWT_SECRET_KEY` mismatch between backends

### `role "postgres" does not exist` (backend)

That's a backend `.env` issue — see `auth-service/README.md` and `product-service/README.md`.

### Node version errors

```bash
nvm install 22
nvm use 22
rm -rf node_modules package-lock.json
npm install
```

Vite 6 requires Node 20+. The project uses Vite 6 (not Vite 8) for broader compatibility.

### Empty product list

Create categories and products via admin UI (`/admin/categories`, `/admin/products`) or Swagger at http://localhost:8001/docs.

---

## Password Requirements

Registration passwords must match auth-service policy:

- Minimum 8 characters
- At least one uppercase letter
- At least one number

Example: `Password1`

# Heroes API Demo

This is a demo FastAPI project with limited functionality. It is meant to show a small authenticated API, basic role-aware access control, and a lightweight React admin-style frontend. It is not production-ready and does not include hardened security, full validation coverage, complete user workflows, or deployment packaging.

## What It Includes

- FastAPI backend for users, heroes, and missions.
- JWT login with bearer-token authentication.
- Admin-only user management endpoints.
- Public read endpoints for heroes and missions.
- Protected create/update endpoints for authenticated users.
- Admin-only delete flows for selected resources.
- Frontend authored by codex.
- A React frontend prototype with login, sidebar navigation, dashboard, heroes, missions, and users views.
- A standalone browser frontend fallback for Windows environments without Node/npm.

## Backend

### *Authored by codex.*

Run the API from the `app` directory:

```powershell
cd app
uvicorn main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Interactive docs:

```text
http://127.0.0.1:8000/docs
```

The FastAPI entrypoint is:

```text
app/main.py
```

The ASGI import path is:

```text
main:app
```

## Frontend

### *Authored by Codex*
The normal React/Vite frontend lives in `frontend/`.

If Node/npm are available:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## No npm Fallback

For Windows environments where `npm install` is not available, use the standalone HTML frontend:

```powershell
cd frontend
python -m http.server 5173
```

Open:

```text
http://127.0.0.1:5173/standalone.html
```

This standalone page loads React from a CDN in the browser, so it still needs internet access unless those scripts are cached.

## Tests

Run tests from the repository root, not from `app`.

If your global Python environment has unrelated pytest plugins installed, disable plugin autoloading:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"
.\.venv\Scripts\python.exe -m pytest -p pytest_asyncio tests -v
```

Without that environment variable, globally installed plugins such as `langsmith` may load automatically and fail before this project's tests are collected.

## Notes

- Users employ a defense-in-depth pattern: route dependencies check authorization, and user services also perform permission checks.
- Other resources are simpler: most access control is handled at the route layer.
- Users can have multiple roles, currently constrained to fixed role names: `viewer`, `editor`, and `admin`.
- Viewers can read heroes and missions only. Editors can create and update heroes and missions. Admins have all privileges across users, heroes, and missions.
- The frontend is intentionally small and demo-oriented; it favors clarity over exhaustive CRUD behavior.
- Database configuration and default admin credentials are loaded from `.env`.

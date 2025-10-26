A to Z Household Services v2

Overview

Full‑stack web app for managing customer service requests and professional assignments. The backend is a Flask API with JWT auth and Celery jobs; the frontend is a Vue 3 app powered by Vite (Node or Deno supported).

Tech Stack

- Backend: Python, Flask, SQLAlchemy, JWT, Celery, Redis
- Frontend: Vue 3, Vite, Bootstrap 5
- DB: SQLite (default), configurable via DATABASE_URL

Repository Structure

```
base/
  backend/        # Flask API + Celery jobs
  frontend/       # Vue 3 SPA (Vite, supports Node or Deno)
```

Prerequisites

- Python 3.13 (recommended; 3.11+ should work)
- Node.js 18+ (if using Node for frontend) OR Deno 2+
- Redis 6+ (only required for Celery jobs)

Quickstart

1) Backend (API)

- Open a terminal in base/backend and create a virtual environment:
  - Windows (PowerShell):
    - python -m venv .venv
    - .\.venv\Scripts\Activate.ps1
  - macOS/Linux:
    - python -m venv .venv
    - source .venv/bin/activate
- Install dependencies:
  - pip install -r requirements.txt
- Create a .env file (see Environment below).
- Run the API:
  - python manage.py
- API base URL: http://localhost:5000/api

2) Frontend (SPA)

Option A: Node
- cd base/frontend
- npm install
- npm run dev
- App URL: http://localhost:5173

Option B: Deno
- cd base/frontend
- deno task dev
- App URL: http://localhost:5173

Environment

Backend .env (base/backend/.env):

```
# Flask
SECRET_KEY=changeme
JWT_SECRET_KEY=changeme

# Admin login (default if not overridden)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123

# Database
# DATABASE_URL=sqlite:///project_database.db  # optional; defaults to sqlite file in backend dir

# Celery/Redis (required only if running background jobs)
broker_url=redis://localhost:6379/0
result_backend=redis://localhost:6379/0
```

Frontend .env (base/frontend/.env):

```
VITE_API_BASE_URL=http://localhost:5000/api
```

Admin Login

- Default credentials come from backend config: ADMIN_EMAIL and ADMIN_PASSWORD.
- If you keep defaults, log in with admin@example.com / admin123.

Background Jobs (Celery)

- Open a terminal in base/backend and activate the venv.
- Start a worker (and optional beat scheduler):
  - Worker: celery -A celery_app.celery worker --loglevel=info
  - Beat:   celery -A celery_app.celery beat --loglevel=info
  - Both:   celery -A celery_app.celery worker --beat --loglevel=info

Notes

- Vite alias: base/frontend/vite.config.js defines '@' aliased to your machine path. If the path differs, update resolve.alias '@' to point to base/frontend/src on your system.
- Database: The app creates tables automatically on startup. Optionally use Flask‑Migrate (migrations folder exists) if you extend the schema.

Documentation

- Backend API and setup: base/backend/README.md
- Frontend usage and routes: base/frontend/README.md

Troubleshooting

- CORS: CORS is enabled for /api/*. If you deploy frontend and backend on different hosts, ensure the origins are allowed.
- Tokens: The frontend saves access tokens to localStorage under token and userRole. Clear localStorage if switching users/roles.
- Redis/Celery: Ensure Redis is running and broker_url/result_backend match your instance.



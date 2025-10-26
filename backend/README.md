# Backend (Flask API)

This document details environment setup and every available API route.

Run Locally

1) Create and activate venv
- Windows (PowerShell):
  - python -m venv .venv
  - .\.venv\Scripts\Activate.ps1
- macOS/Linux:
  - python -m venv .venv
  - source .venv/bin/activate

2) Install dependencies
- pip install -r requirements.txt

3) Configure environment (.env)

```
SECRET_KEY=changeme
JWT_SECRET_KEY=changeme
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
broker_url=redis://localhost:6379/0
result_backend=redis://localhost:6379/0
# DATABASE_URL=sqlite:///project_database.db  # optional override
```

4) Run the API
- python manage.py
- Base URL: http://localhost:5000

Application Wiring

- App factory: `app/__init__.py` registers blueprints and initializes extensions (DB, JWT, CORS, Migrate).
- Config: `config.py` controls DB, JWT, Admin credentials, uploads, Celery.
- Schemas: `app/schemas/schema.py`
- Models: `app/models/models.py`
- Services: `app/services/*`
- Tasks (Celery): `app/tasks.py`, configured via `app/celery_config.py` and `celery_app.py`

JWT

- Access tokens via Authorization: Bearer <token> header
- Refresh token endpoint issues a new access token
- Claims include `email`, `role` and for professionals `is_verified`

Roles

- ADMIN: special login via configured ADMIN_EMAIL/ADMIN_PASSWORD
- CUSTOMER: default for customer registrations
- PROFESSIONAL: requires admin verification for some actions

API Reference

Root

- GET `/` → health/message

Auth (`/api/auth`)

- POST `/login`
  - Body: `{ email, password }`
  - Returns: `{ access_token, refresh_token, email, user }`
  - Admin login allowed via ADMIN_EMAIL/ADMIN_PASSWORD

- POST `/register/customer`
  - Body: `UserSchema + CustomerSchema`
  - Returns: tokens and IDs

- POST `/register/professional`
  - Content-Type: `multipart/form-data` or `application/json`
  - Fields: `UserSchema + ProfessionalSchema`
  - Optional file field: `documents` (multiple)
  - Returns: tokens, `professional_id`, optional uploaded documents info

- POST `/refresh` (refresh token required)
  - Returns a new access token

- POST `/change-password` (auth)
  - Body: `{ old_password, new_password }`

Users (`/api/users`)

- GET `/profile` (auth)
  - Returns current user profile (UserSchema)

- PUT `/profile` (auth)
  - Update current user (partial UserSchema; password cannot be updated here)

- GET `/:user_id` (admin)
  - Returns user by id

- POST `/deactivate` (auth)
  - Deactivates current account

Professionals (`/api/professionals`)

- GET `/profile` (auth)
  - Returns current professional profile (by user id)

- PUT `/profile` (auth)
  - Update professional profile (partial ProfessionalSchema)

- GET `/:professional_id` (auth)
  - Professional details by id

- GET `/service/:service_id?pincode=XXXXX` (public)
  - List available professionals for a service in a pincode

- POST `/documents` (auth, multipart)
  - Upload professional verification documents
  - Fields: `documents` (multiple), `document_type` (optional)

Service Requests (`/api/service-requests`)

- POST `/` (auth customer)
  - Create request (ServiceRequestSchema). Required: `service_id`, `location`, `pin_code`

- GET `/:request_id` (auth)
  - Authorized customer, assigned professional, or admin

- GET `/customer` (auth customer)
  - All requests for current customer

- GET `/professional` (auth professional)
  - All requests assigned to current professional

- GET `/available` (auth professional, verified)
  - Available requests for the professional’s service

- POST `/:request_id/assign` (admin)
  - Body: `{ professional_id }`
  - Assign a professional to a request

- POST `/:request_id/complete` (auth customer)
  - Body may include review fields: `{ rating, comment }`

- POST `/:request_id/start` (auth professional)
  - Mark request in progress

- POST `/:request_id/cancel` (auth customer)
  - Cancel a request

Admin (`/api/admin`) — admin-only unless noted

- GET `/users`
- POST `/users/:user_id/block` `{ reason }`

- GET `/services` (public list of active services)
- POST `/services` (create service) — body: ServiceSchema

- GET `/professionals`
- POST `/professionals/verify/:professional_id`
- POST `/professionals/reject/:professional_id`
- POST `/professionals/reset/:professional_id`

- GET `/customers`

- GET `/dashboard` (placeholder stats)

- POST `/export/service-requests` → starts CSV export job; returns `{ job_id }`
- GET `/export/status/:job_id`
- GET `/export/download/:filename`

Celery Jobs

- Daily reminders: `send_daily_reminders` (18:00 daily)
- Monthly reports: `generate_monthly_reports` (1st day monthly)
- CSV export: `generate_csv_export` (triggered via admin endpoint)

Run Celery

- Worker: `celery -A celery_app.celery worker --loglevel=info`
- Beat:   `celery -A celery_app.celery beat --loglevel=info`
- Both:   `celery -A celery_app.celery worker --beat --loglevel=info`

Status Codes & Errors

- 400/422 validation errors; 401/403 auth/role errors; 404 resource not found; 500 unexpected errors



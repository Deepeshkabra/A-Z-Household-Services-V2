# Frontend (Vue 3 + Vite)

This is the SPA for A to Z Household Services. It talks to the Flask API.

Prerequisites

- Option A: Node.js 18+ (recommended for most users)
- Option B: Deno 2+ (supported via @deno/vite-plugin)

Environment

Create `.env` in this folder:

```
VITE_API_BASE_URL=http://localhost:5000/api
```

Install & Run

Option A: Node

```
npm install
npm run dev
```

Option B: Deno

```
deno task dev
```

Build

Option A: Node

```
npm run build
npm run preview
```

Option B: Deno

```
deno task build
deno task preview
```

Routing Overview

- `/` Home (public)
- `/login` Login (public)
- `/register` Register (public)
- `/customer/dashboard` (auth: CUSTOMER)
- `/customer/service-requests` (auth: CUSTOMER)
- `/customer/new-request` (auth: CUSTOMER)
- `/customer/profile` (auth: CUSTOMER)
- `/professional/dashboard` (auth: PROFESSIONAL)
- `/professional/service-requests` (auth: PROFESSIONAL)
- `/professional/profile` (auth: PROFESSIONAL)
- `/admin/dashboard` (auth: ADMIN)
- `/admin/professionals` (auth: ADMIN)
- `/admin/customers` (auth: ADMIN)
- `/admin/service-requests` (auth: ADMIN)
- `/admin/services` (auth: ADMIN)
- `/:pathMatch(.*)*` NotFound

Authentication

- Access token and role are saved in `localStorage` as `token`, `userRole`, and `user` (JSON).
- Requests are sent via an Axios instance (`src/store/index.js`) that injects the token.
- Navigation guards in `src/router/index.js` enforce `requiresAuth` and role‑based access.

Vite Alias

`vite.config.js` sets `@` to the `src` directory. If your absolute path differs, update:

```
resolve: { alias: { '@': '<absolute-path-to>/base/frontend/src' } }
```

UI

- Bootstrap 5 is imported in `src/main.js`. Components use Bootstrap utility classes.


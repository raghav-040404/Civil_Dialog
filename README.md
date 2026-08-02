# CivilDialog

AI-powered real-time moderation platform that detects toxic language, hate speech, logical fallacies, and negative sentiment while users type.

## Tech Stack

- React 19 + Vite
- Tailwind CSS v4
- React Router DOM
- Axios
- Framer Motion
- Recharts
- React Hook Form
- Context API

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## Demo Credentials

| Email | Password |
|-------|----------|
| admin@civildialog.com | password123 |
| jane@example.com | password123 |

## Environment Variables

Copy `.env.example` to `.env`:

```
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK=true
```

Set `VITE_USE_MOCK=false` when connecting to a real FastAPI backend.

## Project Structure

```
src/
├── components/   # Reusable UI and feature components
├── layouts/      # Page layouts (Auth, Dashboard, Admin)
├── pages/        # Route pages
├── hooks/        # Custom React hooks
├── services/     # API service layer with mock fallbacks
├── context/      # Auth, Theme, Analysis, Toast contexts
├── utils/        # Helpers, constants, token storage
└── routes/       # Application routing
```

## Features

- Landing page with hero, features, and CTA
- JWT authentication (login/register)
- Real-time text analyzer with live highlighting
- AI rewrite panel with accept/copy/replace
- Civility score widget (circular progress)
- Analysis history with search, filter, pagination
- Admin analytics dashboard with charts
- Profile and settings management
- Dark mode support
- Fully responsive design

## API Integration

The frontend expects these FastAPI endpoints:

- `POST /api/auth/login`
- `POST /api/auth/register`
- `POST /api/auth/refresh`
- `POST /api/analyze`
- `GET /api/dashboard/stats`
- `GET /api/history`
- `GET /api/admin/stats`

Mock services are used by default in development (`VITE_USE_MOCK=true`).

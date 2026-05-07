# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sentinel Parking — a smart parking management system with AI license plate recognition, subscription-based billing, real-time map visualization, and hardware webhook integration.

**Tech Stack:**
- **Backend:** Django 4.2+ / DRF / MySQL (tests use SQLite in-memory)
- **Frontend:** Vue 3 + Vite + Element Plus + Tailwind CSS v4 + Pinia
- **AI:** PaddleOCR for license plate recognition

## Architecture

### Backend (Django) — `backend/`

All Django apps live under `backend/apps/`, with `sys.path` modified so they import as top-level modules (e.g., `from accounts.models import User`). `AUTH_USER_MODEL = 'accounts.User'`.

**5 business modules in INSTALLED_APPS + 1 disabled + 1 integration test module:**

| Module | Purpose |
|---|---|
| `accounts` | User auth (JWT + 2FA/TOTP), profile, vehicle CRUD, admin user management |
| `parking` | Parking spaces (SVG map), sessions, reservations, navigation (Dijkstra road-network), AI plate recognition, hardware webhook |
| `payments` | Payments, subscriptions, pricing rules (dynamic), bank cards, top-ups |
| `devices` | IoT device management, fault reporting |
| `dashboard` | Admin dashboard analytics (overview, revenue, occupancy trends) — **NOT in INSTALLED_APPS** but URL route exists |
| `alerts` | Alert/ticket system — **DISABLED** (not in INSTALLED_APPS, no URL mount). Files are stale remnants |
| `integration` | E2E integration tests (vehicle lifecycle, subscription boundaries, permission isolation) |

**Shared config:** `backend/config/` — settings.py, urls.py, wsgi.py, asgi.py

**Key patterns:**
- `ParkingSpace` uses `space_id` (string, e.g., `space_A001`) as business key, numeric `id` as PK
- `is_simulated` flag on Vehicle hides webhook-created vehicles from user's personal list
- Subscription-free parking: `Subscription.objects.filter(user=vehicle.owner, is_active=True, start_date__lte=today, end_date__gte=today)`
- Navigation (`parking/navigation.py`): `RoadNavigator` class builds a graph from road nodes (corridor intersections), connects each spot to its nearest 2 road nodes, then runs Dijkstra. Cross-floor connections via elevator positions. `SpotConnection` records add explicit edges on top. Each `find_path()` call creates a fresh navigator to ensure latest DB state.
- Hardware webhook (`/api/v1/hardware/webhook/`) accepts `space_occupied` / `space_released` events, auto-creates vehicles with `is_simulated=True`
- Quick pay endpoints are `AllowAny` (no login required); `Payment.user` falls back to `session.vehicle.owner` for anonymous requests
- Authentication backend uses `GroupOnlyPermissionBackend` — only group-level and superuser permissions, no direct user permissions
- JWT tokens: 2-hour access, 7-day refresh, with rotation and blacklist

### Frontend (Vue 3) — `frontend/`

| Directory | Purpose |
|---|---|
| `src/api/` | Axios API client + module-specific API functions |
| `src/views/user/` | End-user pages: HomeView, MapView, ReserveView, Payment, Profile |
| `src/views/admin/` | Admin pages |
| `src/components/` | Reusable components (PlateNumberInput, ParkingMapSVG, etc.) |
| `src/stores/` | Pinia stores (auth, plate) |
| `src/layouts/` | Page layouts |
| `src/utils/` | Payment preference, bank card helpers |

**Routing:** Vue Router, frontend dev server runs on port `8180`

**API proxy:** Vite proxies `/api` to `http://127.0.0.1:8080` (configurable via `VITE_API_URL` in `.env`)

**Axios interceptors:**
- `request.js` has a custom `__suppressToast` flag on request config to skip error toasts for expected business errors (e.g., 404 after vehicle exit)

**Alias:** `@` resolves to `frontend/src/`

## Development Commands

### Backend

```bash
cd backend

# Run all tests (uses SQLite in-memory, no MySQL needed)
python manage.py test apps.parking.tests apps.payments.tests apps.accounts.tests apps.dashboard.tests apps.devices.tests apps.integration.tests

# Run a single test
python manage.py test apps.integration.tests.VehicleLifecycleIntegrationTest.test_complete_entry_query_pay_exit

# Run only integration tests
python manage.py test apps.integration.tests

# Start Django dev server
python manage.py runserver        # default port 8000
python manage.py runserver 8080   # specific port (matches frontend proxy default)
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (port 8180, proxies /api to Django on 8080 by default)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Environment

- Django reads credentials from `backend/password.env` (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
- Frontend reads `VITE_API_URL` from `.env` (defaults to `http://127.0.0.1:8080`)
- Tests auto-switch to SQLite in-memory (`settings.py` checks `sys.argv` for `'test'`)
- Locale: `zh-hans`, timezone: `Asia/Shanghai`

## URL Routing

All APIs under `/api/v1/`. Module URL files:
- `accounts/urls.py` — register, profile, vehicles, admin users, 2FA
- `parking/urls.py` — spots, sessions, reservations, navigation, map, webhook
- `payments/urls.py` — payments, subscriptions, plans, pricing, bank cards
- `devices/urls.py` — device CRUD, fault reporting
- `dashboard/urls.py` — overview, analytics (route exists but app not in INSTALLED_APPS)

Compatibility routes at root `urls.py`: `/api/v1/ai/recognize/`, `/api/v1/map/*`, `/api/v1/hardware/webhook/`

JWT endpoints: `/api/v1/auth/token/`, `/api/v1/auth/token/verify-2fa/`, `/api/v1/auth/token/refresh/`

## Key Database Models

- `accounts.User` — Custom user model (phone, status, is_vip, 2FA fields)
- `accounts.Vehicle` — Plate number, owner, is_simulated, is_primary
- `parking.ParkingSpace` — SVG map coordinates, current_plate, reserved_plate, status, floor, node_type
- `parking.ParkingSession` — Vehicle, spot, entry/exit time, amount, payment_status
- `parking.Reservation` — Booking with unique booking_code, status flow: pending→confirmed→completed/cancelled
- `parking.SpotConnection` — Explicit graph edges between spots for navigation
- `payments.Subscription` — User's active subscription with date range
- `payments.PricingRule` — Dynamic pricing (hourly, reservation daily, EV surcharge)
- `payments.Payment` — Payment records (user, session, amount, method, status)
- `devices.Device` — IoT device tracking

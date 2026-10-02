# EVE Healthcare API

A FastAPI backend for diagnostic centre test bookings and simulated payments.

## Stack

- FastAPI and Pydantic v2
- PostgreSQL with SQLAlchemy 2.0
- Alembic migrations
- JWT authentication with bcrypt password hashing
- Docker Compose
- pytest

## Run Locally

Requirements:

- Python 3.12+
- Docker Desktop
- Git

Create the environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and set a long `JWT_SECRET` and `WEBHOOK_SECRET`.

Start PostgreSQL:

```powershell
docker compose up -d db
alembic upgrade head
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

Swagger UI is available at http://127.0.0.1:8000/docs.

To run the test suite:

```powershell
python -m pytest -q
```

Integration tests use `TEST_DATABASE_URL` and a separate database. For example:

```powershell
$env:TEST_DATABASE_URL="postgresql+psycopg://app:app@localhost:5432/eve_healthcare_test"
python -m pytest -q
```

## API Endpoints

Authentication:

- `POST /auth/signup` creates a user.
- `POST /auth/login` returns a bearer JWT.

Centres and tests:

- `GET /centres?page=1&page_size=20` lists centres.
- `GET /centres/{id}` returns a centre and its offered tests with prices.
- `POST /centres` creates a centre and requires an admin JWT.
- `POST /centres/{id}/tests` adds a named test and centre-specific price and requires an admin JWT.

Bookings:

- `POST /bookings` creates an authenticated user's pending booking.
- `GET /bookings?page=1&page_size=20` lists only the caller's bookings.
- `GET /bookings/{id}` returns only the caller's booking.
- `POST /bookings/{id}/cancel` cancels a pending or confirmed booking.

Payments:

- `POST /payments/` simulates payment processing. Use `simulate: "success"` or `simulate: "fail"` for deterministic results; omit it for a random result.
- `POST /payments/webhook/` accepts signed provider updates and does not use JWT authentication.

Example signup:

```json
{
  "email": "patient@example.com",
  "password": "correct horse battery staple"
}
```

Example booking:

```json
{
  "centre_id": "00000000-0000-0000-0000-000000000000",
  "test_id": "00000000-0000-0000-0000-000000000000",
  "appointment_at": "2030-01-15T10:00:00Z"
}
```

Example simulated payment:

```json
{
  "booking_id": "00000000-0000-0000-0000-000000000000",
  "simulate": "success"
}
```

The webhook signature is the lowercase hexadecimal HMAC-SHA256 of the exact JSON request body, using `WEBHOOK_SECRET`, sent in `X-Webhook-Signature`.

## Database Design

- `users` stores credentials and the admin flag.
- `centres` stores diagnostic centre details.
- `tests` is the shared diagnostic test catalogue.
- `centre_tests` associates tests with centres and stores the centre-specific `NUMERIC(10,2)` price.
- `bookings` stores the user, centre, test, appointment, status, and an immutable price snapshot.
- `payments` stores each simulated payment attempt and its unique provider reference.
- `webhook_events` stores unique provider event IDs for idempotent processing.

UUID identifiers, foreign keys, unique constraints, indexes, and database enums protect the core data model.

## Important Assumptions

- Appointment timestamps must include a timezone and must be in the future.
- A user can access only their own bookings; another user's booking is reported as `404`.
- A test is created in the catalogue when it is first assigned to a centre.
- Payments are allowed only for pending or failed bookings.
- Payment and booking updates happen in the same database transaction.
- Webhook events are authenticated before processing and are never allowed to create payments or bookings.

Booking transitions are centralized:

- `PENDING` -> `CONFIRMED`, `FAILED`, or `CANCELLED`
- `FAILED` -> `CONFIRMED`
- `CONFIRMED` -> `CANCELLED`
- `CANCELLED` is terminal

## Scope and Future Improvements

The assignment scope intentionally excludes Redis, Celery, rate limiting, refresh tokens, email verification, capacity management, and real payment providers.

With more time, Celery could process webhooks asynchronously with retries, Redis could cache centre listings, rate limiting could protect authentication and webhook endpoints, and a real provider adapter could replace the simulator while preserving the payment service contract.

Stack (decided)
FastAPI with Pydantic v2. Swagger/OpenAPI comes free, which covers a bonus item.
PostgreSQL with SQLAlchemy 2.0 and Alembic migrations.
JWT via PyJWT, with passwords hashed using bcrypt or argon2.
pytest with a separate test database.
Docker + docker-compose (app + postgres). One command to run is a big README win.
Data model
users: id, email (unique), password_hash, is_admin, created_at
centres: id, name, location
tests: id, name (the catalog entry, e.g. "CBC")
centre_tests: centre_id, test_id, price. Unique on (centre_id, test_id). Price lives here because the same test costs different amounts at different centres.
bookings: id, user_id, centre_id, test_id, appointment_at, amount, status, created_at
payments: id, booking_id, amount, status (PENDING/SUCCESS/FAILED), provider_reference (unique), created_at
webhook_events: event_id (unique), payload, processed_at

Key decisions:

Booking.amount is a snapshot of the price at booking time. If the price changes later, old bookings stay correct. Interviewers like this.
Use Numeric(10,2) for money, never float.
Add DB-level constraints and indexes (foreign keys, uniques, index on bookings.user_id and payments.provider_reference).
Booking state machine

Put all transitions in one function so no endpoint sets status directly:

PENDING to CONFIRMED (payment success), FAILED (payment failed), or CANCELLED (user cancels)
FAILED to CONFIRMED (retry succeeded). A new payment attempt is allowed on PENDING or FAILED bookings.
CONFIRMED to CANCELLED
CANCELLED is terminal, and a CONFIRMED booking cannot go back to FAILED.
Payment and webhook flow (the core of the grading)

POST /payments/ takes booking_id (plus an optional simulate: success|fail field so your tests are deterministic, random otherwise).

Verify the booking belongs to the caller and is payable.
Create a payment row with a generated provider_reference.
Simulate the outcome, then update payment and booking in one transaction.

POST /payments/webhook/ takes event_id, provider_reference, status.

Verify an HMAC signature header using a shared secret from env. This is a cheap, impressive touch, and the webhook does not use JWT.
Insert into webhook_events. If event_id already exists, return 200 with "already processed" and do nothing. The unique constraint is the real guarantee, not an if-check.
Lock the payment row with SELECT ... FOR UPDATE, apply the status through the state machine, and ignore out-of-order or downgrade events (e.g. FAILED arriving after SUCCESS).
Never create a new payment or booking from a webhook. It only updates existing ones.
Endpoints
Auth: POST /auth/signup, POST /auth/login
Centres: GET /centres (paginated), GET /centres/{id} with its tests, POST /centres and POST /centres/{id}/tests (admin only)
Bookings: POST /bookings, GET /bookings (own only, paginated), GET /bookings/{id}, POST /bookings/{id}/cancel
Payments: POST /payments/, POST /payments/webhook/

Authorization rule: accessing someone else's booking returns 404, not 403, so IDs can't be probed. Admin-only creation needs only an is_admin flag and a seed script.

Edge cases to handle explicitly (and test)
Duplicate signup email gives 409; wrong credentials give a generic 401.
Appointment time in the past gives 422.
The test must actually be offered at that centre.
Invalid or nonexistent booking ID gives 404; malformed IDs give 422.
Paying for an already CONFIRMED or CANCELLED booking gives 409.
Duplicate webhook, bad signature, unknown provider_reference, and out-of-order events.
Two concurrent payment requests for the same booking (row lock).
Scope: include vs skip

Include: everything above, Docker, pytest, pagination, Swagger, light structured logging (JSON logs with request and booking IDs), webhook HMAC.

Skip: Redis, Celery, rate limiting, refresh tokens, slot capacity, email verification. Each adds surface area that could be wrong. In the README's "what I'd improve" section, say how you'd add them (e.g. Celery for async webhook processing with retries, Redis for caching centre listings). That gets you the thinking credit without the risk.

Folder structure
app/
  main.py
  core/        (config, security, logging)
  db/          (session, base)
  models/
  schemas/
  api/         (routers: auth, centres, bookings, payments)
  services/    (booking_service, payment_service, state machine)
tests/
alembic/
Dockerfile
docker-compose.yml
README.md

Keep routers thin and put the logic in services/, which is what "maintainable" looks like to a reviewer.
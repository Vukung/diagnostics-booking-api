# EVE Healthcare Backend Execution Plan

This checklist turns `ARCHITECTURE.md` and the assignment brief into implementation milestones. Each milestone must be validated and committed before the next one begins.

## Prerequisites

- [x] Install Python 3.11 or newer
- [ ] Install Docker Desktop and ensure it is running
- [x] Install Git
- [ ] Verify installations:
  ```powershell
  python --version
  docker --version
  docker compose version
  git --version
  ```
- [x] Create and activate a virtual environment:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- [x] Upgrade pip and install project dependencies:
  ```powershell
  python -m pip install --upgrade pip
  python -m pip install -e ".[dev]"
  ```
- [ ] Create a local `.env` file with database, JWT, and webhook settings
- [ ] Confirm `.env` is ignored by Git

## Milestone 1: Skeleton, Docker, Database, and Migrations

- [x] Create the FastAPI application entry point
- [x] Create the planned application package structure
- [x] Add application configuration
- [x] Add PostgreSQL Docker Compose service
- [x] Add the API Dockerfile
- [x] Configure SQLAlchemy 2.0 and the database session
- [x] Define the database base and initial models
- [x] Configure Alembic
- [x] Create the initial migration
- [x] Add a health endpoint
- [x] Validate Python compilation
- [x] Validate migration rendering/application
- [ ] Validate Docker Compose configuration
- [x] Commit: `milestone 1: project foundation`

## Milestone 2: Authentication

- [x] Add user signup
- [x] Add user login
- [x] Hash passwords securely
- [x] Create and validate JWT access tokens
- [x] Add the authenticated-user dependency
- [x] Reject duplicate signup emails with `409`
- [x] Return generic `401` responses for invalid credentials
- [x] Add the admin seed script
- [x] Validate password hashing and verification
- [x] Validate JWT creation and decoding
- [x] Validate signup and login route registration
- [x] Resolve and rerun the currently failing auth validation command
- [ ] Commit: `milestone 2: authentication`

## Milestone 3: Diagnostic Centres and Tests

- [x] Add paginated `GET /centres`
- [x] Add `GET /centres/{id}` with offered tests and prices
- [x] Add admin-only `POST /centres`
- [x] Add admin-only `POST /centres/{id}/tests`
- [x] Enforce unique centre/test pairs
- [x] Validate request data and nonexistent IDs
- [x] Validate admin authorization
- [x] Validate pagination
- [x] Commit: `milestone 3: centres and tests`

## Milestone 4: Bookings and State Machine

- [x] Add booking creation
- [x] Verify the requested test is offered at the selected centre
- [x] Reject appointments in the past with `422`
- [x] Snapshot the centre/test price into `Booking.amount`
- [x] Add paginated own-bookings listing
- [x] Add booking detail endpoint
- [x] Return `404` when accessing another user's booking
- [x] Add booking cancellation
- [x] Implement all booking status transitions in one service function
- [x] Prevent invalid and terminal state transitions
- [x] Validate malformed and nonexistent booking IDs
- [ ] Commit: `milestone 4: bookings and state machine`

## Milestone 5: Payments and Webhook

- [x] Add `POST /payments/`
- [x] Support deterministic `success` and `fail` simulation values
- [x] Allow payment only for payable bookings
- [x] Create payment records with unique provider references
- [x] Update payment and booking status transactionally
- [x] Add row locking for concurrent payment requests
- [x] Add `POST /payments/webhook/`
- [x] Verify the webhook HMAC signature
- [x] Store webhook event IDs with a unique constraint
- [x] Return success without changing state for duplicate events
- [x] Lock the payment row while applying webhook updates
- [x] Ignore unknown provider references safely
- [x] Ignore out-of-order and downgrade events
- [x] Ensure webhooks never create bookings or payments
- [ ] Commit: `milestone 5: payments and webhook`

## Milestone 6: Tests

- [x] Configure pytest
- [x] Configure a separate test database
- [x] Add authentication tests
- [ ] Add duplicate signup and invalid credential tests
- [ ] Add centre and test authorization tests
- [ ] Add pagination tests
- [ ] Add booking validation and ownership tests
- [x] Add booking state-transition tests
- [x] Add payment success and failure tests
- [ ] Add concurrent payment protection tests
- [ ] Add webhook signature tests
- [ ] Add duplicate webhook idempotency tests
- [x] Add out-of-order payment event tests
- [x] Run the complete test suite
- [ ] Commit: `milestone 6: test coverage`

## Milestone 7: README and Submission Documentation

- [x] Document local setup
- [x] Document Docker Compose startup
- [x] Document migration commands
- [x] Document API endpoints
- [x] Add example requests and responses
- [x] Document database/schema design
- [x] Document important assumptions
- [x] Document the state machine and webhook idempotency behavior
- [x] Document what would be improved with more time
- [x] Confirm required submission files are present
- [x] Run the final test suite
- [ ] Commit: `milestone 7: documentation`

## Final Review

- [ ] Confirm no uncommitted implementation changes remain
- [ ] Confirm `.env` and secrets are not committed
- [ ] Confirm Docker Compose starts the application and PostgreSQL
- [ ] Confirm Alembic migrations apply from an empty database
- [ ] Confirm Swagger is available at `/docs`
- [ ] Confirm the README setup instructions work from a clean checkout
- [ ] Confirm all assignment edge cases are covered by tests

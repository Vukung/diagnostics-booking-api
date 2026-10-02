from app.main import app


def test_required_routes_are_documented() -> None:
    paths = set(app.openapi()["paths"])

    assert {
        "/auth/signup",
        "/auth/login",
        "/centres",
        "/centres/{centre_id}",
        "/centres/{centre_id}/tests",
        "/bookings",
        "/bookings/{booking_id}",
        "/bookings/{booking_id}/cancel",
        "/payments/",
        "/payments/webhook/",
    } <= paths
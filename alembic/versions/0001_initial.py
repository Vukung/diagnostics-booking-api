"""create initial schema"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    booking_status = sa.Enum("PENDING", "CONFIRMED", "FAILED", "CANCELLED", name="bookingstatus", create_type=False)
    payment_status = sa.Enum("PENDING", "SUCCESS", "FAILED", name="paymentstatus", create_type=False)
    booking_status.create(op.get_bind(), checkfirst=True)
    payment_status.create(op.get_bind(), checkfirst=True)
    op.create_table("users", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("email", sa.String(320), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("is_admin", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("email"))
    op.create_table("centres", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("name", sa.String(200), nullable=False), sa.Column("location", sa.String(300), nullable=False))
    op.create_table("tests", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("name", sa.String(200), nullable=False))
    op.create_table("centre_tests", sa.Column("centre_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("centres.id", ondelete="CASCADE"), primary_key=True), sa.Column("test_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tests.id", ondelete="CASCADE"), primary_key=True), sa.Column("price", sa.Numeric(10, 2), nullable=False), sa.UniqueConstraint("centre_id", "test_id", name="uq_centre_test"))
    op.create_table("bookings", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False), sa.Column("centre_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("centres.id"), nullable=False), sa.Column("test_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tests.id"), nullable=False), sa.Column("appointment_at", sa.DateTime(timezone=True), nullable=False), sa.Column("amount", sa.Numeric(10, 2), nullable=False), sa.Column("status", booking_status, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_bookings_user_id", "bookings", ["user_id"])
    op.create_table("payments", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("booking_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bookings.id"), nullable=False), sa.Column("amount", sa.Numeric(10, 2), nullable=False), sa.Column("status", payment_status, nullable=False), sa.Column("provider_reference", sa.String(100), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("provider_reference"))
    op.create_index("ix_payments_provider_reference", "payments", ["provider_reference"])
    op.create_table("webhook_events", sa.Column("event_id", sa.String(200), primary_key=True), sa.Column("payload", postgresql.JSONB(), nullable=False), sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    op.drop_table("webhook_events")
    op.drop_index("ix_payments_provider_reference", table_name="payments")
    op.drop_table("payments")
    op.drop_index("ix_bookings_user_id", table_name="bookings")
    op.drop_table("bookings")
    op.drop_table("centre_tests")
    op.drop_table("tests")
    op.drop_table("centres")
    op.drop_table("users")
    sa.Enum(name="paymentstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="bookingstatus").drop(op.get_bind(), checkfirst=True)
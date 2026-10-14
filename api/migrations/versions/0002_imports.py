"""Imports : dépôts de fichiers et valeurs réalisées

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-10
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "import_batches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_sha256", sa.String(64), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("uploaded_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("rows_read", sa.Integer(), nullable=False),
        sa.Column("rows_kept", sa.Integer(), nullable=False),
        sa.Column("rows_ignored", sa.Integer(), nullable=False),
        sa.Column("months", sa.JSON(), nullable=False),
        sa.Column("errors", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("records", sa.JSON(), nullable=True),
        sa.Column(
            "warnings_confirmed", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.create_index("ix_import_batches_kind_status", "import_batches", ["kind", "status"])

    op.create_table(
        "actual_values",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("city_code", sa.String(8), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("metric", sa.String(64), nullable=False),
        sa.Column("seniority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column(
            "batch_id", sa.Integer(), sa.ForeignKey("import_batches.id"), nullable=False
        ),
        sa.UniqueConstraint(
            "source", "city_code", "month", "metric", "seniority", name="uq_actual_value"
        ),
    )
    op.create_index("ix_actual_values_source_month", "actual_values", ["source", "month"])


def downgrade() -> None:
    op.drop_index("ix_actual_values_source_month", table_name="actual_values")
    op.drop_table("actual_values")
    op.drop_index("ix_import_batches_kind_status", table_name="import_batches")
    op.drop_table("import_batches")

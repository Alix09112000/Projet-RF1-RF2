"""Saisie des hypothèses, paramètres de la ville, table List

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-14
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assumption_values",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("version_id", sa.Integer(), sa.ForeignKey("forecast_versions.id"),
                  nullable=False),
        sa.Column("module", sa.String(16), nullable=False),
        sa.Column("row", sa.Integer(), nullable=False),
        sa.Column("slot", sa.Integer(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("version_id", "module", "row", "slot", name="uq_assumption_cell"),
    )
    op.create_table(
        "assumption_changes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("version_id", sa.Integer(), sa.ForeignKey("forecast_versions.id"),
                  nullable=False),
        sa.Column("module", sa.String(16), nullable=False),
        sa.Column("row", sa.Integer(), nullable=False),
        sa.Column("slot", sa.Integer(), nullable=False),
        sa.Column("old_value", sa.Float(), nullable=True),
        sa.Column("new_value", sa.Float(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_assumption_changes_cell", "assumption_changes", ["version_id", "module", "row"]
    )
    op.create_table(
        "city_parameters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(32), nullable=False, unique=True),
        sa.Column("value", sa.String(255), nullable=False),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "list_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity", sa.String(120), nullable=False),
        sa.Column("country", sa.String(120), nullable=False),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("source_row", sa.Integer(), nullable=False),
        sa.UniqueConstraint("entity", "city", name="uq_list_entry"),
    )


def downgrade() -> None:
    op.drop_table("list_entries")
    op.drop_table("city_parameters")
    op.drop_index("ix_assumption_changes_cell", table_name="assumption_changes")
    op.drop_table("assumption_changes")
    op.drop_table("assumption_values")

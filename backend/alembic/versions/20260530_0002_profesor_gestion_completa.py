"""profesor gestion completa

Revision ID: 20260530_0002
Revises: 20260519_0001
Create Date: 2026-05-30
"""
from alembic import op
import sqlalchemy as sa

revision = "20260530_0002"
down_revision = "20260519_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("profesores", sa.Column("rut", sa.String(length=12), nullable=True))
    op.add_column("profesores", sa.Column("especialidad", sa.String(length=120), nullable=True))
    op.add_column("profesores", sa.Column("activo", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.create_index(op.f("ix_profesores_rut"), "profesores", ["rut"], unique=True)
    op.alter_column("profesores", "activo", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_profesores_rut"), table_name="profesores")
    op.drop_column("profesores", "activo")
    op.drop_column("profesores", "especialidad")
    op.drop_column("profesores", "rut")

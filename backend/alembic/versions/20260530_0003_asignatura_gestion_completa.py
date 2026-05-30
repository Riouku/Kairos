"""asignatura gestion completa

Revision ID: 20260530_0003
Revises: 20260530_0002
Create Date: 2026-05-30
"""
from alembic import op
import sqlalchemy as sa

revision = "20260530_0003"
down_revision = "20260530_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("asignaturas", sa.Column("nivel", sa.String(length=80), nullable=True))
    op.add_column("asignaturas", sa.Column("horas_semanales", sa.Integer(), nullable=True))
    op.add_column("asignaturas", sa.Column("activo", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.alter_column("asignaturas", "activo", server_default=None)


def downgrade() -> None:
    op.drop_column("asignaturas", "activo")
    op.drop_column("asignaturas", "horas_semanales")
    op.drop_column("asignaturas", "nivel")

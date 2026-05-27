"""initial schema

Revision ID: 20260519_0001
Revises:
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa

revision = "20260519_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profesores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellido", sa.String(length=100), nullable=False),
        sa.Column("correo", sa.String(length=150), nullable=False),
        sa.Column("telefono", sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_profesores_correo"), "profesores", ["correo"], unique=True)
    op.create_index(op.f("ix_profesores_id"), "profesores", ["id"], unique=False)

    op.create_table(
        "asignaturas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("codigo", sa.String(length=20), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_asignaturas_codigo"), "asignaturas", ["codigo"], unique=True)
    op.create_index(op.f("ix_asignaturas_id"), "asignaturas", ["id"], unique=False)

    op.create_table(
        "asignaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profesor_id", sa.Integer(), nullable=False),
        sa.Column("asignatura_id", sa.Integer(), nullable=False),
        sa.Column("fecha_asignacion", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
        sa.ForeignKeyConstraint(["asignatura_id"], ["asignaturas.id"]),
        sa.ForeignKeyConstraint(["profesor_id"], ["profesores.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profesor_id", "asignatura_id", name="uq_profesor_asignatura"),
    )
    op.create_index(op.f("ix_asignaciones_asignatura_id"), "asignaciones", ["asignatura_id"], unique=False)
    op.create_index(op.f("ix_asignaciones_id"), "asignaciones", ["id"], unique=False)
    op.create_index(op.f("ix_asignaciones_profesor_id"), "asignaciones", ["profesor_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_asignaciones_profesor_id"), table_name="asignaciones")
    op.drop_index(op.f("ix_asignaciones_id"), table_name="asignaciones")
    op.drop_index(op.f("ix_asignaciones_asignatura_id"), table_name="asignaciones")
    op.drop_table("asignaciones")
    op.drop_index(op.f("ix_asignaturas_id"), table_name="asignaturas")
    op.drop_index(op.f("ix_asignaturas_codigo"), table_name="asignaturas")
    op.drop_table("asignaturas")
    op.drop_index(op.f("ix_profesores_id"), table_name="profesores")
    op.drop_index(op.f("ix_profesores_correo"), table_name="profesores")
    op.drop_table("profesores")

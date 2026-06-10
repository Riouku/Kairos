"""asistencias

Revision ID: 20260616_0006
Revises: 20260609_0005
Create Date: 2026-06-16
"""
from alembic import op
import sqlalchemy as sa


revision = "20260616_0006"
down_revision = "20260609_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "asistencias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("estudiante_id", sa.Integer(), nullable=False),
        sa.Column("curso_id", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("observacion", sa.Text(), nullable=True),
        sa.Column("anio_academico", sa.Integer(), nullable=False),
        sa.Column("fecha_registro", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["curso_id"], ["cursos.id"]),
        sa.ForeignKeyConstraint(["estudiante_id"], ["estudiantes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("estudiante_id", "fecha", name="uq_asistencia_estudiante_fecha"),
    )
    op.create_index(op.f("ix_asistencias_anio_academico"), "asistencias", ["anio_academico"], unique=False)
    op.create_index(op.f("ix_asistencias_curso_id"), "asistencias", ["curso_id"], unique=False)
    op.create_index(op.f("ix_asistencias_estado"), "asistencias", ["estado"], unique=False)
    op.create_index(op.f("ix_asistencias_estudiante_id"), "asistencias", ["estudiante_id"], unique=False)
    op.create_index(op.f("ix_asistencias_fecha"), "asistencias", ["fecha"], unique=False)
    op.create_index(op.f("ix_asistencias_id"), "asistencias", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_asistencias_id"), table_name="asistencias")
    op.drop_index(op.f("ix_asistencias_fecha"), table_name="asistencias")
    op.drop_index(op.f("ix_asistencias_estudiante_id"), table_name="asistencias")
    op.drop_index(op.f("ix_asistencias_estado"), table_name="asistencias")
    op.drop_index(op.f("ix_asistencias_curso_id"), table_name="asistencias")
    op.drop_index(op.f("ix_asistencias_anio_academico"), table_name="asistencias")
    op.drop_table("asistencias")

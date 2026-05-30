"""calendario academico

Revision ID: 20260604_0004
Revises: 20260530_0003
Create Date: 2026-06-04
"""
from alembic import op
import sqlalchemy as sa


revision = "20260604_0004"
down_revision = "20260530_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cursos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("nivel", sa.String(length=80), nullable=False),
        sa.Column("letra", sa.String(length=5), nullable=True),
        sa.Column("jornada", sa.String(length=30), nullable=False),
        sa.Column("anio_academico", sa.Integer(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre", "jornada", "anio_academico", name="uq_curso_nombre_jornada_anio"),
    )
    op.create_index(op.f("ix_cursos_anio_academico"), "cursos", ["anio_academico"], unique=False)
    op.create_index(op.f("ix_cursos_id"), "cursos", ["id"], unique=False)

    op.create_table(
        "eventos_academicos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=150), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("fecha_inicio", sa.DateTime(), nullable=False),
        sa.Column("fecha_fin", sa.DateTime(), nullable=True),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("curso_id", sa.Integer(), nullable=True),
        sa.Column("profesor_id", sa.Integer(), nullable=True),
        sa.Column("asignatura_id", sa.Integer(), nullable=True),
        sa.Column("anio_academico", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["asignatura_id"], ["asignaturas.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["curso_id"], ["cursos.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["profesor_id"], ["profesores.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_eventos_academicos_anio_academico"), "eventos_academicos", ["anio_academico"], unique=False)
    op.create_index(op.f("ix_eventos_academicos_asignatura_id"), "eventos_academicos", ["asignatura_id"], unique=False)
    op.create_index(op.f("ix_eventos_academicos_curso_id"), "eventos_academicos", ["curso_id"], unique=False)
    op.create_index(op.f("ix_eventos_academicos_estado"), "eventos_academicos", ["estado"], unique=False)
    op.create_index(op.f("ix_eventos_academicos_fecha_fin"), "eventos_academicos", ["fecha_fin"], unique=False)
    op.create_index(op.f("ix_eventos_academicos_fecha_inicio"), "eventos_academicos", ["fecha_inicio"], unique=False)
    op.create_index(op.f("ix_eventos_academicos_id"), "eventos_academicos", ["id"], unique=False)
    op.create_index(op.f("ix_eventos_academicos_profesor_id"), "eventos_academicos", ["profesor_id"], unique=False)
    op.create_index(op.f("ix_eventos_academicos_tipo"), "eventos_academicos", ["tipo"], unique=False)

    op.create_table(
        "horarios_clases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("curso_id", sa.Integer(), nullable=False),
        sa.Column("profesor_id", sa.Integer(), nullable=False),
        sa.Column("asignatura_id", sa.Integer(), nullable=False),
        sa.Column("dia_semana", sa.Integer(), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=False),
        sa.Column("hora_fin", sa.Time(), nullable=False),
        sa.Column("anio_academico", sa.Integer(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["asignatura_id"], ["asignaturas.id"]),
        sa.ForeignKeyConstraint(["curso_id"], ["cursos.id"]),
        sa.ForeignKeyConstraint(["profesor_id"], ["profesores.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_horarios_clases_activo"), "horarios_clases", ["activo"], unique=False)
    op.create_index(op.f("ix_horarios_clases_anio_academico"), "horarios_clases", ["anio_academico"], unique=False)
    op.create_index(op.f("ix_horarios_clases_asignatura_id"), "horarios_clases", ["asignatura_id"], unique=False)
    op.create_index(op.f("ix_horarios_clases_curso_id"), "horarios_clases", ["curso_id"], unique=False)
    op.create_index(op.f("ix_horarios_clases_dia_semana"), "horarios_clases", ["dia_semana"], unique=False)
    op.create_index(op.f("ix_horarios_clases_id"), "horarios_clases", ["id"], unique=False)
    op.create_index(op.f("ix_horarios_clases_profesor_id"), "horarios_clases", ["profesor_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_horarios_clases_profesor_id"), table_name="horarios_clases")
    op.drop_index(op.f("ix_horarios_clases_id"), table_name="horarios_clases")
    op.drop_index(op.f("ix_horarios_clases_dia_semana"), table_name="horarios_clases")
    op.drop_index(op.f("ix_horarios_clases_curso_id"), table_name="horarios_clases")
    op.drop_index(op.f("ix_horarios_clases_asignatura_id"), table_name="horarios_clases")
    op.drop_index(op.f("ix_horarios_clases_anio_academico"), table_name="horarios_clases")
    op.drop_index(op.f("ix_horarios_clases_activo"), table_name="horarios_clases")
    op.drop_table("horarios_clases")

    op.drop_index(op.f("ix_eventos_academicos_tipo"), table_name="eventos_academicos")
    op.drop_index(op.f("ix_eventos_academicos_profesor_id"), table_name="eventos_academicos")
    op.drop_index(op.f("ix_eventos_academicos_id"), table_name="eventos_academicos")
    op.drop_index(op.f("ix_eventos_academicos_fecha_inicio"), table_name="eventos_academicos")
    op.drop_index(op.f("ix_eventos_academicos_fecha_fin"), table_name="eventos_academicos")
    op.drop_index(op.f("ix_eventos_academicos_estado"), table_name="eventos_academicos")
    op.drop_index(op.f("ix_eventos_academicos_curso_id"), table_name="eventos_academicos")
    op.drop_index(op.f("ix_eventos_academicos_asignatura_id"), table_name="eventos_academicos")
    op.drop_index(op.f("ix_eventos_academicos_anio_academico"), table_name="eventos_academicos")
    op.drop_table("eventos_academicos")

    op.drop_index(op.f("ix_cursos_id"), table_name="cursos")
    op.drop_index(op.f("ix_cursos_anio_academico"), table_name="cursos")
    op.drop_table("cursos")

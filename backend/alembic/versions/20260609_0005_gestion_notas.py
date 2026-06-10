"""gestion notas

Revision ID: 20260609_0005
Revises: 20260604_0004
Create Date: 2026-06-09
"""
from alembic import op
import sqlalchemy as sa


revision = "20260609_0005"
down_revision = "20260604_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "estudiantes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rut", sa.String(length=12), nullable=True),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellido", sa.String(length=100), nullable=False),
        sa.Column("correo", sa.String(length=150), nullable=True),
        sa.Column("curso_id", sa.Integer(), nullable=False),
        sa.Column("anio_academico", sa.Integer(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["curso_id"], ["cursos.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("correo"),
        sa.UniqueConstraint("rut"),
    )
    op.create_index(op.f("ix_estudiantes_anio_academico"), "estudiantes", ["anio_academico"], unique=False)
    op.create_index(op.f("ix_estudiantes_correo"), "estudiantes", ["correo"], unique=True)
    op.create_index(op.f("ix_estudiantes_curso_id"), "estudiantes", ["curso_id"], unique=False)
    op.create_index(op.f("ix_estudiantes_id"), "estudiantes", ["id"], unique=False)
    op.create_index(op.f("ix_estudiantes_rut"), "estudiantes", ["rut"], unique=True)

    op.create_table(
        "periodos_academicos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin", sa.Date(), nullable=False),
        sa.Column("anio_academico", sa.Integer(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre", "anio_academico", name="uq_periodo_nombre_anio"),
    )
    op.create_index(op.f("ix_periodos_academicos_anio_academico"), "periodos_academicos", ["anio_academico"], unique=False)
    op.create_index(op.f("ix_periodos_academicos_id"), "periodos_academicos", ["id"], unique=False)

    op.create_table(
        "evaluaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=150), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("curso_id", sa.Integer(), nullable=False),
        sa.Column("asignatura_id", sa.Integer(), nullable=False),
        sa.Column("profesor_id", sa.Integer(), nullable=False),
        sa.Column("periodo_id", sa.Integer(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("ponderacion", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("anio_academico", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["asignatura_id"], ["asignaturas.id"]),
        sa.ForeignKeyConstraint(["curso_id"], ["cursos.id"]),
        sa.ForeignKeyConstraint(["periodo_id"], ["periodos_academicos.id"]),
        sa.ForeignKeyConstraint(["profesor_id"], ["profesores.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evaluaciones_anio_academico"), "evaluaciones", ["anio_academico"], unique=False)
    op.create_index(op.f("ix_evaluaciones_asignatura_id"), "evaluaciones", ["asignatura_id"], unique=False)
    op.create_index(op.f("ix_evaluaciones_curso_id"), "evaluaciones", ["curso_id"], unique=False)
    op.create_index(op.f("ix_evaluaciones_estado"), "evaluaciones", ["estado"], unique=False)
    op.create_index(op.f("ix_evaluaciones_fecha"), "evaluaciones", ["fecha"], unique=False)
    op.create_index(op.f("ix_evaluaciones_id"), "evaluaciones", ["id"], unique=False)
    op.create_index(op.f("ix_evaluaciones_periodo_id"), "evaluaciones", ["periodo_id"], unique=False)
    op.create_index(op.f("ix_evaluaciones_profesor_id"), "evaluaciones", ["profesor_id"], unique=False)

    op.create_table(
        "notas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("estudiante_id", sa.Integer(), nullable=False),
        sa.Column("evaluacion_id", sa.Integer(), nullable=False),
        sa.Column("nota", sa.Numeric(precision=3, scale=1), nullable=False),
        sa.Column("observacion", sa.Text(), nullable=True),
        sa.Column("fecha_registro", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["estudiante_id"], ["estudiantes.id"]),
        sa.ForeignKeyConstraint(["evaluacion_id"], ["evaluaciones.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("estudiante_id", "evaluacion_id", name="uq_nota_estudiante_evaluacion"),
    )
    op.create_index(op.f("ix_notas_estudiante_id"), "notas", ["estudiante_id"], unique=False)
    op.create_index(op.f("ix_notas_evaluacion_id"), "notas", ["evaluacion_id"], unique=False)
    op.create_index(op.f("ix_notas_id"), "notas", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notas_id"), table_name="notas")
    op.drop_index(op.f("ix_notas_evaluacion_id"), table_name="notas")
    op.drop_index(op.f("ix_notas_estudiante_id"), table_name="notas")
    op.drop_table("notas")

    op.drop_index(op.f("ix_evaluaciones_profesor_id"), table_name="evaluaciones")
    op.drop_index(op.f("ix_evaluaciones_periodo_id"), table_name="evaluaciones")
    op.drop_index(op.f("ix_evaluaciones_id"), table_name="evaluaciones")
    op.drop_index(op.f("ix_evaluaciones_fecha"), table_name="evaluaciones")
    op.drop_index(op.f("ix_evaluaciones_estado"), table_name="evaluaciones")
    op.drop_index(op.f("ix_evaluaciones_curso_id"), table_name="evaluaciones")
    op.drop_index(op.f("ix_evaluaciones_asignatura_id"), table_name="evaluaciones")
    op.drop_index(op.f("ix_evaluaciones_anio_academico"), table_name="evaluaciones")
    op.drop_table("evaluaciones")

    op.drop_index(op.f("ix_periodos_academicos_id"), table_name="periodos_academicos")
    op.drop_index(op.f("ix_periodos_academicos_anio_academico"), table_name="periodos_academicos")
    op.drop_table("periodos_academicos")

    op.drop_index(op.f("ix_estudiantes_rut"), table_name="estudiantes")
    op.drop_index(op.f("ix_estudiantes_id"), table_name="estudiantes")
    op.drop_index(op.f("ix_estudiantes_curso_id"), table_name="estudiantes")
    op.drop_index(op.f("ix_estudiantes_correo"), table_name="estudiantes")
    op.drop_index(op.f("ix_estudiantes_anio_academico"), table_name="estudiantes")
    op.drop_table("estudiantes")

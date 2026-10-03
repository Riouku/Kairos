"""Agregar apoderados y vinculos con estudiantes."""
from alembic import op
import sqlalchemy as sa


revision = "20261003_0012"
down_revision = "20261003_0011"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "apoderados",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rut", sa.String(length=12), nullable=True),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellido", sa.String(length=100), nullable=False),
        sa.Column("correo", sa.String(length=150), nullable=True),
        sa.Column("telefono", sa.String(length=30), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("rut", name="uq_apoderados_rut"),
    )
    op.create_index("ix_apoderados_correo", "apoderados", ["correo"])
    op.create_index("ix_apoderados_activo", "apoderados", ["activo"])
    op.create_table(
        "apoderados_estudiantes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("apoderado_id", sa.Integer(), sa.ForeignKey("apoderados.id", ondelete="CASCADE"), nullable=False),
        sa.Column("estudiante_id", sa.Integer(), sa.ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parentesco", sa.String(length=50), nullable=True),
        sa.Column("recibe_avisos", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("apoderado_id", "estudiante_id", name="uq_apoderado_estudiante"),
    )
    op.create_index("ix_apoderados_estudiantes_apoderado_id", "apoderados_estudiantes", ["apoderado_id"])
    op.create_index("ix_apoderados_estudiantes_estudiante_id", "apoderados_estudiantes", ["estudiante_id"])


def downgrade():
    op.drop_table("apoderados_estudiantes")
    op.drop_table("apoderados")

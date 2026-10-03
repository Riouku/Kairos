"""Crear cuentas de acceso y sesiones para alumnos."""
from alembic import op
import sqlalchemy as sa


revision = "20261002_0010"
down_revision = "20261002_0009"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cuentas_estudiante",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("estudiante_id", sa.Integer(), sa.ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("correo", sa.String(length=150), nullable=False),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("estudiante_id", name="uq_cuentas_estudiante_estudiante_id"),
        sa.UniqueConstraint("correo", name="uq_cuentas_estudiante_correo"),
    )
    op.create_index("ix_cuentas_estudiante_estudiante_id", "cuentas_estudiante", ["estudiante_id"])
    op.create_index("ix_cuentas_estudiante_correo", "cuentas_estudiante", ["correo"])
    op.create_table(
        "sesiones_usuario",
        sa.Column("token_hash", sa.String(length=64), primary_key=True),
        sa.Column("rol", sa.String(length=20), nullable=False),
        sa.Column("cuenta_estudiante_id", sa.Integer(), sa.ForeignKey("cuentas_estudiante.id", ondelete="CASCADE"), nullable=True),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("creada_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_sesiones_usuario_cuenta_estudiante_id", "sesiones_usuario", ["cuenta_estudiante_id"])
    op.create_index("ix_sesiones_usuario_expira_en", "sesiones_usuario", ["expira_en"])


def downgrade():
    op.drop_table("sesiones_usuario")
    op.drop_table("cuentas_estudiante")

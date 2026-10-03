"""Agregar tokens temporales de recuperación de contraseña."""
from alembic import op
import sqlalchemy as sa


revision = "20261003_0011"
down_revision = "20261002_0010"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tokens_recuperacion",
        sa.Column("token_hash", sa.String(length=64), primary_key=True),
        sa.Column("cuenta_estudiante_id", sa.Integer(), sa.ForeignKey("cuentas_estudiante.id", ondelete="CASCADE"), nullable=False),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_tokens_recuperacion_cuenta_estudiante_id", "tokens_recuperacion", ["cuenta_estudiante_id"])
    op.create_index("ix_tokens_recuperacion_expira_en", "tokens_recuperacion", ["expira_en"])


def downgrade():
    op.drop_table("tokens_recuperacion")

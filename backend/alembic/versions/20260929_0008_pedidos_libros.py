"""pedidos de biblioteca"""
from alembic import op
import sqlalchemy as sa
revision = "20260929_0008"
down_revision = "20260929_0007"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table("pedidos_libros",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("estudiante_id", sa.Integer(), nullable=False),
        sa.Column("libro_id", sa.Integer(), nullable=True),
        sa.Column("titulo_solicitado", sa.String(length=200), nullable=True),
        sa.Column("fecha_pedido", sa.DateTime(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("observacion", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["estudiante_id"], ["estudiantes.id"]),
        sa.ForeignKeyConstraint(["libro_id"], ["libros.id"]),
        sa.PrimaryKeyConstraint("id"))
    for col in ("id", "estudiante_id", "libro_id", "fecha_pedido", "estado"):
        op.create_index(f"ix_pedidos_libros_{col}", "pedidos_libros", [col], unique=False)
def downgrade():
    op.drop_table("pedidos_libros")

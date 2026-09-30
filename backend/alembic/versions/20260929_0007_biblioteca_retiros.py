"""biblioteca y retiros"""
from alembic import op
import sqlalchemy as sa
revision="20260929_0007"
down_revision="20260616_0006"
branch_labels=None
depends_on=None
def upgrade():
    op.create_table("libros",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("titulo",sa.String(200),nullable=False),sa.Column("autor",sa.String(150),nullable=False),sa.Column("isbn",sa.String(20),nullable=True,unique=True),sa.Column("ejemplares",sa.Integer(),nullable=False))
    op.create_index("ix_libros_id","libros",["id"])
    op.create_index("ix_libros_titulo","libros",["titulo"])
    op.create_table("prestamos_libros",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("libro_id",sa.Integer(),sa.ForeignKey("libros.id"),nullable=False),sa.Column("estudiante_id",sa.Integer(),sa.ForeignKey("estudiantes.id"),nullable=False),sa.Column("fecha_prestamo",sa.Date(),nullable=False),sa.Column("fecha_devolucion",sa.Date(),nullable=False),sa.Column("devuelto_en",sa.DateTime(),nullable=True))
    op.create_index("ix_prestamos_libros_id","prestamos_libros",["id"]); op.create_index("ix_prestamos_libros_libro_id","prestamos_libros",["libro_id"]); op.create_index("ix_prestamos_libros_estudiante_id","prestamos_libros",["estudiante_id"]); op.create_index("ix_prestamos_libros_fecha_devolucion","prestamos_libros",["fecha_devolucion"])
    op.create_table("retiros_estudiantes",sa.Column("id",sa.Integer(),primary_key=True),sa.Column("estudiante_id",sa.Integer(),sa.ForeignKey("estudiantes.id"),nullable=False),sa.Column("retirado_por",sa.String(150),nullable=False),sa.Column("autorizado_por",sa.String(150),nullable=False),sa.Column("motivo",sa.Text(),nullable=True),sa.Column("fecha_hora",sa.DateTime(),server_default=sa.text("now()"),nullable=False))
    op.create_index("ix_retiros_estudiantes_id","retiros_estudiantes",["id"]); op.create_index("ix_retiros_estudiantes_estudiante_id","retiros_estudiantes",["estudiante_id"]); op.create_index("ix_retiros_estudiantes_fecha_hora","retiros_estudiantes",["fecha_hora"])
def downgrade():
    op.drop_table("retiros_estudiantes"); op.drop_table("prestamos_libros"); op.drop_index("ix_libros_titulo",table_name="libros"); op.drop_index("ix_libros_id",table_name="libros"); op.drop_table("libros")

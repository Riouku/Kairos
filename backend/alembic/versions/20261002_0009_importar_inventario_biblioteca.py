"""Conservar el inventario 2025 y sus datos bibliográficos."""
import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "20261002_0009"
down_revision = "20260929_0008"
branch_labels = None
depends_on = None


def _normalizar(value):
    return " ".join((value or "").strip().casefold().split())


def _clave_sin_isbn(row):
    return tuple(_normalizar(row.get(field)) for field in ("titulo", "autor", "editorial", "anio_publicacion"))


def upgrade():
    bind = op.get_bind()

    for constraint in sa.inspect(bind).get_unique_constraints("libros"):
        if constraint.get("column_names") == ["isbn"]:
            op.drop_constraint(constraint["name"], "libros", type_="unique")

    op.add_column("libros", sa.Column("editorial", sa.String(length=150), nullable=True))
    op.add_column("libros", sa.Column("anio_publicacion", sa.String(length=20), nullable=True))
    op.add_column("libros", sa.Column("pais", sa.String(length=80), nullable=True))
    op.add_column("libros", sa.Column("ubicacion", sa.String(length=200), nullable=True))
    op.add_column("libros", sa.Column("clasificacion", sa.Text(), nullable=True))
    op.add_column("libros", sa.Column("observaciones", sa.Text(), nullable=True))
    op.create_index("ix_libros_isbn", "libros", ["isbn"], unique=False)

    data_path = Path(__file__).resolve().parents[2] / "app" / "data" / "inventario_biblioteca_2025.json"
    inventory = json.loads(data_path.read_text(encoding="utf-8"))["libros"]
    books = sa.table(
        "libros",
        sa.column("id", sa.Integer()),
        sa.column("titulo", sa.String()),
        sa.column("autor", sa.String()),
        sa.column("isbn", sa.String()),
        sa.column("ejemplares", sa.Integer()),
        sa.column("editorial", sa.String()),
        sa.column("anio_publicacion", sa.String()),
        sa.column("pais", sa.String()),
        sa.column("ubicacion", sa.String()),
        sa.column("clasificacion", sa.Text()),
        sa.column("observaciones", sa.Text()),
    )
    existing = bind.execute(sa.select(books)).mappings().all()
    by_isbn = {}
    by_title_without_isbn = {}
    for row in existing:
        if not row["isbn"]:
            by_title_without_isbn.setdefault(_clave_sin_isbn(row), []).append(row)
        if row["isbn"]:
            by_isbn.setdefault((
                _normalizar(row["titulo"]),
                _normalizar(row["autor"]),
                _normalizar(row["isbn"]),
            ), []).append(row)

    to_insert = []
    for item in inventory:
        exact = by_isbn.get((
            _normalizar(item["titulo"]),
            _normalizar(item["autor"]),
            _normalizar(item.get("isbn")),
        ), []) if item.get("isbn") else by_title_without_isbn.get(_clave_sin_isbn(item), [])

        if exact:
            current = exact[0]
            updates = {"ejemplares": max(current["ejemplares"], item["ejemplares"])}
            for field in (
                "editorial", "anio_publicacion", "pais", "ubicacion", "clasificacion", "observaciones"
            ):
                if not current[field] and item.get(field):
                    updates[field] = item[field]
            bind.execute(sa.update(books).where(books.c.id == current["id"]).values(**updates))
            continue

        to_insert.append(item)

    if to_insert:
        op.bulk_insert(books, to_insert)


def downgrade():
    op.drop_index("ix_libros_isbn", table_name="libros")
    op.drop_column("libros", "observaciones")
    op.drop_column("libros", "clasificacion")
    op.drop_column("libros", "ubicacion")
    op.drop_column("libros", "pais")
    op.drop_column("libros", "anio_publicacion")
    op.drop_column("libros", "editorial")

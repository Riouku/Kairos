from logging.config import fileConfig

from alembic import context


from app.database.session import Base, get_engine
from app.models import (  # noqa: F401
    Asignacion,
    Asignatura,
    Asistencia,
    Libro,
    PrestamoLibro,
    RetiroEstudiante,
    Curso,
    Estudiante,
    Evaluacion,
    EventoAcademico,
    HorarioClase,
    Nota,
    PeriodoAcademico,
    Profesor,
)
from config import get_settings

config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

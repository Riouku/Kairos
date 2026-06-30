from collections.abc import Generator
from functools import lru_cache

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()


@lru_cache
def get_engine():
    engine_options = {"pool_pre_ping": True}
    if settings.database_url.startswith("postgresql"):
        engine_options["connect_args"] = {"connect_timeout": 5}
    return create_engine(settings.database_url, **engine_options)


@lru_cache
def get_session_factory():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def SessionLocal() -> Session:
    return get_session_factory()()


engine = None


def get_db() -> Generator[Session, None, None]:
    try:
        db = SessionLocal()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo iniciar la conexion a PostgreSQL. Revisa DATABASE_URL en Vercel.",
        ) from exc
    try:
        yield db
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo consultar PostgreSQL. Revisa DATABASE_URL y las migraciones.",
        ) from exc
    finally:
        db.close()

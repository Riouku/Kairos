from collections.abc import Generator
from functools import lru_cache
import ssl

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()


@lru_cache
def get_engine():
    engine_options = {"pool_pre_ping": True}
    database_url = settings.database_url
    if settings.database_url.startswith("postgresql+pg8000"):
        engine_options["connect_args"] = {"timeout": 5}
        url = make_url(settings.database_url)
        if url.query.get("sslmode") in {"require", "verify-ca", "verify-full"}:
            engine_options["connect_args"]["ssl_context"] = ssl.create_default_context()
            database_url = str(url.difference_update_query(["sslmode"]))
    elif settings.database_url.startswith("postgresql"):
        engine_options["connect_args"] = {"connect_timeout": 5}
    return create_engine(database_url, **engine_options)


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

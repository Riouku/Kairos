import socket
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import text


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.database import SessionLocal  # noqa: E402
from config import get_settings  # noqa: E402


def redact_database_url(database_url: str) -> str:
    parsed = urlsplit(database_url)
    host = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    user = parsed.username or ""
    auth = f"{user}:***@" if user else ""
    return urlunsplit((parsed.scheme, f"{auth}{host}{port}", parsed.path, parsed.query, parsed.fragment))


def resolve_host(host: str) -> list[str]:
    if not host:
        return []
    addresses = []
    try:
        for family, _type, _proto, _canonname, sockaddr in socket.getaddrinfo(host, None):
            label = "IPv6" if family == socket.AF_INET6 else "IPv4"
            addresses.append(f"{label} {sockaddr[0]}")
    except OSError as exc:
        return [f"DNS error: {exc}"]
    return sorted(set(addresses))


def main() -> int:
    settings = get_settings()
    parsed = urlsplit(settings.database_url)
    host = parsed.hostname or ""

    print("Kairos DB profiler")
    print("==================")
    print(f"DATABASE_URL configurada: {'si' if bool(settings.database_url) else 'no'}")
    print(f"URL redactada: {redact_database_url(settings.database_url)}")
    print(f"Driver: {parsed.scheme}")
    print(f"Host: {host or '-'}")
    print(f"Puerto: {parsed.port or '-'}")
    print(f"Base: {parsed.path.lstrip('/') or '-'}")

    print("\nDNS:")
    for address in resolve_host(host):
        print(f"- {address}")

    print("\nAdvertencias:")
    warnings = []
    if "REGION" in settings.database_url.upper():
        warnings.append("La URL aun contiene REGION; copia el host real desde Supabase.")
    if host.startswith("db.") and host.endswith(".supabase.co"):
        warnings.append("Es la conexion directa de Supabase; para Vercel conviene Transaction pooler puerto 6543.")
    if parsed.port == 5432 and host.endswith(".supabase.co"):
        warnings.append("Puerto 5432 puede fallar en Vercel; usa el pooler en puerto 6543.")
    if not warnings:
        warnings.append("Sin advertencias obvias en el formato.")
    for warning in warnings:
        print(f"- {warning}")

    print("\nConexion:")
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            version = db.execute(text("SELECT version()")).scalar()
            try:
                alembic_version = db.execute(text("SELECT version_num FROM alembic_version")).scalar()
            except Exception as exc:
                alembic_version = f"No disponible ({exc.__class__.__name__})"
    except Exception as exc:
        print("Estado: error")
        print(f"Tipo: {exc.__class__.__name__}")
        print(f"Detalle: {str(exc).splitlines()[0]}")
        return 1

    print("Estado: ok")
    print(f"PostgreSQL: {version}")
    print(f"Alembic: {alembic_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

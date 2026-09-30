from pathlib import Path
import os
import shutil
import stat
import sys
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
PUBLIC = ROOT / "public"
BACKEND = ROOT / "backend"


def copy_tree(source: Path, target: Path) -> None:
    if target.exists():
        remove_tree(target)
    shutil.copytree(source, target)


def remove_tree(path: Path) -> None:
    def handle_remove_error(func, failed_path, _exc_info):
        os.chmod(failed_path, stat.S_IWRITE)
        func(failed_path)

    shutil.rmtree(path, onerror=handle_remove_error)


def migrate_database() -> None:
    if os.environ.get("VERCEL_ENV") != "production":
        return

    sys.path.insert(0, str(BACKEND))
    from alembic import command
    from alembic.config import Config
    from config import get_settings

    host = urlsplit(get_settings().database_url).hostname or ""
    if not host.endswith(".supabase.com"):
        raise RuntimeError("Refusing to run Vercel migrations: the selected database is not Supabase.")

    previous_directory = Path.cwd()
    try:
        os.chdir(BACKEND)
        command.upgrade(Config(str(BACKEND / "alembic.ini")), "head")
    finally:
        os.chdir(previous_directory)
def main() -> None:
    migrate_database()
    if PUBLIC.exists():
        remove_tree(PUBLIC)

    PUBLIC.mkdir()
    copy_tree(FRONTEND / "static", PUBLIC / "static")
    copy_tree(FRONTEND / "templates", PUBLIC / "templates")

    for html_file in (FRONTEND / "templates").glob("*.html"):
        shutil.copy2(html_file, PUBLIC / html_file.name)

    shutil.copy2(FRONTEND / "templates" / "index.html", PUBLIC / "index.html")


if __name__ == "__main__":
    main()

from pathlib import Path
import os
import shutil
import stat


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
PUBLIC = ROOT / "public"


def copy_tree(source: Path, target: Path) -> None:
    if target.exists():
        remove_tree(target)
    shutil.copytree(source, target)


def remove_tree(path: Path) -> None:
    def handle_remove_error(func, failed_path, _exc_info):
        os.chmod(failed_path, stat.S_IWRITE)
        func(failed_path)

    shutil.rmtree(path, onerror=handle_remove_error)


def main() -> None:
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

from pathlib import Path
import shutil


ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"
PUBLIC_DIR = ROOT_DIR / "public"


def copy_tree(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)


def main() -> None:
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    for html_file in (FRONTEND_DIR / "templates").glob("*.html"):
        shutil.copy2(html_file, PUBLIC_DIR / html_file.name)
    copy_tree(FRONTEND_DIR / "static", PUBLIC_DIR / "static")


if __name__ == "__main__":
    main()

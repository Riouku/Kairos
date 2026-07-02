import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    from main import app  # noqa: E402
except Exception as import_error:  # pragma: no cover - diagnostic fallback for Vercel startup failures.
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI(title="Kairos startup error")

    def startup_error_response():
        return JSONResponse(
            status_code=500,
            content={
                "detail": "No se pudo iniciar el backend en Vercel.",
                "error": str(import_error),
                "help": "Revisa DATABASE_URL, dependencias y logs del deployment en Vercel.",
            },
        )

    @app.get("/health")
    def health():
        return startup_error_response()

    @app.get("/health/db")
    def health_db():
        return startup_error_response()

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    def catch_all(_path: str):
        return startup_error_response()

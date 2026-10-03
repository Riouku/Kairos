from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
import hashlib
import hmac
import logging
import secrets
import smtplib
import ssl

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Asistencia, CuentaEstudiante, Evaluacion, Nota, SesionUsuario, TokenRecuperacion
from app.models.estudiante import Estudiante
from config import get_settings

router = APIRouter(tags=["Autenticación"])
settings = get_settings()
logger = logging.getLogger(__name__)
COOKIE_NAME = "kairos_session"
SESSION_DAYS = 7


class LoginPayload(BaseModel):
    correo: str = Field(min_length=5, max_length=150, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    contrasena: str = Field(min_length=1, max_length=200)


class CuentaPayload(BaseModel):
    estudiante_id: int
    correo: str = Field(min_length=5, max_length=150, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    contrasena: str = Field(min_length=10, max_length=200)


class SolicitarRecuperacion(BaseModel):
    correo: str = Field(min_length=5, max_length=150, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class RestablecerContrasena(BaseModel):
    token: str = Field(min_length=30, max_length=200)
    contrasena: str = Field(min_length=10, max_length=200)


class CambiarContrasena(BaseModel):
    contrasena_actual: str = Field(min_length=1, max_length=200)
    contrasena_nueva: str = Field(min_length=10, max_length=200)


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, salt_hex, digest_hex = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        actual = _hash_password(password, bytes.fromhex(salt_hex)).split("$")[2]
        return hmac.compare_digest(actual, digest_hex)
    except (ValueError, TypeError):
        return False


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _new_session(db: Session, role: str, account_id: int | None = None) -> str:
    token = secrets.token_urlsafe(40)
    db.add(SesionUsuario(
        token_hash=token_hash(token), rol=role, cuenta_estudiante_id=account_id,
        expira_en=datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS),
    ))
    db.commit()
    return token


def set_session_cookie(response: Response, token: str, request: Request) -> None:
    response.set_cookie(COOKIE_NAME, token, httponly=True, secure=request.url.scheme == "https",
                        samesite="lax", max_age=SESSION_DAYS * 86400, path="/")


def _send_reset_email(email: str, token: str) -> None:
    if not all((settings.smtp_host, settings.smtp_user, settings.smtp_password,
                settings.smtp_from_email, settings.kairos_public_url)):
        raise RuntimeError("Falta configurar SMTP y KAIROS_PUBLIC_URL.")
    base_url = settings.kairos_public_url.rstrip("/")
    reset_url = f"{base_url}/restablecer-contrasena.html?token={token}"
    message = EmailMessage()
    message["Subject"] = "Recuperación de contraseña - Colegio Kairos"
    message["From"] = settings.smtp_from_email
    message["To"] = email
    message.set_content(
        "Recibimos una solicitud para cambiar la contraseña de tu cuenta de alumno. "
        f"Abre este enlace para crear una contraseña nueva (vence en 30 minutos):\n\n{reset_url}\n\n"
        "Si no solicitaste este cambio, ignora este mensaje."
    )
    context = ssl.create_default_context()
    if settings.smtp_port == 465:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=12, context=context) as server:
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=12) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)


def get_session(db: Session, token: str | None) -> SesionUsuario | None:
    if not token:
        return None
    session = db.get(SesionUsuario, token_hash(token))
    if not session:
        return None
    expiration = session.expira_en
    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)
    if expiration <= datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        return None
    if session.rol == "alumno":
        account = db.scalar(select(CuentaEstudiante).options(joinedload(CuentaEstudiante.estudiante)).where(
            CuentaEstudiante.id == session.cuenta_estudiante_id,
            CuentaEstudiante.activo.is_(True),
        ))
        if not account or not account.estudiante.activo:
            return None
    return session


@router.post("/api/auth/login")
def login(payload: LoginPayload, request: Request, response: Response, db: Session = Depends(get_db)):
    email = payload.correo.lower().strip()
    admin_email = settings.kairos_admin_email.lower().strip()
    admin_password = settings.kairos_admin_password
    if admin_email and admin_password and hmac.compare_digest(email, admin_email) and hmac.compare_digest(payload.contrasena, admin_password):
        token = _new_session(db, "admin")
        set_session_cookie(response, token, request)
        return {"rol": "admin", "redirect": "index.html"}

    account = db.scalar(select(CuentaEstudiante).options(joinedload(CuentaEstudiante.estudiante)).where(
        CuentaEstudiante.correo == email, CuentaEstudiante.activo.is_(True),
    ))
    if not account or not account.estudiante.activo or not _verify_password(payload.contrasena, account.password_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
    token = _new_session(db, "alumno", account.id)
    set_session_cookie(response, token, request)
    return {"rol": "alumno", "redirect": "portal-alumno.html"}


@router.get("/api/auth/me")
def who_am_i(request: Request, db: Session = Depends(get_db)):
    session = get_session(db, request.cookies.get(COOKIE_NAME))
    if not session:
        raise HTTPException(status_code=401, detail="La sesión expiró.")
    return {"rol": session.rol}


@router.post("/api/auth/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        session = db.get(SesionUsuario, token_hash(token))
        if session:
            db.delete(session)
            db.commit()
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, samesite="lax")
    return {"ok": True}


@router.post("/api/auth/cuentas-alumno", status_code=status.HTTP_201_CREATED)
def crear_cuenta(payload: CuentaPayload, db: Session = Depends(get_db)):
    email = payload.correo.lower().strip()
    estudiante = db.get(Estudiante, payload.estudiante_id)
    if not estudiante or not estudiante.activo:
        raise HTTPException(status_code=404, detail="No se encontró un estudiante activo.")
    existing = db.scalar(select(CuentaEstudiante).where(
        (CuentaEstudiante.estudiante_id == estudiante.id) | (CuentaEstudiante.correo == email)
    ))
    if existing:
        raise HTTPException(status_code=409, detail="El estudiante ya tiene una cuenta o el correo está en uso.")
    account = CuentaEstudiante(estudiante_id=estudiante.id, correo=email, password_hash=_hash_password(payload.contrasena))
    db.add(account)
    db.commit()
    return {"id": account.id, "estudiante_id": estudiante.id, "correo": email, "activo": True}


@router.post("/api/auth/solicitar-recuperacion", status_code=status.HTTP_202_ACCEPTED)
def solicitar_recuperacion(payload: SolicitarRecuperacion, db: Session = Depends(get_db)):
    email = payload.correo.lower().strip()
    if not all((settings.smtp_host, settings.smtp_user, settings.smtp_password,
                settings.smtp_from_email, settings.kairos_public_url)):
        raise HTTPException(status_code=503, detail="La recuperación por correo aún no está configurada.")
    account = db.scalar(select(CuentaEstudiante).where(
        CuentaEstudiante.correo == email, CuentaEstudiante.activo.is_(True),
    ))
    generic_response = {"detail": "Si existe una cuenta activa con ese correo, recibirás instrucciones para restablecer la contraseña."}
    if not account or not account.estudiante.activo:
        return generic_response

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=1)
    previous = db.scalars(select(TokenRecuperacion).where(
        TokenRecuperacion.cuenta_estudiante_id == account.id
    )).all()
    recent = any((item.creado_en.replace(tzinfo=timezone.utc) if item.creado_en.tzinfo is None else item.creado_en) > cutoff for item in previous)
    if recent:
        return generic_response
    for item in previous:
        db.delete(item)

    token = secrets.token_urlsafe(36)
    reset = TokenRecuperacion(token_hash=token_hash(token), cuenta_estudiante_id=account.id,
                              expira_en=datetime.now(timezone.utc) + timedelta(minutes=30))
    db.add(reset)
    db.commit()
    try:
        _send_reset_email(email, token)
    except Exception as exc:
        db.delete(reset)
        db.commit()
        logger.exception("Fallo el envío del correo para recuperación de contraseña")
    return generic_response


@router.post("/api/auth/restablecer-contrasena")
def restablecer_contrasena(payload: RestablecerContrasena, db: Session = Depends(get_db)):
    reset = db.get(TokenRecuperacion, token_hash(payload.token))
    if not reset:
        raise HTTPException(status_code=400, detail="El enlace no es válido o ya fue utilizado.")
    expiration = reset.expira_en
    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)
    if expiration <= datetime.now(timezone.utc):
        db.delete(reset)
        db.commit()
        raise HTTPException(status_code=400, detail="El enlace venció. Solicita uno nuevo.")
    account_id = reset.cuenta_estudiante_id
    account = db.get(CuentaEstudiante, account_id)
    if not account or not account.activo:
        raise HTTPException(status_code=400, detail="La cuenta no está disponible.")
    account.password_hash = _hash_password(payload.contrasena)
    for item in db.scalars(select(TokenRecuperacion).where(TokenRecuperacion.cuenta_estudiante_id == account_id)).all():
        db.delete(item)
    for session in db.scalars(select(SesionUsuario).where(SesionUsuario.cuenta_estudiante_id == account_id)).all():
        db.delete(session)
    db.commit()
    return {"detail": "Contraseña actualizada. Ya puedes iniciar sesión."}


@router.post("/api/auth/cambiar-contrasena")
def cambiar_contrasena(payload: CambiarContrasena, request: Request, db: Session = Depends(get_db)):
    session = get_session(db, request.cookies.get(COOKIE_NAME))
    if not session or session.rol != "alumno" or not session.cuenta_estudiante_id:
        raise HTTPException(status_code=403, detail="Solo un alumno puede cambiar su contraseña desde el portal.")
    account = db.get(CuentaEstudiante, session.cuenta_estudiante_id)
    if not account or not _verify_password(payload.contrasena_actual, account.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual no coincide.")
    account.password_hash = _hash_password(payload.contrasena_nueva)
    for item in db.scalars(select(SesionUsuario).where(
        SesionUsuario.cuenta_estudiante_id == account.id,
        SesionUsuario.token_hash != token_hash(request.cookies.get(COOKIE_NAME, "")),
    )).all():
        db.delete(item)
    db.commit()
    return {"detail": "Contraseña cambiada correctamente."}


@router.get("/api/portal/alumno")
def portal_alumno(request: Request, db: Session = Depends(get_db)):
    session = get_session(db, request.cookies.get(COOKIE_NAME))
    if not session or session.rol != "alumno" or not session.cuenta_estudiante_id:
        raise HTTPException(status_code=403, detail="Esta página es solo para alumnos.")
    account = db.scalar(select(CuentaEstudiante).options(joinedload(CuentaEstudiante.estudiante).joinedload(Estudiante.curso)).where(
        CuentaEstudiante.id == session.cuenta_estudiante_id,
    ))
    student = account.estudiante
    notas = db.scalars(select(Nota).options(joinedload(Nota.evaluacion).joinedload(Evaluacion.asignatura),
        joinedload(Nota.evaluacion).joinedload(Evaluacion.periodo)).join(Nota.evaluacion).where(
        Nota.estudiante_id == student.id, Evaluacion.anio_academico == student.anio_academico)
        .order_by(Nota.fecha_registro.desc())).all()
    attendance = db.scalars(select(Asistencia).where(
        Asistencia.estudiante_id == student.id, Asistencia.anio_academico == student.anio_academico
    )).all()
    counts = {"presente": 0, "ausente": 0, "atrasado": 0, "justificado": 0}
    for row in attendance:
        status_name = row.estado.lower()
        if status_name == "tarde":
            status_name = "atrasado"
        if status_name in counts:
            counts[status_name] += 1
    total_days = len(attendance)
    percent = round((counts["presente"] + counts["atrasado"] + counts["justificado"]) * 100 / total_days, 1) if total_days else None
    weighted_sum = sum(float(item.nota) * float(item.evaluacion.ponderacion or 0) for item in notas)
    total_weight = sum(float(item.evaluacion.ponderacion or 0) for item in notas)
    return {
        "estudiante": {"nombre": f"{student.nombre} {student.apellido}", "curso": student.curso.nombre,
                       "anio_academico": student.anio_academico},
        "promedio": round(weighted_sum / total_weight, 1) if total_weight else None,
        "notas": [{"asignatura": item.evaluacion.asignatura.nombre, "evaluacion": item.evaluacion.titulo,
                   "periodo": item.evaluacion.periodo.nombre, "nota": float(item.nota),
                   "ponderacion": float(item.evaluacion.ponderacion or 0)} for item in notas],
        "asistencia": {"porcentaje": percent, "presentes": counts["presente"], "ausentes": counts["ausente"],
                       "atrasos": counts["atrasado"], "justificados": counts["justificado"], "dias_registrados": total_days},
    }

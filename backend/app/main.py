"""Punto de entrada HTTP de FastAPI.

Aquí vive infraestructura de borde: middlewares, handlers HTTP, startup.
No contiene reglas de negocio de dominio.
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import SessionLocal
from app.composition.bootstrap import ensure_superadmin

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


def run_auto_migrations() -> None:
    """Aplica migraciones al iniciar si la configuración lo habilita."""
    if not settings.auto_migrate_on_start:
        return

    backend_dir = Path(__file__).resolve().parents[1]
    alembic_cfg = Config(str(backend_dir / 'alembic.ini'))
    alembic_cfg.set_main_option('script_location', str(backend_dir / 'alembic'))
    alembic_cfg.set_main_option('sqlalchemy.url', settings.database_url)
    command.upgrade(alembic_cfg, 'head')


@app.on_event('startup')
def startup() -> None:
    """Evento de inicio: migra DB y asegura superadmin inicial."""
    run_auto_migrations()
    with SessionLocal() as db:
        ensure_superadmin(db)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Datos invalidos',
                'details': exc.errors(),
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and 'error' in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': {
                'code': 'HTTP_ERROR',
                'message': str(exc.detail),
                'details': None,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Error interno del servidor',
                'details': str(exc),
            }
        },
    )


@app.get('/health')
def health():
    """Endpoint mínimo de liveness/readiness."""
    return {'status': 'ok'}


app.include_router(api_router, prefix=settings.api_prefix)

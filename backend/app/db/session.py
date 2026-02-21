"""Utilidades de base de datos (`session`): sesión, base o metadatos."""

import logging
from threading import Lock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.composition.bootstrap import ensure_superadmin

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger = logging.getLogger(__name__)

_superadmin_bootstrap_done = False
_superadmin_bootstrap_lock = Lock()


def _ensure_superadmin_once() -> None:
    global _superadmin_bootstrap_done
    if _superadmin_bootstrap_done:
        return

    with _superadmin_bootstrap_lock:
        if _superadmin_bootstrap_done:
            return
        with SessionLocal() as db:
            ensure_superadmin(db)
        _superadmin_bootstrap_done = True


def get_db():
    try:
        _ensure_superadmin_once()
    except Exception:
        logger.exception('Fallo bootstrap de superadmin en get_db')
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

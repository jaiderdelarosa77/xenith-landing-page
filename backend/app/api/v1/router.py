"""Router principal de API: agrupa y registra sub-rutas por módulo."""

from fastapi import APIRouter

from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.clients import router as clients_router
from app.api.v1.comunicados import router as comunicados_router
from app.api.v1.concepts import router as concepts_router
from app.api.v1.contact import router as contact_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.item_groups import router as item_groups_router
from app.api.v1.profile import router as profile_router
from app.api.v1.projects import router as projects_router
from app.api.v1.products import router as products_router
from app.api.v1.quotations import router as quotations_router
from app.api.v1.rfid import router as rfid_router
from app.api.v1.suppliers import router as suppliers_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.uploads import router as uploads_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(audit_router)
api_router.include_router(auth_router)
api_router.include_router(categories_router)
api_router.include_router(clients_router)
api_router.include_router(comunicados_router)
api_router.include_router(concepts_router)
api_router.include_router(contact_router)
api_router.include_router(products_router)
api_router.include_router(suppliers_router)
api_router.include_router(inventory_router)
api_router.include_router(item_groups_router)
api_router.include_router(projects_router)
api_router.include_router(tasks_router)
api_router.include_router(uploads_router)
api_router.include_router(quotations_router)
api_router.include_router(rfid_router)
api_router.include_router(profile_router)
api_router.include_router(users_router)

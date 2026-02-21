# Xenith Backend (FastAPI)

API backend de Xenith.

## Stack
- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pydantic v2
- PostgreSQL
- JWT access + refresh (cookies HttpOnly)

## Arquitectura hexagonal (incremental)
- `app/domain`: entidades y puertos (sin dependencia de FastAPI/SQLAlchemy).
- `app/application`: casos de uso que orquestan reglas de negocio.
- `app/infrastructure`: adaptadores concretos (SQLAlchemy, security, etc.).
- `app/composition`: composition root (wiring de casos de uso + adaptadores).
- `app/api`: capa de entrada HTTP (controladores/routers).

Guia para principiantes:
- `docs/BACKEND_EXPLICADO.md` (explica que hace cada capa, como fluye un request y por que esta diseñado asi).

Migrado en esta fase:
- Auth (`login`, `refresh`, `logout`) usa `AuthUseCases` + puertos/adaptadores.
- Bootstrap de superadmin usa caso de uso + gateway de infraestructura.
- Users (`/v1/users`) usa `UsersUseCases` + puertos/adaptadores.
- Products (`/v1/products`) usa `ProductsUseCases` + puertos/adaptadores.
- Inventory (`/v1/inventory`) usa `InventoryUseCases` + puertos/adaptadores.
- RFID (`/v1/rfid`) usa `RfidUseCases` + puertos/adaptadores.
- Clients (`/v1/clients`) usa `ClientsUseCases` + puertos/adaptadores.
- Projects (`/v1/projects`) usa `ProjectsUseCases` + puertos/adaptadores.
- Tasks (`/v1/tasks`) usa `TasksUseCases` + puertos/adaptadores.
- Quotations (`/v1/quotations`) usa `QuotationsUseCases` + puertos/adaptadores.
- Categories (`/v1/categories`) usa `CategoriesUseCases` + puertos/adaptadores.
- Suppliers (`/v1/suppliers`) usa `SuppliersUseCases` + puertos/adaptadores.
- Concepts (`/v1/concepts`) usa `ConceptsUseCases` + puertos/adaptadores.
- Item Groups (`/v1/item-groups`) usa `ItemGroupsUseCases` + puertos/adaptadores.
- Audit (`/v1/audit`) usa `AuditUseCases` + puertos/adaptadores.
- Profile (`/v1/profile`) usa `ProfileUseCases` + puertos/adaptadores.
- Deps de auth/permisos (`app/api/deps.py`) delega en `AccessControlUseCases`.

## Correr local
1. Crear entorno y dependencias.
2. Copiar `backend/.env.example` a `backend/.env`.
3. Generar migración si cambiaste modelos.
4. Ejecutar migraciones Alembic.
5. Levantar API.

Comandos sugeridos:

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "init"
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Por defecto, la API ejecuta `alembic upgrade head` al iniciar (`AUTO_MIGRATE_ON_START=true`).
Si prefieres desactivarlo, usa `AUTO_MIGRATE_ON_START=false`.
Al iniciar tambien intenta asegurar un superadmin inicial usando `SUPERADMIN_EMAIL` y `SUPERADMIN_PASSWORD`.

## Regla de migraciones
- Cambias modelos -> generas migración (`revision --autogenerate`).
- Revisas el archivo generado antes de aplicarlo.
- Commits de backend deben incluir código + migración en el mismo cambio.
- En despliegue no se genera migración: solo `alembic upgrade head`.
- Ejecuta `alembic check` para validar que no queden cambios de modelos sin migración.

Comandos útiles backend:
- `uv run alembic revision --autogenerate -m "describe-cambio"`
- `uv run alembic upgrade head`
- `uv run alembic check`
- `uv run alembic current`
- `uv run alembic heads`

## Endpoints migrados en esta fase
- `POST /v1/auth/login`
- `POST /v1/auth/refresh`
- `POST /v1/auth/logout`
- `GET /v1/auth/me`
- `GET /v1/profile`
- `PUT /v1/profile/change-password`
- `GET /v1/users`
- `POST /v1/users`
- `GET /v1/users/{id}`
- `PUT /v1/users/{id}`
- `DELETE /v1/users/{id}`
- `GET /v1/products`
- `POST /v1/products`
- `GET /v1/products/{id}`
- `PUT /v1/products/{id}`
- `DELETE /v1/products/{id}`
- `GET /v1/products/{id}/suppliers`
- `POST /v1/products/{id}/suppliers`
- `DELETE /v1/products/{id}/suppliers/{supplierId}`
- `GET /v1/inventory`
- `POST /v1/inventory`
- `GET /v1/inventory/{id}`
- `PUT /v1/inventory/{id}`
- `DELETE /v1/inventory/{id}`
- `POST /v1/inventory/{id}/check-in`
- `POST /v1/inventory/{id}/check-out`
- `GET /v1/inventory/summary`
- `GET /v1/inventory/movements`
- `GET /v1/clients`
- `POST /v1/clients`
- `GET /v1/clients/{id}`
- `PUT /v1/clients/{id}`
- `DELETE /v1/clients/{id}`
- `GET /v1/projects`
- `POST /v1/projects`
- `GET /v1/projects/{id}`
- `PUT /v1/projects/{id}`
- `DELETE /v1/projects/{id}`
- `GET /v1/tasks`
- `GET /v1/tasks/{id}`
- `PATCH /v1/tasks/{id}`
- `GET /v1/quotations`
- `POST /v1/quotations`
- `GET /v1/quotations/{id}`
- `PUT /v1/quotations/{id}`
- `DELETE /v1/quotations/{id}`
- `GET /v1/quotations/{id}/pdf`
- `GET /v1/rfid/tags`
- `POST /v1/rfid/tags`
- `GET /v1/rfid/tags/unknown`
- `GET /v1/rfid/tags/{id}`
- `PUT /v1/rfid/tags/{id}`
- `DELETE /v1/rfid/tags/{id}`
- `POST /v1/rfid/tags/{id}/enroll`
- `DELETE /v1/rfid/tags/{id}/enroll`
- `GET /v1/rfid/detections`
- `POST /v1/rfid/read`
- `GET /v1/categories`
- `POST /v1/categories`
- `GET /v1/categories/{id}`
- `PUT /v1/categories/{id}`
- `DELETE /v1/categories/{id}`
- `GET /v1/suppliers`
- `POST /v1/suppliers`
- `GET /v1/suppliers/{id}`
- `PUT /v1/suppliers/{id}`
- `DELETE /v1/suppliers/{id}`
- `GET /v1/concepts`
- `POST /v1/concepts`
- `GET /v1/concepts/{id}`
- `PUT /v1/concepts/{id}`
- `DELETE /v1/concepts/{id}`
- `GET /v1/item-groups`
- `POST /v1/item-groups`
- `GET /v1/item-groups/{id}`
- `PUT /v1/item-groups/{id}`
- `DELETE /v1/item-groups/{id}`
- `POST /v1/item-groups/{id}/items`
- `DELETE /v1/item-groups/{id}/items/{itemId}`
- `GET /v1/audit`
- `POST /v1/comunicados`
- `POST /v1/contact`
- `POST /v1/uploads/products`
- `DELETE /v1/uploads/products`

## Notas
- Se agregó tabla `refresh_tokens` por Alembic.
- El frontend ya puede autenticarse contra FastAPI con `NEXT_PUBLIC_API_URL`.
- Para `POST /v1/comunicados` configura `RESEND_API_KEY` y opcionalmente `EMAILS_FROM`.
- Para uploads configura `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME` y `R2_PUBLIC_URL`.
- Guía de despliegue unificada: ver `README.md` en la raíz del proyecto.

## Checklist Hexagonal
- `api/*`: solo HTTP/Depends/serialización de errores.
- `application/*`: casos de uso sin SQLAlchemy/FastAPI.
- `domain/*`: puertos, entidades y errores de negocio.
- `infrastructure/*`: adaptadores concretos (ORM, security, externos).
- `composition/*`: fábricas/wiring de dependencias (sin reglas de negocio).

Verificación automática:
- `cd backend && python3 scripts/check_hexagonal.py`
- Valida imports prohibidos en `domain`, `application` y `api` (evita acoplar `api` a `infrastructure`/`models`).

## Tests Unitarios
- Ejecutar: `cd backend && .venv/bin/pytest -q`
- Cobertura actual (hardening pass): `auth`, `users`, `quotations`, `access_control`.

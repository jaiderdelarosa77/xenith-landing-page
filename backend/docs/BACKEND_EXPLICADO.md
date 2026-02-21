# Backend explicado (nivel principiante)

Este documento explica el backend como si fueras nuevo en el proyecto y en arquitectura hexagonal.

## 1. Idea general

El backend esta separado en capas para que el negocio no dependa de FastAPI ni de SQLAlchemy.

Capas principales:
- `app/domain`: reglas y contratos del negocio.
- `app/application`: casos de uso (orquestan pasos de negocio).
- `app/infrastructure`: implementaciones concretas (DB, seguridad, servicios externos).
- `app/composition`: conecta casos de uso con implementaciones concretas.
- `app/api`: endpoints HTTP (entrada/salida).

Regla mental:
- `domain` no conoce a nadie.
- `application` conoce `domain`.
- `infrastructure` implementa lo que `domain/application` necesitan.
- `api` solo llama a `composition`.

## 2. Que hace cada carpeta (que, para que, como, por que)

### `app/domain`
- Que es: el corazon del negocio.
- Para que sirve: definir "que necesita el negocio" sin tecnologia concreta.
- Como lo hace: con `entities.py`, `errors.py`, `ports.py`, `read_models.py`.
- Por que asi: permite cambiar DB/framework sin romper reglas de negocio.

### `app/application`
- Que es: servicios de casos de uso.
- Para que sirve: ejecutar acciones de negocio (crear usuario, actualizar permisos, etc.).
- Como lo hace: recibe puertos de `domain`, valida reglas, coordina transacciones.
- Por que asi: concentra la logica en un punto testeable y desacoplado.

### `app/infrastructure`
- Que es: adaptadores tecnicos reales.
- Para que sirve: hablar con SQLAlchemy, hashing, storage, email, etc.
- Como lo hace: clases tipo `SqlAlchemy...Repository`, `...Writer`, `...Gateway`.
- Por que asi: el detalle tecnico queda aislado y reemplazable.

### `app/composition`
- Que es: "cableado" de dependencias.
- Para que sirve: decidir que implementacion concreta usa cada caso de uso.
- Como lo hace: construye `UseCases(...)` inyectando repositorio, UoW, seguridad, etc.
- Por que asi: evita que API o dominio creen dependencias directamente.

### `app/api`
- Que es: endpoints FastAPI.
- Para que sirve: recibir requests HTTP y devolver responses.
- Como lo hace: valida entrada con schemas, llama funciones de `composition`, traduce errores.
- Por que asi: HTTP queda separado de negocio y se puede cambiar transporte.

## 3. Flujo real de un request (ejemplo usuarios)

1. Entra `POST /v1/users` en `app/api/v1/users.py`.
2. El router toma datos del request y llama `create_user(...)` en `app/composition/users.py`.
3. Composition arma `UsersUseCases` con:
- `SqlAlchemyUsersRepository`
- `SqlAlchemyUsersAuditWriter`
- `SecurityAdapter`
- `SqlAlchemyUnitOfWork`
4. `UsersUseCases.create_user(...)` valida reglas:
- email unico
- no crear otro `SUPERADMIN`
5. Caso de uso guarda usuario, escribe auditoria y hace `commit`.
6. Si algo falla, hace `rollback` y propaga error.
7. API captura error de dominio y responde HTTP apropiado.

## 4. Patrones que ya se estan usando

- Hexagonal (Ports and Adapters): `domain/*/ports.py` + `infrastructure/*`.
- Use Case / Application Service: `application/*/use_cases.py`.
- Repository: `SqlAlchemy...Repository`.
- Unit of Work: `SqlAlchemyUnitOfWork`.
- Composition Root / Dependency Injection manual: `app/composition/*`.

## 5. Como validar que se mantiene hexagonal

Comando de validacion:

```bash
cd backend
python3 scripts/check_hexagonal.py
```

Si todo esta bien, imprime:

```text
Hexagonal boundaries OK
```

## 6. Guia rapida para leer el backend sin perderte

Cuando quieras entender una funcionalidad nueva, sigue este orden:

1. `app/api/v1/<modulo>.py`
2. `app/composition/<modulo>.py`
3. `app/application/<modulo>/use_cases.py`
4. `app/domain/<modulo>/ports.py` y `entities.py`
5. `app/infrastructure/<modulo>/sqlalchemy_repository.py`

Con ese recorrido entiendes "que entra", "que regla corre" y "donde se guarda".

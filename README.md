# Xenith CRM

Sistema de gestión de clientes, proyectos, cotizaciones e inventario RFID.

Arquitectura actual:
- Frontend: Next.js (App Router)
- Backend: FastAPI (`backend/`)
- Base de datos: PostgreSQL
- Autenticación: JWT en cookies `HttpOnly` desde FastAPI

## Requisitos previos
- [Node.js](https://nodejs.org/) v18 o superior
- [Python](https://www.python.org/) 3.11 o superior
- [uv](https://docs.astral.sh/uv/) para dependencias Python
- [Docker](https://www.docker.com/products/docker-desktop/) y Docker Compose

## Inicio rápido
### 1. Instalar dependencias
```bash
npm install
```

### 2. Configurar variables de entorno
Frontend:
```bash
cp .env.example .env
```

Backend:
```bash
cp backend/.env.example backend/.env
```

Variables mínimas:
- Frontend (`.env`): `NEXT_PUBLIC_APP_URL`, `NEXT_PUBLIC_API_URL`
- Backend (`backend/.env`): `DATABASE_URL`, `JWT_ACCESS_SECRET`, `JWT_REFRESH_SECRET`

### 3. Levantar PostgreSQL
```bash
docker compose up -d
```

### 4. Levantar backend FastAPI
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API aplica migraciones automáticamente al iniciar (`AUTO_MIGRATE_ON_START=true`).

### 5. Levantar frontend
```bash
npm run dev
```

Frontend: [http://localhost:3000](http://localhost:3000)  
API: [http://localhost:8000](http://localhost:8000)

## Despliegue (VPS + Docker)
### 1. Variables
Configura:
- `.env` para frontend (`NEXT_PUBLIC_API_URL` apuntando al backend público).
- `backend/.env` para API y servicios (JWT, Resend, R2, DB).

### 2. Construir y levantar
```bash
docker compose up -d --build
```

### 3. Migraciones backend
```bash
cd backend
uv run alembic upgrade head
```

### 4. Verificación
- Frontend cargando.
- `GET /health` del backend responde `{"status":"ok"}`.
- Login y navegación de dashboard funcionales.

## Comandos útiles
| Comando | Descripción |
|---------|-------------|
| `npm run dev` | Inicia frontend en desarrollo |
| `npm run build` | Build de frontend |
| `npm run start` | Frontend en producción |
| `npm run lint` | ESLint del frontend |
| `npm run db:seed` | Seed Prisma |
| `docker compose up -d` | Inicia PostgreSQL |
| `docker compose down` | Detiene PostgreSQL |

Comandos backend adicionales: ver `backend/README.md`.

## Flujo correcto de migraciones (desarrollo)
Cuando cambies modelos SQLAlchemy, crea y versiona la migración antes de levantar cambios:

```bash
cd backend
uv run alembic revision --autogenerate -m "describe-cambio"
uv run alembic upgrade head
uv run alembic check
```

Regla del equipo:
- No crear tablas manualmente en DB.
- No depender de que alguien escriba migraciones a mano si `autogenerate` cubre el cambio.
- Siempre commitear código + archivo de migración juntos.

## Tecnologías
- [Next.js](https://nextjs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Prisma](https://www.prisma.io/) (schema/seed)
- [PostgreSQL](https://www.postgresql.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Zustand](https://zustand-demo.pmnd.rs/)
- [React Hook Form](https://react-hook-form.com/) + [Zod](https://zod.dev/)

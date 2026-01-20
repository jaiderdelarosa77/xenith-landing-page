# Xenith CRM

Sistema de gestión de clientes, proyectos y cotizaciones para Xenith.

## Requisitos previos

- [Node.js](https://nodejs.org/) v18 o superior
- [Docker](https://www.docker.com/products/docker-desktop/) y Docker Compose
- [npm](https://www.npmjs.com/) (incluido con Node.js)

## Inicio rápido

### 1. Clonar e instalar dependencias

```bash
git clone <repo-url>
cd xenith
npm install
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y configura tus variables:

```bash
cp .env.example .env
```

Edita `.env` con tus valores. Para desarrollo local con Docker, los valores por defecto funcionan:

```env
DATABASE_URL="postgresql://xenith:xenith123@localhost:5432/xenith_db"
AUTH_SECRET="tu-secret-aqui"
NEXTAUTH_URL="http://localhost:3000"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

> Genera un secret seguro con: `openssl rand -base64 32`

### 3. Iniciar la base de datos con Docker

```bash
docker compose up -d
```

Esto inicia PostgreSQL en el puerto 5432. Para ver los logs:

```bash
docker compose logs -f
```

Para detener la base de datos:

```bash
docker compose down
```

### 4. Ejecutar migraciones de Prisma

```bash
npx prisma migrate dev
```

Esto crea las tablas en la base de datos y genera el cliente de Prisma.

### 5. (Opcional) Poblar la base de datos con datos de prueba

```bash
npm run db:seed
```

### 6. Iniciar el servidor de desarrollo

```bash
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000) en tu navegador.

## Comandos útiles

| Comando | Descripción |
|---------|-------------|
| `npm run dev` | Inicia el servidor de desarrollo |
| `npm run build` | Genera el build de producción |
| `npm run start` | Inicia el servidor de producción |
| `npm run lint` | Ejecuta ESLint |
| `docker compose up -d` | Inicia PostgreSQL |
| `docker compose down` | Detiene PostgreSQL |
| `npx prisma migrate dev` | Ejecuta migraciones pendientes |
| `npx prisma studio` | Abre Prisma Studio (GUI para la BD) |
| `npm run db:seed` | Puebla la BD con datos de prueba |

## Tecnologías

- [Next.js 16](https://nextjs.org/) - Framework React
- [Prisma](https://www.prisma.io/) - ORM
- [PostgreSQL](https://www.postgresql.org/) - Base de datos
- [NextAuth.js](https://authjs.dev/) - Autenticación
- [Tailwind CSS](https://tailwindcss.com/) - Estilos
- [Zustand](https://zustand-demo.pmnd.rs/) - Estado global
- [React Hook Form](https://react-hook-form.com/) + [Zod](https://zod.dev/) - Formularios y validación

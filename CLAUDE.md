# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

XENITH CRM + Inventory Control System with RFID integration for audiovisual equipment rental. Frontend in Next.js 16 (App Router), backend in FastAPI (`backend/`), PostgreSQL as database.

## Development Commands

```bash
# Development server
npm run dev

# Build & production
npm run build
npm run start

# Linting
npm run lint

# Database
docker compose up -d          # Start PostgreSQL
docker compose down           # Stop PostgreSQL
npx prisma migrate dev        # Run migrations + generate client
npx prisma studio             # Database GUI
npm run db:seed               # Seed demo data (creates superadmin: camilo.vargas@xenith.com.co / admin123)
```

## Architecture

### Route Groups (App Router)
- `app/(auth)/` - Login page
- `app/(dashboard)/` - Protected routes requiring authentication
- `app/(public)/` - Public-facing pages (contacto)

### API Pattern
- El frontend consume FastAPI vía `lib/api/client.ts` (`NEXT_PUBLIC_API_URL`)
- Rutas backend: `backend/app/api/v1/*`
- Auth en backend con JWT en cookies HttpOnly

### State Management
- **Zustand stores** (`store/`): Global state for auth, clients, projects, quotations, UI
- **React Hook Form + Zod**: Form state and validation

### Key Directories
- `components/dashboard/` - Tables, stats cards, data display
- `components/forms/` - Reusable forms with validation
- `components/ui/` - Primitive UI components (Card, Button, etc.)
- `hooks/` - Custom hooks for data fetching (useClients, useProjects, useQuotations)
- `lib/validations/` - Zod schemas for all entities
- `lib/pdf/` - PDF generation with @react-pdf/renderer

### Database Models (Prisma)

#### CRM Models
- **User**: Roles (SUPERADMIN, ADMIN, USER), bcrypt-hashed passwords
- **Client**: Customer records
- **Project**: Status (PROSPECT, IN_PROGRESS, ON_HOLD, COMPLETED, CANCELLED), Priority levels
- **Task**: Sub-tasks within projects (TODO, IN_PROGRESS, DONE)
- **Quotation**: Auto-numbered (QT-YYYY-NNNN), status (DRAFT, SENT, ACCEPTED, REJECTED, EXPIRED)
- **QuotationItem**: Line items with quantity and unit price

#### Inventory Models
- **Category**: Product categories with color/icon
- **Supplier**: Equipment suppliers with contact info
- **Product**: Product catalog with SKU, soft-delete support
- **ProductSupplier**: Many-to-many product-supplier relationship
- **InventoryItem**: Physical items with RFID, status (IN, OUT, MAINTENANCE, LOST)
- **BulkInventory**: Quantity-based inventory without RFID
- **BulkMovement**: Bulk inventory movement history
- **RfidTag**: RFID tags with EPC, status (ENROLLED, UNASSIGNED, UNKNOWN)
- **RfidDetection**: RFID read log from readers
- **InventoryMovement**: Item movement audit trail

### Security Features
- Rate limiting in `lib/security/rate-limiter.ts` (in-memory, consider Redis for production)
- Strong password validation rules in `lib/validations/auth.ts`
- Security headers configured in `next.config.ts`
- Constant-time password comparison

## Environment Setup

Copy `.env.example` to `.env`. Default values work with docker-compose PostgreSQL:
```
DATABASE_URL="postgresql://xenith:xenith123@localhost:5432/xenith_db"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

Backend env: copiar `backend/.env.example` a `backend/.env`.

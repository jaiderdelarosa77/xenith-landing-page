"""Adaptador de infraestructura para `clients` (persistencia concreta)."""

from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.domain.clients.entities import ClientFilters
from app.domain.clients.errors import ClientHasRelationsError, ClientNotFoundError, ClientPersistenceError
from app.models.project_client import Client, Project, Quotation


class SqlAlchemyClientsRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _client_payload(client: Client) -> dict:
        return {
            'id': client.id,
            'name': client.name,
            'company': client.company,
            'email': client.email,
            'phone': client.phone,
            'address': client.address,
            'city': client.city,
            'country': client.country,
            'nit': client.nit,
            'notes': client.notes,
            'rutUrl': client.rut_url,
            'createdAt': client.created_at,
            'updatedAt': client.updated_at,
        }

    def list_clients(self, filters: ClientFilters) -> list[dict]:
        stmt = select(Client).order_by(Client.created_at.desc())
        if filters.search:
            search_like = f'%{filters.search}%'
            stmt = stmt.where(or_(Client.name.ilike(search_like), Client.email.ilike(search_like), Client.company.ilike(search_like)))

        clients = self._db.scalars(stmt).all()
        return [self._client_payload(client) for client in clients]

    def create_client(self, payload: dict) -> dict:
        client = Client(
            id=str(uuid4()),
            name=payload['name'],
            company=payload.get('company'),
            email=payload['email'],
            phone=payload.get('phone'),
            address=payload.get('address'),
            city=payload.get('city'),
            country=payload.get('country'),
            nit=payload.get('nit'),
            notes=payload.get('notes'),
            rut_url=payload.get('rutUrl'),
        )
        self._db.add(client)

        try:
            self._db.flush()
        except IntegrityError:
            raise ClientPersistenceError('No se pudo crear el cliente') from None

        self._db.refresh(client)
        return self._client_payload(client)

    def get_client(self, client_id: str) -> dict:
        client = self._db.scalar(select(Client).where(Client.id == client_id).options(selectinload(Client.projects), selectinload(Client.quotations)))
        if not client:
            raise ClientNotFoundError('Cliente no encontrado')

        payload = self._client_payload(client)
        payload['projects'] = [
            {
                'id': project.id,
                'title': project.title,
                'status': project.status,
                'createdAt': project.created_at,
            }
            for project in sorted(client.projects, key=lambda row: row.created_at, reverse=True)
        ]
        payload['quotations'] = [
            {
                'id': quotation.id,
                'quotationNumber': quotation.quotation_number,
                'title': quotation.title,
                'status': quotation.status,
                'createdAt': quotation.created_at,
            }
            for quotation in sorted(client.quotations, key=lambda row: row.created_at, reverse=True)
        ]
        return payload

    def update_client(self, client_id: str, payload: dict) -> dict:
        client = self._db.get(Client, client_id)
        if not client:
            raise ClientNotFoundError('Cliente no encontrado')

        client.name = payload['name']
        client.company = payload.get('company')
        client.email = payload['email']
        client.phone = payload.get('phone')
        client.address = payload.get('address')
        client.city = payload.get('city')
        client.country = payload.get('country')
        client.nit = payload.get('nit')
        client.notes = payload.get('notes')
        client.rut_url = payload.get('rutUrl')

        try:
            self._db.flush()
        except IntegrityError:
            raise ClientPersistenceError('No se pudo actualizar el cliente') from None

        self._db.refresh(client)
        return self._client_payload(client)

    def delete_client(self, client_id: str) -> dict:
        client = self._db.get(Client, client_id)
        if not client:
            raise ClientNotFoundError('Cliente no encontrado')

        projects_count = self._db.scalar(select(func.count(Project.id)).where(Project.client_id == client_id)) or 0
        quotations_count = self._db.scalar(select(func.count(Quotation.id)).where(Quotation.client_id == client_id)) or 0
        if projects_count > 0 or quotations_count > 0:
            raise ClientHasRelationsError('No se puede eliminar el cliente porque tiene proyectos o cotizaciones asociadas')

        self._db.delete(client)
        self._db.flush()
        return {'success': True}

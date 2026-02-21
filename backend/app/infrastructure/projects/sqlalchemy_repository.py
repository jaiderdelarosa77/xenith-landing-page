"""Adaptador de infraestructura para `projects` (persistencia concreta)."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.domain.projects.entities import ProjectFilters, ProjectInput
from app.domain.projects.errors import (
    InvalidDateFormatError,
    ProjectNotFoundError,
    ProjectPersistenceError,
)
from app.domain.projects.read_models import ProjectMutationResult, ProjectView
from app.models.project_client import Client, Project, Task
from app.models.user import User


class SqlAlchemyProjectsRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _parse_date(value: str | None):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise InvalidDateFormatError('Formato de fecha invalido') from None

    @staticmethod
    def _project_payload(project: Project, include_deep: bool = False) -> ProjectView:
        payload = {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'status': project.status,
            'clientId': project.client_id,
            'assignedTo': project.assigned_to,
            'startDate': project.start_date,
            'endDate': project.end_date,
            'budget': float(project.budget) if project.budget is not None else None,
            'priority': project.priority,
            'tags': project.tags or [],
            'notes': project.notes,
            'createdAt': project.created_at,
            'updatedAt': project.updated_at,
            'client': {
                'id': project.client.id,
                'name': project.client.name,
                'company': project.client.company,
                'email': project.client.email,
            }
            if project.client
            else None,
            'assignedUser': {
                'id': project.assigned_user.id,
                'name': project.assigned_user.name,
                'email': project.assigned_user.email,
            }
            if project.assigned_user
            else None,
            'tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'status': task.status,
                    'priority': task.priority,
                    'completed': task.completed,
                    'dueDate': task.due_date,
                    'assignedTo': task.assigned_to,
                    'assignedUser': {
                        'id': task.assigned_user.id,
                        'name': task.assigned_user.name,
                        'email': task.assigned_user.email,
                    }
                    if task.assigned_user
                    else None,
                }
                for task in sorted(project.tasks, key=lambda row: row.created_at, reverse=include_deep)
            ],
        }

        if include_deep:
            payload['quotations'] = [
                {
                    'id': quotation.id,
                    'quotationNumber': quotation.quotation_number,
                    'title': quotation.title,
                    'status': quotation.status,
                    'total': float(quotation.total),
                    'createdAt': quotation.created_at,
                }
                for quotation in sorted(project.quotations, key=lambda row: row.created_at, reverse=True)
            ]

        return payload

    def list_projects(self, filters: ProjectFilters) -> list[ProjectView]:
        conditions = []

        if filters.search:
            search_like = f'%{filters.search}%'
            conditions.append(or_(Project.title.ilike(search_like), Project.description.ilike(search_like)))

        if filters.status_filter:
            conditions.append(Project.status == filters.status_filter)
        if filters.priority:
            conditions.append(Project.priority == filters.priority)
        if filters.client_id:
            conditions.append(Project.client_id == filters.client_id)
        if filters.assigned_to:
            conditions.append(Project.assigned_to == filters.assigned_to)

        stmt = (
            select(Project)
            .options(
                selectinload(Project.client),
                selectinload(Project.assigned_user),
                selectinload(Project.tasks).selectinload(Task.assigned_user),
            )
            .order_by(Project.created_at.desc())
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))

        projects = self._db.scalars(stmt).all()
        return [self._project_payload(project) for project in projects]

    def create_project(self, payload: ProjectInput) -> ProjectView:
        budget_value = float(payload.budget) if payload.budget else None

        project = Project(
            id=str(uuid4()),
            title=payload.title,
            description=payload.description,
            status=payload.status,
            client_id=payload.client_id,
            assigned_to=payload.assigned_to,
            start_date=self._parse_date(payload.start_date),
            end_date=self._parse_date(payload.end_date),
            budget=budget_value,
            priority=payload.priority,
            tags=payload.tags or [],
            notes=payload.notes,
        )
        self._db.add(project)
        self._db.flush()

        for task in payload.tasks:
            self._db.add(
                Task(
                    id=str(uuid4()),
                    project_id=project.id,
                    title=task.title,
                    description=task.description,
                    status='TODO',
                    assigned_to=task.assigned_to,
                    due_date=self._parse_date(task.due_date),
                    priority=task.priority,
                    completed=False,
                )
            )

        try:
            self._db.flush()
        except IntegrityError:
            raise ProjectPersistenceError('No se pudo crear el proyecto') from None

        project = self._db.scalar(
            select(Project)
            .where(Project.id == project.id)
            .options(
                selectinload(Project.client),
                selectinload(Project.assigned_user),
                selectinload(Project.tasks).selectinload(Task.assigned_user),
            )
        )
        return self._project_payload(project)

    def get_project(self, project_id: str) -> ProjectView:
        project = self._db.scalar(
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.client),
                selectinload(Project.assigned_user),
                selectinload(Project.tasks).selectinload(Task.assigned_user),
                selectinload(Project.quotations),
            )
        )

        if not project:
            raise ProjectNotFoundError('Proyecto no encontrado')

        return self._project_payload(project, include_deep=True)

    def update_project(self, project_id: str, payload: ProjectInput) -> ProjectView:
        project = self._db.get(Project, project_id)
        if not project:
            raise ProjectNotFoundError('Proyecto no encontrado')

        project.title = payload.title
        project.description = payload.description
        project.status = payload.status
        project.client_id = payload.client_id
        project.assigned_to = payload.assigned_to
        project.start_date = self._parse_date(payload.start_date)
        project.end_date = self._parse_date(payload.end_date)
        project.budget = float(payload.budget) if payload.budget else None
        project.priority = payload.priority
        project.tags = payload.tags or []
        project.notes = payload.notes

        self._db.execute(delete(Task).where(Task.project_id == project_id))
        for task in payload.tasks:
            self._db.add(
                Task(
                    id=str(uuid4()),
                    project_id=project_id,
                    title=task.title,
                    description=task.description,
                    status='TODO',
                    assigned_to=task.assigned_to,
                    due_date=self._parse_date(task.due_date),
                    priority=task.priority,
                    completed=False,
                )
            )

        try:
            self._db.flush()
        except IntegrityError:
            raise ProjectPersistenceError('No se pudo actualizar el proyecto') from None

        project = self._db.scalar(
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.client),
                selectinload(Project.assigned_user),
                selectinload(Project.tasks).selectinload(Task.assigned_user),
            )
        )
        return self._project_payload(project)

    def delete_project(self, project_id: str) -> ProjectMutationResult:
        project = self._db.get(Project, project_id)
        if not project:
            raise ProjectNotFoundError('Proyecto no encontrado')

        self._db.delete(project)
        self._db.flush()
        return {'success': True}

    def client_exists(self, client_id: str) -> bool:
        return self._db.get(Client, client_id) is not None

    def assigned_user_exists(self, user_id: str) -> bool:
        return self._db.get(User, user_id) is not None

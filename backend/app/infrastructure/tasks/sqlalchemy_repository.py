"""Adaptador de infraestructura para `tasks` (persistencia concreta)."""

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, selectinload

from app.domain.tasks.entities import TaskFilters
from app.domain.tasks.errors import TaskNotFoundError
from app.models.project_client import Project, Task


class SqlAlchemyTasksRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    @staticmethod
    def _task_payload(task: Task) -> dict:
        return {
            'id': task.id,
            'projectId': task.project_id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'assignedTo': task.assigned_to,
            'dueDate': task.due_date,
            'priority': task.priority,
            'completed': task.completed,
            'createdAt': task.created_at,
            'updatedAt': task.updated_at,
            'project': {
                'id': task.project.id,
                'title': task.project.title,
                'status': task.project.status,
            }
            if task.project
            else None,
            'assignedUser': {
                'id': task.assigned_user.id,
                'name': task.assigned_user.name,
                'email': task.assigned_user.email,
            }
            if task.assigned_user
            else None,
        }

    def list_tasks(self, filters: TaskFilters) -> list[dict]:
        conditions = []

        if filters.search:
            search_like = f'%{filters.search}%'
            conditions.append(
                or_(
                    Task.title.ilike(search_like),
                    Task.description.ilike(search_like),
                    Task.project.has(Project.title.ilike(search_like)),
                )
            )

        if filters.status_filter:
            conditions.append(Task.status == filters.status_filter)
        if filters.priority:
            conditions.append(Task.priority == filters.priority)
        if filters.assigned_to:
            conditions.append(Task.assigned_to == filters.assigned_to)
        if filters.my_tasks:
            conditions.append(Task.assigned_to == filters.current_user_id)

        stmt = (
            select(Task)
            .options(selectinload(Task.project), selectinload(Task.assigned_user))
            .order_by(Task.status.asc(), Task.priority.desc(), Task.due_date.asc(), Task.created_at.desc())
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))

        tasks = self._db.scalars(stmt).all()
        return [self._task_payload(task) for task in tasks]

    def get_task(self, task_id: str) -> dict:
        task = self._db.scalar(select(Task).where(Task.id == task_id).options(selectinload(Task.project), selectinload(Task.assigned_user)))
        if not task:
            raise TaskNotFoundError('Tarea no encontrada')
        return self._task_payload(task)

    def update_task(self, task_id: str, payload: dict) -> dict:
        task = self._db.get(Task, task_id)
        if not task:
            raise TaskNotFoundError('Tarea no encontrada')

        status = payload.get('status')
        completed = payload.get('completed')

        if status is not None:
            task.status = status
            task.completed = status == 'DONE'

        if completed is not None:
            task.completed = completed
            if completed and status is None:
                task.status = 'DONE'

        self._db.flush()
        task = self._db.scalar(select(Task).where(Task.id == task_id).options(selectinload(Task.project), selectinload(Task.assigned_user)))
        return self._task_payload(task)

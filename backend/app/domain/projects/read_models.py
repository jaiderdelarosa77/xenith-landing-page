"""Modelos tipados de lectura para `projects` (salidas/consultas)."""

from typing import NotRequired, TypedDict


class ProjectUserView(TypedDict):
    id: str
    name: str
    email: str


class ProjectClientView(TypedDict):
    id: str
    name: str
    company: str | None
    email: str | None


class ProjectTaskView(TypedDict):
    id: str
    title: str
    description: str | None
    status: str
    priority: str
    completed: bool
    dueDate: object | None
    assignedTo: str | None
    assignedUser: ProjectUserView | None


class ProjectQuotationView(TypedDict):
    id: str
    quotationNumber: str
    title: str
    status: str
    total: float
    createdAt: object


class ProjectView(TypedDict):
    id: str
    title: str
    description: str
    status: str
    clientId: str
    assignedTo: str
    startDate: object | None
    endDate: object | None
    budget: float | None
    priority: str
    tags: list[str]
    notes: str | None
    createdAt: object
    updatedAt: object
    client: ProjectClientView | None
    assignedUser: ProjectUserView | None
    tasks: list[ProjectTaskView]
    quotations: NotRequired[list[ProjectQuotationView]]


class ProjectMutationResult(TypedDict):
    success: bool

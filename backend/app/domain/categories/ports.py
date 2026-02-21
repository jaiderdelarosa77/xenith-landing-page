"""Puertos (interfaces) del dominio `categories` para desacoplar infraestructura."""

from typing import Protocol

from app.domain.categories.entities import CategoryFilters
from app.domain.categories.read_models import CategoryMutationResult, CategoryPayload, CategoryView


class CategoriesRepository(Protocol):
    def list_categories(self, filters: CategoryFilters) -> list[CategoryView]: ...

    def create_category(self, payload: CategoryPayload) -> CategoryView: ...

    def get_category(self, category_id: str) -> CategoryView: ...

    def update_category(self, category_id: str, payload: CategoryPayload) -> CategoryView: ...

    def delete_category(self, category_id: str) -> CategoryMutationResult: ...


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...

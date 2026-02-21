"""Casos de uso de `categories`.

Orquesta reglas de negocio, validaciones y transacciones.
"""

from app.domain.categories.entities import CategoryFilters
from app.domain.categories.ports import CategoriesRepository, UnitOfWork
from app.domain.categories.read_models import CategoryMutationResult, CategoryPayload, CategoryView


class CategoriesUseCases:
    def __init__(self, repo: CategoriesRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def list_categories(self, filters: CategoryFilters) -> list[CategoryView]:
        return self._repo.list_categories(filters)

    def create_category(self, payload: CategoryPayload) -> CategoryView:
        try:
            result = self._repo.create_category(payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def get_category(self, category_id: str) -> CategoryView:
        return self._repo.get_category(category_id)

    def update_category(self, category_id: str, payload: CategoryPayload) -> CategoryView:
        try:
            result = self._repo.update_category(category_id, payload)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def delete_category(self, category_id: str) -> CategoryMutationResult:
        try:
            result = self._repo.delete_category(category_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

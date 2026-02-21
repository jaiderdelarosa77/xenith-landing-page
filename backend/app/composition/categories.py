"""Composition root de `categories`: conecta casos de uso con adaptadores concretos."""

from app.application.categories.use_cases import CategoriesUseCases
from app.domain.categories.entities import CategoryFilters
from app.domain.categories.errors import CategoryDuplicateNameError, CategoryHasProductsError, CategoryNotFoundError
from app.infrastructure.categories.sqlalchemy_repository import SqlAlchemyCategoriesRepository
from app.infrastructure.common.unit_of_work import SqlAlchemyUnitOfWork


def _use_cases(db) -> CategoriesUseCases:
    return CategoriesUseCases(
        repo=SqlAlchemyCategoriesRepository(db),
        uow=SqlAlchemyUnitOfWork(db),
    )


def list_categories(db, *, search: str) -> list[dict]:
    return _use_cases(db).list_categories(CategoryFilters(search=search))


def create_category(db, *, payload: dict) -> dict:
    return _use_cases(db).create_category(payload)


def get_category(db, category_id: str) -> dict:
    return _use_cases(db).get_category(category_id)


def update_category(db, *, category_id: str, payload: dict) -> dict:
    return _use_cases(db).update_category(category_id, payload)


def delete_category(db, category_id: str) -> dict:
    return _use_cases(db).delete_category(category_id)


__all__ = [
    'CategoryDuplicateNameError',
    'CategoryHasProductsError',
    'CategoryNotFoundError',
    'create_category',
    'delete_category',
    'get_category',
    'list_categories',
    'update_category',
]

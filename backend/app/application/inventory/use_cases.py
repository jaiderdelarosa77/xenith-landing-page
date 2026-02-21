"""Casos de uso del módulo de inventario.

Responsabilidad de esta capa:
- validar reglas de negocio,
- coordinar repositorio + transacciones (Unit of Work),
- devolver errores de dominio claros.
"""

from app.domain.inventory.entities import CheckInOutInput, InventoryItemInput, InventoryListFilters, MovementListFilters
from app.domain.inventory.errors import (
    AlreadyCheckedInError,
    AlreadyCheckedOutError,
    ContainerHasItemsError,
    InvalidInventoryFiltersError,
    InvalidInventoryPayloadError,
    InventoryPersistenceError,
    LostItemCheckOutError,
)
from app.domain.inventory.ports import InventoryRepository, UnitOfWork
from app.domain.inventory.read_models import (
    InventoryCheckInOutResult,
    InventoryItemView,
    InventoryMovementsPageView,
    InventoryMutationResult,
    InventorySummaryView,
)

ALLOWED_ITEM_STATUSES = {'IN', 'OUT', 'MAINTENANCE', 'LOST'}
ALLOWED_ITEM_TYPES = {'UNIT', 'CONTAINER'}
ALLOWED_MOVEMENT_TYPES = {'CHECK_IN', 'CHECK_OUT', 'ADJUSTMENT', 'ENROLLMENT', 'TRANSFER'}


class InventoryUseCases:
    """Servicio de aplicación para operaciones de inventario."""

    def __init__(self, repo: InventoryRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def list_items(self, filters: InventoryListFilters) -> list[InventoryItemView]:
        # Validamos filtros aquí para no pasar datos inválidos al repositorio.
        if filters.status_filter and filters.status_filter not in ALLOWED_ITEM_STATUSES:
            raise InvalidInventoryFiltersError('Filtro de estado invalido')
        if filters.type_filter and filters.type_filter not in ALLOWED_ITEM_TYPES:
            raise InvalidInventoryFiltersError('Filtro de tipo invalido')
        return self._repo.list_items(filters)

    def create_item(self, payload: InventoryItemInput, user_id: str) -> InventoryItemView:
        # Se valida negocio antes de tocar persistencia.
        self._validate_payload(payload)
        if not user_id:
            raise InvalidInventoryPayloadError('Usuario invalido')
        try:
            result = self._repo.create_item(payload, user_id)
            # Si todo sale bien, confirmamos la transacción.
            self._uow.commit()
            return result
        except Exception as exc:
            # Si algo falla, dejamos el sistema consistente.
            self._uow.rollback()
            if isinstance(exc, InventoryPersistenceError):
                raise
            raise

    def summary(self) -> InventorySummaryView:
        return self._repo.summary()

    def list_movements(self, filters: MovementListFilters) -> InventoryMovementsPageView:
        # Reglas de paginación para proteger performance y evitar consultas inválidas.
        if filters.type_filter and filters.type_filter not in ALLOWED_MOVEMENT_TYPES:
            raise InvalidInventoryFiltersError('Filtro de movimiento invalido')
        if filters.limit <= 0 or filters.limit > 200:
            raise InvalidInventoryFiltersError('El limite debe estar entre 1 y 200')
        if filters.offset < 0:
            raise InvalidInventoryFiltersError('El offset no puede ser negativo')
        return self._repo.list_movements(filters)

    def get_item(self, item_id: str) -> InventoryItemView:
        if not item_id:
            raise InvalidInventoryFiltersError('ID de item invalido')
        return self._repo.get_item(item_id)

    def update_item(self, item_id: str, payload: InventoryItemInput, user_id: str) -> InventoryItemView:
        if not item_id:
            raise InvalidInventoryFiltersError('ID de item invalido')
        self._validate_payload(payload)
        if not user_id:
            raise InvalidInventoryPayloadError('Usuario invalido')
        try:
            result = self._repo.update_item(item_id, payload, user_id)
            self._uow.commit()
            return result
        except Exception as exc:
            self._uow.rollback()
            if isinstance(exc, InventoryPersistenceError):
                raise
            raise

    def delete_item(self, item_id: str) -> InventoryMutationResult:
        if not item_id:
            raise InvalidInventoryFiltersError('ID de item invalido')
        item = self._repo.get_item(item_id)
        # Regla de negocio: no borrar contenedores que aún tienen contenido.
        if item['_count']['contents'] > 0:
            raise ContainerHasItemsError('No se puede eliminar un contenedor con items dentro')
        try:
            result = self._repo.delete_item(item_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def check_in(self, item_id: str, payload: CheckInOutInput, user_id: str) -> InventoryCheckInOutResult:
        if not item_id:
            raise InvalidInventoryFiltersError('ID de item invalido')
        if not user_id:
            raise InvalidInventoryPayloadError('Usuario invalido')
        current_item = self._repo.get_item(item_id)
        # Evitamos movimientos redundantes.
        if current_item['status'] == 'IN':
            raise AlreadyCheckedInError('El item ya esta en bodega')
        try:
            result = self._repo.check_in(item_id, payload, user_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    def check_out(self, item_id: str, payload: CheckInOutInput, user_id: str) -> InventoryCheckInOutResult:
        if not item_id:
            raise InvalidInventoryFiltersError('ID de item invalido')
        if not user_id:
            raise InvalidInventoryPayloadError('Usuario invalido')
        current_item = self._repo.get_item(item_id)
        if current_item['status'] == 'OUT':
            raise AlreadyCheckedOutError('El item ya esta fuera')
        # Regla de seguridad: un item perdido no puede salir nuevamente.
        if current_item['status'] == 'LOST':
            raise LostItemCheckOutError('No se puede hacer check-out de un item perdido')
        try:
            result = self._repo.check_out(item_id, payload, user_id)
            self._uow.commit()
            return result
        except Exception:
            self._uow.rollback()
            raise

    @staticmethod
    def _validate_payload(payload: InventoryItemInput) -> None:
        """Valida reglas mínimas del payload de inventario."""
        if not payload.product_id:
            raise InvalidInventoryPayloadError('El producto es obligatorio')
        if payload.item_type not in ALLOWED_ITEM_TYPES:
            raise InvalidInventoryPayloadError('Tipo de item invalido')
        if payload.status not in ALLOWED_ITEM_STATUSES:
            raise InvalidInventoryPayloadError('Estado de item invalido')
        if payload.purchase_price is not None and payload.purchase_price < 0:
            raise InvalidInventoryPayloadError('El precio de compra no puede ser negativo')

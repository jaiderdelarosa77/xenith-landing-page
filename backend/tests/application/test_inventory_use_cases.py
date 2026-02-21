import pytest

from app.application.inventory.use_cases import InventoryUseCases
from app.domain.inventory.entities import CheckInOutInput, InventoryItemInput, InventoryListFilters, MovementListFilters
from app.domain.inventory.errors import (
    AlreadyCheckedInError,
    ContainerHasItemsError,
    InvalidInventoryFiltersError,
    InvalidInventoryPayloadError,
)


class FakeInventoryRepo:
    def __init__(self):
        self.item_status = 'IN'
        self.contents_count = 0

    def list_items(self, filters):
        return [{'id': 'i1', 'filters': filters}]

    def create_item(self, payload, user_id):
        return {'id': 'i2', 'payload': payload, 'userId': user_id}

    def summary(self):
        return {'total': 1}

    def list_movements(self, filters):
        return {'movements': [], 'filters': filters}

    def get_item(self, item_id):
        return {
            'id': item_id,
            'status': self.item_status,
            '_count': {'contents': self.contents_count, 'movements': 0},
        }

    def update_item(self, item_id, payload, user_id):
        return {'id': item_id, 'payload': payload, 'userId': user_id}

    def delete_item(self, item_id):
        return {'success': True, 'id': item_id}

    def check_in(self, item_id, payload, user_id):
        return {'id': item_id, 'userId': user_id, 'location': payload.location}

    def check_out(self, item_id, payload, user_id):
        return {'id': item_id, 'userId': user_id, 'location': payload.location}


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def _build():
    uow = FakeUow()
    repo = FakeInventoryRepo()
    uc = InventoryUseCases(repo, uow)
    return uc, uow, repo


def _item_input() -> InventoryItemInput:
    return InventoryItemInput(
        product_id='p1',
        serial_number=None,
        asset_tag=None,
        item_type='UNIT',
        status='IN',
        condition=None,
        location=None,
        container_id=None,
        purchase_date=None,
        purchase_price=None,
        warranty_expiry=None,
        notes=None,
    )


def test_list_movements_invalid_limit_raises() -> None:
    uc, _, _ = _build()

    with pytest.raises(InvalidInventoryFiltersError):
        uc.list_movements(MovementListFilters(type_filter='', inventory_item_id='', limit=0, offset=0))


def test_list_items_invalid_status_filter_raises() -> None:
    uc, _, _ = _build()

    with pytest.raises(InvalidInventoryFiltersError):
        uc.list_items(InventoryListFilters(search='', status_filter='INVALID', type_filter='', product_id='', container_id=''))


def test_update_item_requires_user_id() -> None:
    uc, _, _ = _build()

    with pytest.raises(InvalidInventoryPayloadError):
        uc.update_item('i1', _item_input(), '')


def test_check_out_delegates_when_inputs_are_valid() -> None:
    uc, uow, _ = _build()

    result = uc.check_out('i1', CheckInOutInput(location='Bodega', reason=None, reference=None), 'u1')

    assert result['id'] == 'i1'
    assert result['userId'] == 'u1'
    assert uow.commits == 1


def test_create_item_rejects_invalid_type() -> None:
    uc, _, _ = _build()
    payload = _item_input()
    payload.item_type = 'INVALID'

    with pytest.raises(InvalidInventoryPayloadError):
        uc.create_item(payload, 'u1')


def test_create_item_commits_on_success() -> None:
    uc, uow, _ = _build()

    uc.create_item(_item_input(), 'u1')

    assert uow.commits == 1
    assert uow.rollbacks == 0


def test_check_in_raises_when_item_already_in() -> None:
    uc, _, repo = _build()
    repo.item_status = 'IN'

    with pytest.raises(AlreadyCheckedInError):
        uc.check_in('i1', CheckInOutInput(location=None, reason=None, reference=None), 'u1')


def test_delete_item_raises_when_container_has_contents() -> None:
    uc, _, repo = _build()
    repo.contents_count = 2

    with pytest.raises(ContainerHasItemsError):
        uc.delete_item('i1')

import pytest

from app.application.rfid.use_cases import RfidUseCases
from app.domain.rfid.entities import DetectionFilters, TagFilters


class FakeRepo:
    def list_tags(self, filters: TagFilters):
        return [{'id': 't1', 'filters': filters}]

    def create_tag(self, payload: dict):
        return {'id': 't2'}

    def list_unknown_tags(self):
        return [{'id': 'tu1'}]

    def get_tag(self, tag_id: str):
        return {'id': tag_id}

    def update_tag(self, tag_id: str, payload: dict):
        return {'id': tag_id}

    def delete_tag(self, tag_id: str):
        return {'success': True}

    def enroll_tag(self, tag_id: str, inventory_item_id: str):
        return {'success': True}

    def unenroll_tag(self, tag_id: str):
        return {'success': True}

    def list_detections(self, filters: DetectionFilters):
        return {'detections': [], 'filters': filters}

    def process_read(self, payload: dict, api_key: str):
        if payload.get('fail'):
            raise RuntimeError('read error')
        return {'success': True}


class FakeUow:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_create_tag_commits() -> None:
    uow = FakeUow()
    uc = RfidUseCases(FakeRepo(), uow)

    result = uc.create_tag({'epc': 'E1'})

    assert result['id'] == 't2'
    assert uow.commits == 1


def test_process_read_rolls_back_on_error() -> None:
    uow = FakeUow()
    uc = RfidUseCases(FakeRepo(), uow)

    with pytest.raises(RuntimeError):
        uc.process_read({'fail': True}, 'key')

    assert uow.rollbacks == 1


def test_list_tags_delegates_filters() -> None:
    uc = RfidUseCases(FakeRepo(), FakeUow())
    result = uc.list_tags(TagFilters(search='epc', status_filter='ASSIGNED'))

    assert result[0]['id'] == 't1'

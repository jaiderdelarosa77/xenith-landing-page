from app.application.bootstrap.use_cases import ensure_superadmin_use_case


class FakeGateway:
    def __init__(self):
        self.called = False
        self.payload = None
        self.result = 'created'

    def ensure_superadmin(self, email: str, name: str, password: str | None, force_password_reset: bool) -> str:
        self.called = True
        self.payload = {
            'email': email,
            'name': name,
            'password': password,
            'force_password_reset': force_password_reset,
        }
        return self.result


class FakeUnitOfWork:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def test_ensure_superadmin_normalizes_email() -> None:
    gateway = FakeGateway()
    uow = FakeUnitOfWork()

    ensure_superadmin_use_case(gateway, uow, ' Admin@Example.com ', 'Admin', 'secret', False)

    assert gateway.called
    assert gateway.payload['email'] == 'admin@example.com'
    assert uow.commits == 1
    assert uow.rollbacks == 0


def test_ensure_superadmin_skips_when_email_empty() -> None:
    gateway = FakeGateway()
    uow = FakeUnitOfWork()

    ensure_superadmin_use_case(gateway, uow, '   ', 'Admin', 'secret', False)

    assert not gateway.called
    assert uow.commits == 0
    assert uow.rollbacks == 0

from __future__ import annotations

import ast
import sys
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1] / 'app'

FORBIDDEN_IN_DOMAIN = (
    'app.api',
    'app.application',
    'app.composition',
    'app.db',
    'app.infrastructure',
    'app.models',
    'alembic',
    'boto3',
    'fastapi',
    'httpx',
    'reportlab',
    'sqlalchemy',
)

FORBIDDEN_IN_APPLICATION = (
    'app.api',
    'app.composition',
    'app.db',
    'app.infrastructure',
    'app.models',
    'fastapi',
    'sqlalchemy',
)

FORBIDDEN_IN_API = (
    'app.infrastructure',
    'app.models',
)


def _imports_for_file(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    imports: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            if module:
                imports.append((node.lineno, module))
    return imports


def _violations(path: Path, forbidden_prefixes: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    for lineno, module in _imports_for_file(path):
        if module.startswith('app.domain'):
            continue
        if module in {'dataclasses', 'datetime', 'typing', 'uuid', 'hashlib', 'logging'}:
            continue
        for prefix in forbidden_prefixes:
            if module == prefix or module.startswith(f'{prefix}.'):
                rel = path.relative_to(APP_ROOT.parent)
                errors.append(f'{rel}:{lineno} importa "{module}" (forbidden: {prefix})')
                break
    return errors


def main() -> int:
    errors: list[str] = []

    for path in sorted((APP_ROOT / 'domain').rglob('*.py')):
        errors.extend(_violations(path, FORBIDDEN_IN_DOMAIN))

    for path in sorted((APP_ROOT / 'application').rglob('*.py')):
        if path.name == '__init__.py':
            continue
        errors.extend(_violations(path, FORBIDDEN_IN_APPLICATION))

    for path in sorted((APP_ROOT / 'api').rglob('*.py')):
        if path.name == '__init__.py':
            continue
        errors.extend(_violations(path, FORBIDDEN_IN_API))

    if errors:
        print('Hexagonal boundary violations found:')
        for err in errors:
            print(f'- {err}')
        return 1

    print('Hexagonal boundaries OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())

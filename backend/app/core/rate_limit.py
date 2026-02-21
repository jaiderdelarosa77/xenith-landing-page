"""Utilidades core del backend (`rate_limit`)."""

import time
from dataclasses import dataclass


@dataclass
class RateLimitResult:
    success: bool
    remaining: int
    reset_at: int


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._store: dict[str, tuple[int, int]] = {}

    def check(self, key: str, max_attempts: int, window_seconds: int) -> RateLimitResult:
        now = int(time.time())
        count, reset_at = self._store.get(key, (0, now + window_seconds))

        if now >= reset_at:
            count = 0
            reset_at = now + window_seconds

        if count >= max_attempts:
            return RateLimitResult(False, 0, reset_at)

        count += 1
        self._store[key] = (count, reset_at)
        return RateLimitResult(True, max_attempts - count, reset_at)

    def reset(self, key: str) -> None:
        self._store.pop(key, None)


rate_limiter = InMemoryRateLimiter()

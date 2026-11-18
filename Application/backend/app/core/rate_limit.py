"""R1.7: simple in-memory fixed-window rate limiter, keyed by (bucket, client IP).

Intentionally a tiny custom dependency rather than a new library, per project constraints.
Uses the real wall clock (not the injectable `get_now`) since request pacing is an
infrastructure concern, independent of the business-time clock used for slots/coupons.
"""
import time
from collections import defaultdict

from fastapi import Request

from app.core.errors import RateLimitedError

_hits: dict[str, list[float]] = defaultdict(list)


def reset_rate_limits() -> None:
    _hits.clear()


def rate_limiter(bucket: str, max_requests: int = 10, window_seconds: int = 60):
    async def _dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{bucket}:{client_ip}"
        now = time.time()
        window_start = now - window_seconds
        hits = [t for t in _hits[key] if t > window_start]
        if len(hits) >= max_requests:
            oldest = min(hits)
            retry_after = max(1, int(oldest + window_seconds - now) + 1)
            _hits[key] = hits
            raise RateLimitedError(retry_after)
        hits.append(now)
        _hits[key] = hits

    return _dependency

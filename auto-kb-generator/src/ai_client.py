import time

import httpx

RETRYABLE_ERRORS = (
    httpx.RemoteProtocolError,
    httpx.ReadTimeout,
    httpx.ConnectTimeout,
    httpx.ConnectError,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
)

DEFAULT_TIMEOUT_MS = 180_000


def chat_complete(client, *, max_attempts=3, retry_delay=3, timeout_ms=DEFAULT_TIMEOUT_MS, **kwargs):
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            return client.chat.complete(timeout_ms=timeout_ms, **kwargs)
        except RETRYABLE_ERRORS as exc:
            last_error = exc
            if attempt == max_attempts:
                raise
            wait = retry_delay * attempt
            print(f"Mistral API error: {exc}. Retry {attempt}/{max_attempts} in {wait}s...")
            time.sleep(wait)

    raise last_error

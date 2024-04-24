import itertools
import logging
from functools import wraps
from time import sleep

from redis.exceptions import ConnectionError, TimeoutError

from matter_persistence.redis.exceptions import CacheServerError

logger = logging.getLogger(__name__)


def retry_if_failed(func, delays=(0, 1, 5)):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        for delay in itertools.chain(delays, [None]):
            try:
                result = await func(*args, **kwargs)

            except ConnectionError as exc:
                operation_successful = False
                error_message = str(exc)
                error_type = type(exc).__name__
                needs_retry = True
                detail = {
                    "exception": exc,
                    "error_type": error_type,
                    "error_message": error_message,
                }
                new_exc = CacheServerError(
                    description=f"Unable to connect to Redis: {error_message}",
                    detail=detail,
                )

            except TimeoutError as exc:
                operation_successful = False
                error_message = str(exc)
                error_type = type(exc).__name__
                needs_retry = False
                detail = {
                    "exception": exc,
                    "error_type": error_type,
                    "error_message": error_message,
                }
                new_exc = CacheServerError(
                    description=f"Redis operation timed out: {error_message}",
                    detail=detail,
                )

            else:
                operation_successful = True
                needs_retry = False

            if not needs_retry or delay is None:
                if not operation_successful:
                    raise new_exc
                return result
            else:
                logging.warning(f"Unable to connect to Cache due to {error_type}. Retrying in {delay} seconds...")
                sleep(delay)

    return async_wrapper

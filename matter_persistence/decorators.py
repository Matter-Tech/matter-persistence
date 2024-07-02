import itertools
import logging
from enum import Enum
from functools import wraps
from time import sleep

from redis.exceptions import ConnectionError, TimeoutError
from sqlalchemy.exc import IntegrityError, OperationalError

from matter_persistence.redis.exceptions import CacheServerError
from matter_persistence.sql.exceptions import DatabaseError, DatabaseIntegrityError

logger = logging.getLogger(__name__)


class OperationOutcome(Enum):
    CACHE_ERROR = "CACHE_ERROR"
    SQL_ERROR = "SQL_ERROR"
    SUCCESS = "SUCCESS"


def _exception_to_details(exception: BaseException) -> dict:
    return {
        "exception": exception,
        "error_type": str(exception),
        "error_message": type(exception).__name__,
    }


def retry_if_failed(func, delays=(0, 1, 5)):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        operation_outcome = OperationOutcome.SUCCESS  # assume success
        last_exception: Exception | None = None
        for delay in itertools.chain(delays, [None]):
            try:
                result = await func(*args, **kwargs)
            except OperationalError as exc:
                operation_outcome = OperationOutcome.SQL_ERROR
                needs_retry = True
                new_exc = DatabaseError(
                    description=f"Unable to perform database operation: {type(exc).__name__}",
                    detail=_exception_to_details(exc),
                )
                last_exception = exc
            except IntegrityError as exc:
                operation_outcome = OperationOutcome.SQL_ERROR
                needs_retry = False
                new_exc = DatabaseIntegrityError(
                    description=f"Violation of rules or conditions: {type(exc).__name__}",
                    detail=_exception_to_details(exc),
                )
                last_exception = exc
            except ConnectionError as exc:
                operation_outcome = OperationOutcome.CACHE_ERROR
                needs_retry = True
                new_exc = CacheServerError(
                    description=f"Unable to connect to Redis: {type(exc).__name__}",
                    detail=_exception_to_details(exc),
                )
                last_exception = exc
            except TimeoutError as exc:
                operation_outcome = OperationOutcome.CACHE_ERROR
                needs_retry = False
                new_exc = CacheServerError(
                    description=f"Redis operation timed out: {type(exc).__name__}",
                    detail=_exception_to_details(exc),
                )
                last_exception = exc
            else:
                needs_retry = False
                new_exc = None

            if not needs_retry or delay is None:
                if (
                    operation_outcome in [OperationOutcome.CACHE_ERROR, OperationOutcome.SQL_ERROR]
                    and new_exc is not None
                ):
                    raise new_exc from last_exception
                return result
            else:
                storage = "database" if operation_outcome == OperationOutcome.SQL_ERROR else "cache"
                logging.warning(
                    f"Unable to connect to {storage} due to {type(last_exception)}. Retrying in {delay} seconds...",
                )
                sleep(delay)

    return async_wrapper

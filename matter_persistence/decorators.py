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


def retry_if_failed(func, delays=(0, 1, 5)):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        operation_outcome = OperationOutcome.SUCCESS  # assume success
        for delay in itertools.chain(delays, [None]):
            try:
                result = await func(*args, **kwargs)

            except OperationalError as exc:
                operation_outcome = OperationOutcome.SQL_ERROR
                error_message = str(exc)
                error_type = type(exc).__name__
                needs_retry = True
                detail = {
                    "exception": exc,
                    "error_type": error_type,
                    "error_message": error_message,
                }
                new_exc = DatabaseError(
                    description=f"Unable to perform database operation: {error_message}",
                    detail=detail,
                )

            except IntegrityError as exc:
                operation_outcome = OperationOutcome.SQL_ERROR
                error_message = str(exc.orig)
                error_type = type(exc).__name__
                needs_retry = False
                detail = {
                    "exception": exc,
                    "error_type": error_type,
                    "error_message": error_message,
                }
                new_exc = DatabaseIntegrityError(
                    description=f"Violation of rules or conditions: {error_message}",
                    detail=detail,
                )

            except ConnectionError as exc:
                operation_outcome = OperationOutcome.CACHE_ERROR
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
                operation_outcome = OperationOutcome.CACHE_ERROR
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
                needs_retry = False

            if not needs_retry or delay is None:
                if operation_outcome in [OperationOutcome.CACHE_ERROR, OperationOutcome.SQL_ERROR]:
                    raise new_exc
                return result
            else:
                storage = "database" if operation_outcome == OperationOutcome.SQL_ERROR else "cache"
                logging.warning(f"Unable to connect to {storage} due to {error_type}. Retrying in {delay} seconds...")
                sleep(delay)

    return async_wrapper

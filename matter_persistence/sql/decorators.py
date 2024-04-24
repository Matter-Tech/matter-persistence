import itertools
import logging
from functools import wraps
from time import sleep

from sqlalchemy.exc import IntegrityError, OperationalError

from matter_persistence.sql.exceptions import DatabaseError, DatabaseIntegrityError

logger = logging.getLogger(__name__)


def retry_if_failed(func, delays=(0, 1, 5)):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        for delay in itertools.chain(delays, [None]):
            try:
                result = await func(*args, **kwargs)

            except OperationalError as exc:
                operation_successful = False
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
                operation_successful = False
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

            else:
                operation_successful = True
                needs_retry = False

            if not needs_retry or delay is None:
                if not operation_successful:
                    raise new_exc
                return result
            else:
                logging.warning(f"Unable to connect to database due to {error_type}. Retrying in {delay} seconds...")
                sleep(delay)

    return async_wrapper

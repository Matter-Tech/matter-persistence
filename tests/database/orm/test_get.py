import pytest

from matter_persistence.database import InstanceNotFoundError
from .conftest import BaseOrmModel


@pytest.mark.asyncio
async def test_base_get_raises_not_found_when_pk_doesnt_exist(configure_base_class):
    with pytest.raises(InstanceNotFoundError):
        await BaseOrmModel.get(ident=1)

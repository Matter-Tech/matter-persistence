import pytest

from matter_persistence.database import InstanceNotFoundError, get_or_reuse_session
from .conftest import BaseOrmModel, AnotherOrmModel


@pytest.mark.asyncio
async def test_base_get_raises_not_found_when_pk_doesnt_exist(configure_base_class):
    with pytest.raises(InstanceNotFoundError):
        await BaseOrmModel.get(ident=1)


@pytest.mark.asyncio
async def test_base_get_with_releted_loaded(configure_base_class):
    another = AnotherOrmModel(name="another")
    b = BaseOrmModel(name="a name", anothers_orm=[another])
    await b.save()

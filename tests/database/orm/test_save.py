import pytest

from .conftest import BaseOrmModel


@pytest.mark.asyncio
async def test_base_save_and_retrieve(configure_base_class):
    b = BaseOrmModel(id=1, name="a name")
    await b.save()

    b1 = await BaseOrmModel.get(ident=1)

    assert b1.name == b.name

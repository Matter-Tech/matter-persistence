import pytest

from .conftest import BaseOrmModel

@pytest.mark.asyncio
async def test_count_without_where(configure_base_class):
    b_1 = BaseOrmModel(name="item 1")
    await b_1.save()
    b_2 = BaseOrmModel(name="item 2")
    await b_2.save()

    count = await BaseOrmModel.count()

    assert count == 2


@pytest.mark.asyncio
async def test_count_empty_set(configure_base_class):
    count = await BaseOrmModel.count()

    assert count == 0


@pytest.mark.asyncio
async def test_count_no_result(configure_base_class):

    count = await BaseOrmModel.count(BaseOrmModel.name=="item 1")

    assert count == 0

@pytest.mark.asyncio
async def test_count_filtered(configure_base_class):
    b_1 = BaseOrmModel(name="item 1")
    await b_1.save()
    b_2 = BaseOrmModel(name="item 2")
    await b_2.save()
    count = await BaseOrmModel.count(BaseOrmModel.name=="item 1")

    assert count == 1

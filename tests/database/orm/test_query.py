import pytest

from .conftest import BaseOrmModel


@pytest.mark.asyncio
async def test_query_without_where(configure_base_class):
    b_1 = BaseOrmModel(name="item 1")
    await b_1.save()
    b_2 = BaseOrmModel(name="item 2")
    await b_2.save()

    objs = await BaseOrmModel.query()

    assert len(objs) == 2
    # ordered by id by default
    assert objs[0].id == b_1.id
    assert objs[1].id == b_2.id


@pytest.mark.asyncio
async def test_query_empty_set(configure_base_class):
    objs = await BaseOrmModel.query()

    assert len(objs) == 0


@pytest.mark.asyncio
async def test_query_no_result(configure_base_class):
    objs = await BaseOrmModel.query(BaseOrmModel.name == "item 1")

    assert len(objs) == 0


@pytest.mark.asyncio
async def test_query_filtered(configure_base_class):
    b_1 = BaseOrmModel(name="item 1")
    await b_1.save()
    b_2 = BaseOrmModel(name="item 2")
    await b_2.save()
    objs = await BaseOrmModel.query(BaseOrmModel.name == "item 1")

    assert len(objs) == 1
    assert objs[0].id == b_1.id

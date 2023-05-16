import pytest
import sqlalchemy as sa

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


@pytest.mark.asyncio
async def test_query_grouped_by(configure_base_class):
    b_1 = BaseOrmModel(name="item 1")
    await b_1.save()
    b_2 = BaseOrmModel(name="item 2")
    await b_2.save()
    b_3 = BaseOrmModel(name="item 1")
    await b_3.save()

    objs = await BaseOrmModel.query(
        select=[BaseOrmModel.name, sa.func.count().label("amount")],
        group_by=[BaseOrmModel.name],
        ordered_by=[BaseOrmModel.name],
    )

    assert len(objs) == 2
    assert objs[0] == "item 1"
    assert objs[1] == "item 2"


@pytest.mark.asyncio
async def test_mapped_query_grouped_by(configure_base_class):
    b_1 = BaseOrmModel(name="item 1")
    await b_1.save()
    b_2 = BaseOrmModel(name="item 2")
    await b_2.save()
    b_3 = BaseOrmModel(name="item 1")
    await b_3.save()

    objs = await BaseOrmModel.mapped_query(
        select=[BaseOrmModel.name, sa.func.count().label("amount")],
        group_by=[BaseOrmModel.name],
        ordered_by=[BaseOrmModel.name],
    )

    assert len(objs) == 2
    assert objs[0].name == "item 1"
    assert objs[0].amount == 2

    assert objs[1].name == "item 2"
    assert objs[1].amount == 1


@pytest.mark.asyncio
async def test_mapped_query_grouped_by_with_having(configure_base_class):
    b_1 = BaseOrmModel(name="item 1")
    await b_1.save()
    b_2 = BaseOrmModel(name="item 2")
    await b_2.save()
    b_3 = BaseOrmModel(name="item 1")
    await b_3.save()

    objs = await BaseOrmModel.mapped_query(
        select=[BaseOrmModel.name, sa.func.count().label("amount")],
        group_by=[BaseOrmModel.name],
        ordered_by=[BaseOrmModel.name],
        having=[
            sa.func.count().label("amount") > 1,
        ],
    )

    assert len(objs) == 1
    assert objs[0].name == "item 1"
    assert objs[0].amount == 2


@pytest.mark.asyncio
async def test_query_with_distinct(configure_base_class):
    b_1 = BaseOrmModel(name="item 1")
    await b_1.save()
    b_2 = BaseOrmModel(name="item 2")
    await b_2.save()
    b_3 = BaseOrmModel(name="item 1")
    await b_3.save()

    objs = await BaseOrmModel.query(
        select=[sa.distinct(BaseOrmModel.name)]
    )

    assert len(objs) == 2
    assert objs[0] == "item 1"
    assert objs[1] == "item 2"

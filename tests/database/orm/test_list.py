import pytest

from .conftest import BaseOrmModel


@pytest.mark.asyncio
async def test_list_base_case(configure_base_class):
    b_1 = BaseOrmModel(name="item 1")
    await b_1.save()
    b_2 = BaseOrmModel(name="item 2")
    await b_2.save()

    base_list = await BaseOrmModel.list()

    assert (len(base_list)) == 2

    assert all([type(i) is BaseOrmModel for i in base_list])

    assert base_list[0].id == b_1.id
    assert base_list[1].id == b_2.id


@pytest.mark.asyncio
async def test_list_base_empty_base(configure_base_class):
    base_list = await BaseOrmModel.list()
    assert (len(base_list)) == 0


@pytest.mark.asyncio
async def test_list_base_with_limit(configure_base_class):
    for i in range(10):
        b_1 = BaseOrmModel(name=f"item {i}")
        await b_1.save()

    base_list = await BaseOrmModel.list(limit=1)
    assert (len(base_list)) == 1


@pytest.mark.asyncio
async def test_list_base_with_order(configure_base_class):
    for i in range(10):
        b_1 = BaseOrmModel(name=f"item {i}")
        await b_1.save()

        # just a sanity check to ensure the items is getting the right ids.
        # this simplifies the underlying tests
        assert b_1.id == i + 1

    base_list = await BaseOrmModel.list(ordered_by=[BaseOrmModel.id.desc()])

    assert (len(base_list)) == 10

    assert base_list[0].id == 10
    assert base_list[-1].id == 1


@pytest.mark.asyncio
async def test_list_base_with_where(configure_base_class):
    for i in range(10):
        b_1 = BaseOrmModel(name=f"item {i + 1}")
        await b_1.save()

        # just a sanity check to ensure the items is getting the right ids.
        # this simplifies the underlying tests

        assert b_1.id == i + 1

    base_list = await BaseOrmModel.list(BaseOrmModel.name == "item 6")

    assert (len(base_list)) == 1

    assert base_list[0].id == 6


@pytest.mark.asyncio
async def test_list_multiple_args(configure_base_class):
    for i in range(10):
        b_1 = BaseOrmModel(name=f"item {i + 1}")
        await b_1.save()

        # just a sanity check to ensure the items is getting the right ids.
        # this simplifies the underlying tests

        assert b_1.id == i + 1

    base_list = await BaseOrmModel.list(
        BaseOrmModel.id > 6, BaseOrmModel.id < 10, limit=2, ordered_by=[BaseOrmModel.name.desc()]
    )

    assert (len(base_list)) == 2

    assert base_list[0].id == 9
    assert base_list[1].id == 8

import pytest

from matter_persistence.database import InstanceNotFoundError, InvalidActionError
from .conftest import BaseOrmModel


@pytest.mark.asyncio
async def test_delete_sets_deleted_property_to_true(configure_base_class):
    b = BaseOrmModel(id=1, name="a name")
    assert b.deleted is False
    await b.save()

    await b.delete()
    assert b.deleted is True


@pytest.mark.asyncio
async def test_base_delete(configure_base_class):
    b = BaseOrmModel(id=1, name="a name")
    await b.save()

    await b.delete()

    # ensures the objects has been in fact deleted
    with pytest.raises(InstanceNotFoundError):
        await BaseOrmModel.get(ident=b.id)


@pytest.mark.asyncio
async def test_delete_not_saved_object(configure_base_class):
    b = BaseOrmModel(id=1, name="a name")

    with pytest.raises(InvalidActionError):
        await b.delete()


@pytest.mark.asyncio
async def test_delete_deleted_object(configure_base_class):
    b = BaseOrmModel(id=1, name="a name")
    await b.save()
    await b.delete()

    with pytest.raises(InvalidActionError):
        await b.delete()

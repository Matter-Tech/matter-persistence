import asyncio

import pytest

from matter_persistence.redis.exceptions import CacheRecordNotFoundError
from tests.redis.conftest import INTERNAL_ID, ORGANISATION_ID, TestDTO


async def test_cache_manager_is_alive(cache_manager):
    assert await cache_manager.is_cache_alive()


async def test_cache_manager_save_and_get(cache_manager, test_dto):
    await cache_manager.save_value(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO)
    res = await cache_manager.get_value(ORGANISATION_ID, INTERNAL_ID, TestDTO)
    assert res.value["test_field"] == test_dto.test_field


async def test_cache_manager_save_and_get_without_object_class(cache_manager, test_dto):
    await cache_manager.save_value(ORGANISATION_ID, INTERNAL_ID, test_dto)
    res = await cache_manager.get_value(ORGANISATION_ID, INTERNAL_ID)
    assert res.value["test_field"] == test_dto.test_field


async def test_cache_manager_save_and_get_with_expiration_success(cache_manager, test_dto):
    await cache_manager.save_value(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO)
    await asyncio.sleep(0.5)
    res = await cache_manager.get_value(ORGANISATION_ID, INTERNAL_ID, TestDTO)
    assert res.value["test_field"] == test_dto.test_field


async def test_cache_manager_save_and_get_with_expiration_expired(cache_manager, test_dto):
    await cache_manager.save_value(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO, 1)
    await asyncio.sleep(1.1)
    with pytest.raises(CacheRecordNotFoundError):
        await cache_manager.get_value(ORGANISATION_ID, INTERNAL_ID, TestDTO)


async def test_cache_manager_delete_value(cache_manager, test_dto):
    await cache_manager.save_value(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO)
    await cache_manager.delete_value(ORGANISATION_ID, INTERNAL_ID, TestDTO)
    with pytest.raises(CacheRecordNotFoundError):
        await cache_manager.get_value(ORGANISATION_ID, INTERNAL_ID, TestDTO)


async def test_cache_manager_cache_record_exists_success(cache_manager, test_dto):
    await cache_manager.save_value(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO)
    assert await cache_manager.cache_record_exists(ORGANISATION_ID, INTERNAL_ID, TestDTO) == 1


async def test_cache_manager_cache_record_exists_unsuccess(cache_manager, test_dto):
    await cache_manager.save_value(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO)
    await cache_manager.delete_value(ORGANISATION_ID, INTERNAL_ID, TestDTO)
    assert await cache_manager.cache_record_exists(ORGANISATION_ID, INTERNAL_ID, TestDTO) == 0


# async def test_cache_manager_close_connection_pool(cache_manager):
#   await cache_manager.close_connection_pool()
#    assert True  # basically check if method executes without error

import asyncio

import pytest
from pydantic import BaseModel

from matter_persistence.redis.exceptions import CacheRecordNotFoundError
from matter_persistence.redis.manager import CacheManager
from tests.redis.conftest import INTERNAL_ID, ORGANISATION_ID, TestDTO


async def test_cache_manager_is_alive(cache_manager):
    assert await cache_manager.is_cache_alive()


async def test_cache_manager_save_and_get(cache_manager, test_dto):
    await cache_manager.save_value(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO)
    res = await cache_manager.get_value(ORGANISATION_ID, INTERNAL_ID, TestDTO)
    assert res.value.test_field == test_dto.test_field


async def test_cache_manager_save_and_get_without_object_class(cache_manager, test_dto):
    await cache_manager.save_value(ORGANISATION_ID, INTERNAL_ID, test_dto)
    res = await cache_manager.get_value(ORGANISATION_ID, INTERNAL_ID)
    assert res.value.test_field == test_dto.test_field


async def test_cache_manager_save_and_get_with_expiration_success(cache_manager, test_dto):
    await cache_manager.save_value(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO)
    await asyncio.sleep(0.5)
    res = await cache_manager.get_value(ORGANISATION_ID, INTERNAL_ID, TestDTO)
    assert res.value.test_field == test_dto.test_field


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


async def test_cache_manager_close_connection_pool(cache_manager):
    await cache_manager.close_connection_pool()
    assert True  # basically check if method executes without error


async def test_cache_manager_incorrect_argument_combination():
    with pytest.raises(ValueError):
        _ = CacheManager()


async def test_cache_manager_save_with_key_and_get_with_key_success(cache_manager, test_dto):
    await cache_manager.save_with_key("key", test_dto, TestDTO)
    assert await cache_manager.get_with_key("key", TestDTO)


async def test_cache_manager_save_and_get_many_objects_with_keys_success(cache_manager: CacheManager) -> None:
    test_dtos = {f"key_{i}": TestDTO(test_field=i) for i in range(10)}
    await cache_manager.save_many_with_keys(test_dtos, TestDTO, 100)
    response = await cache_manager.get_many_with_keys(list(test_dtos.keys()), TestDTO)
    assert response == test_dtos


async def test_cache_manager_save_and_get_many_raw_values_with_keys_success(cache_manager: CacheManager) -> None:
    test_input = {f"key_{i}": f"test_value_{i}" for i in range(10)}
    await cache_manager.save_many_with_keys(test_input, None, 100)
    response: dict[str, bytes | list[bytes] | BaseModel | list[BaseModel]] = await cache_manager.get_many_with_keys(
        list(test_input.keys()), None
    )
    for key, value in response.items():
        assert isinstance(value, bytes)
        assert test_input[key] == value.decode()


async def test_cache_manager_get_many_returns_none_for_missing_keys(
    cache_manager: CacheManager, test_dto: TestDTO
) -> None:
    await cache_manager.save_with_key("key", test_dto, TestDTO)
    response = await cache_manager.get_many_with_keys(("key", "key2", "key3"), TestDTO)
    assert len(response.keys()) == 3
    assert response["key"] == test_dto
    assert response["key2"] is None
    assert response["key3"] is None


async def test_cache_manager_save_with_key_and_get_with_key_expired(cache_manager, test_dto):
    await cache_manager.save_with_key("key", test_dto, TestDTO, 1)
    await asyncio.sleep(1.05)
    with pytest.raises(CacheRecordNotFoundError):
        await cache_manager.get_with_key("key", TestDTO)


async def test_cache_manager_cache_record_with_key_exists(cache_manager, test_dto):
    await cache_manager.save_with_key("key", test_dto, TestDTO)
    assert await cache_manager.cache_record_with_key_exists("key", TestDTO)


async def test_cache_manager_delete_with_key(cache_manager):
    await cache_manager.save_with_key("key", "value")
    await cache_manager.delete_with_key("key")
    with pytest.raises(CacheRecordNotFoundError):
        await cache_manager.get_with_key("key")


async def test_cache_manager_set_many_with_sentinel(cache_manager_with_sentinel: CacheManager) -> None:
    await cache_manager_with_sentinel.save_with_key("test", "some_value")
    assert (await cache_manager_with_sentinel.get_with_key("test")).decode() == "some_value"

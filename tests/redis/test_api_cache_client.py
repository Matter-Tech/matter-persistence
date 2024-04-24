import asyncio

import pytest

from matter_persistence.redis.exceptions import CacheRecordNotFoundError
from tests.redis.conftest import INTERNAL_ID, ORGANISATION_ID, TestDTO


async def test_api_cache_client_is_alive(api_cache_client):
    assert await api_cache_client.is_cache_alive()


async def test_api_cache_client_save_and_find_raw(api_cache_client, test_dto):
    await api_cache_client.save_raw("test_key", test_dto, TestDTO)
    res = await api_cache_client.find_raw("test_key", TestDTO)
    assert res == test_dto


async def test_api_cache_client_save_and_find_raw_with_expiration_success(api_cache_client, test_dto):
    await api_cache_client.save_raw("test_key", test_dto, TestDTO, 15)
    await asyncio.sleep(0.5)
    res = await api_cache_client.find_raw("test_key", TestDTO)
    assert res == test_dto


async def test_api_cache_client_save_and_find_raw_will_expire(api_cache_client, test_dto):
    await api_cache_client.save_raw("test_key", test_dto, TestDTO, 1)
    await asyncio.sleep(1.1)
    with pytest.raises(CacheRecordNotFoundError):
        await api_cache_client.find_raw("test_key", TestDTO)


async def test_api_cache_client_delete_raw(api_cache_client, test_dto):
    await api_cache_client.save_raw("test_key", test_dto, TestDTO)
    await api_cache_client.delete_raw("test_key", TestDTO)
    with pytest.raises(CacheRecordNotFoundError):
        await api_cache_client.find_raw("test_key", TestDTO)


async def test_api_cache_client_raw_cache_record_exists(api_cache_client, test_dto):
    await api_cache_client.save_raw("test_key", test_dto, TestDTO)
    assert await api_cache_client.raw_cache_record_exists("test_key", TestDTO)


async def test_api_cache_client_save_object(api_cache_client, test_dto):
    await api_cache_client.save_object(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO)
    assert await api_cache_client.cache_record_exists(ORGANISATION_ID, INTERNAL_ID, TestDTO)


async def test_api_cache_client_save_object_will_expire(api_cache_client, test_dto):
    await api_cache_client.save_object(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO, 1)
    await asyncio.sleep(1.1)
    assert not await api_cache_client.cache_record_exists(ORGANISATION_ID, INTERNAL_ID, TestDTO)


async def test_api_cache_client_find_object(api_cache_client, test_dto):
    await api_cache_client.save_object(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO)
    res = await api_cache_client.find_object(ORGANISATION_ID, INTERNAL_ID, TestDTO)
    assert res.value.test_field == test_dto.test_field


async def test_api_cache_client_save_cache_record(api_cache_client, test_dto):
    await api_cache_client.save_cache_record(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO)
    res = await api_cache_client.find_cache_record(ORGANISATION_ID, INTERNAL_ID, TestDTO)
    assert res.value.test_field == test_dto.test_field


async def test_api_cache_client_save_cache_record_will_expire(api_cache_client, test_dto):
    await api_cache_client.save_cache_record(ORGANISATION_ID, INTERNAL_ID, test_dto, TestDTO, 1)
    await asyncio.sleep(1.1)
    with pytest.raises(CacheRecordNotFoundError):
        await api_cache_client.find_cache_record(ORGANISATION_ID, INTERNAL_ID, TestDTO)


async def test_api_cache_client_close_connection_pool(api_cache_client):
    await api_cache_client.close_connection_pool()
    assert True  # basically check if method executes without error

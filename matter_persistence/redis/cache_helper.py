from datetime import UTC, datetime, timedelta
from hashlib import sha1
from typing import Any
from uuid import UUID

from .models import CacheRecordModel


class CacheHelper:
    @classmethod
    def create_cache_record(
        cls,
        organization_id: UUID,
        internal_id: str,
        value: Any,
        object_class: object | None = None,
        expiration_in_seconds: int | None = None,
    ) -> CacheRecordModel:
        hash_key = cls.create_hash_key(
            organization_id=organization_id,
            internal_id=internal_id,
            object_class=object_class,
        )

        return CacheRecordModel(
            internal_id=internal_id,
            hash_key=hash_key,
            organization_id=organization_id,
            value=value,
            expiration=None
            if not expiration_in_seconds
            else (datetime.now(tz=UTC) + timedelta(seconds=expiration_in_seconds)),
        )

    @classmethod
    def create_hash_key(cls, organization_id: UUID, internal_id: str, object_class: object | None = None) -> str:
        key = cls.__get_object_hashkey(internal_id)
        if object_class:
            key = f"{organization_id}_{object_class.__name__}_{key}"
        else:
            key = f"{organization_id}_{key}"

        return key

    @classmethod
    def create_basic_hash_key(cls, key: str, key_type: str | None = None) -> str:
        key = cls.__get_object_hashkey(key)
        if key_type:
            key = f"{key_type}_{key}"

        return key

    @classmethod
    def __get_object_hashkey(cls, key) -> str:
        """
        Generates a Redis key according to the object's Id
        :param id: the object's Id (string)
        :return: Redis key (string)
        """

        return sha1(str(key).encode("UTF-8", errors="ignore")).hexdigest()

from datetime import datetime, timedelta, timezone
from hashlib import sha1
from uuid import UUID

from matter_persistence.redis.base import CacheRecordModel, Model


class CacheHelper:
    @classmethod
    def create_cache_record(
        cls,
        organization_id: UUID,
        internal_id: str,
        value: type[Model],
        object_class: type[Model] | None = None,
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
            # due to supporting py3.10, "from datetime import UTC" cannot be used
            else (datetime.now(tz=timezone.utc) + timedelta(seconds=expiration_in_seconds)),  # noqa: UP017
        )

    @classmethod
    def create_hash_key(cls, organization_id: UUID, internal_id: str, object_class: type[Model] | None = None) -> str:
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

from datetime import UTC, datetime

from tests.sql.conftest import one_min_difference_in_secs


def test_base_db_model_init_fields(test_base_db_model):
    test_base_db_model.init_fields()
    assert test_base_db_model.created_at is not None
    assert test_base_db_model.created_at_timestamp is not None


def test_base_db_model_assign(test_base_db_model, test_foundation_model):
    test_base_db_model.assign(test_foundation_model)
    assert test_base_db_model.test_field == test_foundation_model.test_field


def test_base_db_model_assign_with_update(test_base_db_model, test_foundation_model):
    test_base_db_model.assign(test_foundation_model, update=True)
    assert test_base_db_model.updated_at is not None


def test_base_db_model_soft_delete(test_base_db_model):
    test_base_db_model.soft_delete()
    assert test_base_db_model.deleted_at is not None


def test_base_db_model_parse_dict(test_base_db_model, test_other_foundation_model):
    parsed_obj = test_base_db_model.parse_dict(test_other_foundation_model.model_dump())
    assert parsed_obj.test_field == test_other_foundation_model.test_field


def test_base_db_model_parse_obj(test_base_db_model, test_other_foundation_model):
    parsed_obj = test_base_db_model.parse_obj(test_other_foundation_model)
    assert parsed_obj.test_field == test_other_foundation_model.test_field


def test_base_db_model_set_update(test_base_db_model):
    test_base_db_model.set_update()
    assert (datetime.now(tz=UTC) - test_base_db_model.updated_at).seconds < one_min_difference_in_secs


def test_base_db_model_set_delete(test_base_db_model):
    test_base_db_model.set_delete()
    assert (datetime.now(tz=UTC) - test_base_db_model.deleted_at).seconds < one_min_difference_in_secs

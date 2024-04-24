from tests.sql.conftest import test_base_db_model  # noqa


def test_foundation_model_fields_are_correct(test_foundation_model):
    assert test_foundation_model.test_field == 1
    assert test_foundation_model.created_at is not None
    assert test_foundation_model.created_at_timestamp is not None


def test_foundation_model_parse_obj_list(test_foundation_model):
    parsed_obj = test_foundation_model.parse_obj([test_foundation_model])
    assert parsed_obj == [test_foundation_model]


def test_foundation_model_parse_obj_dict(test_foundation_model):
    parsed_obj = test_foundation_model.parse_obj(test_foundation_model.model_dump())
    assert parsed_obj == test_foundation_model


def test_foundation_model_parse_obj_basemodel(test_foundation_model):
    parsed_obj = test_foundation_model.parse_obj(test_foundation_model)
    assert parsed_obj == test_foundation_model


def test_foundation_model_parse_obj_basedbmodel(test_foundation_model, test_base_db_model):
    parsed_obj = test_foundation_model.parse_obj(test_base_db_model)
    assert parsed_obj == test_foundation_model


def test_foundation_model_assign(test_foundation_model, test_other_foundation_model):
    test_foundation_model.assign(test_other_foundation_model)
    assert test_foundation_model.test_field == 2

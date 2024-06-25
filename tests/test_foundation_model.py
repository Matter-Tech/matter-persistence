from tests.conftest import Person, PersonClass, PersonORM, PersonWithAge


def test_foundation_model_created_at_fields(person_dto):
    assert person_dto.created_at
    assert person_dto.created_at_timestamp


def test_foundation_model_from_dict(person_dto):
    person = Person.parse_obj({"name": "john"})
    assert person.name == person_dto.name


def test_foundation_model_from_pydantic(person_dto):
    person = Person.parse_obj(PersonWithAge(name="john", age=30))
    assert person.name == person_dto.name


def test_foundation_model_from_custom_base(person_dto):
    person = Person.parse_obj(PersonORM(name="john"))
    assert person.name == person_dto.name


def test_foundation_model_from_list(person_dto):
    persons = Person.parse_obj([Person(name="john"), Person(name="jane")])
    assert persons[0].name == person_dto.name
    assert len(persons) == 2


def test_foundation_model_from_python_class(person_dto):
    person = Person.parse_obj(PersonClass(name="john"))
    assert person.name == person_dto.name

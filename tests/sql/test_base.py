from tests.conftest import Person, PersonORM


def test_person_orm_from_pydantic(person_dto):
    person = PersonORM.parse_obj(Person(name="john"))
    assert person.name == person_dto.name

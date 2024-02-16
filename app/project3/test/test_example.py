import pytest


class Student:
    def __init__(self, first_name, last_name: str, major: str, year: int) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.year = year


@pytest.fixture
def default_employee():
    return Student("Jhon", "Doe", "Computer Science", 3)


def test_person_initialization(default_employee):
    assert default_employee.first_name == "Jhon", "Always should be Jhon"
    assert default_employee.last_name == "Doe"
    assert default_employee.major == "Computer Science"
    assert default_employee.year == 3

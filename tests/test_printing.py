from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from uv_build_pmt.utils.printing import print_model_tree

if TYPE_CHECKING:
    import pytest


def test_print_model_tree(capsys: pytest.CaptureFixture[str]):
    class TestModel(BaseModel):
        name: str
        age: int

    model = TestModel(name="Alice", age=30)
    print_model_tree(model)

    captured = capsys.readouterr()
    assert "TestModel" in captured.out
    assert "name: str" in captured.out
    assert "age: int" in captured.out


def test_nested_model_tree(capsys: pytest.CaptureFixture[str]):
    class Address(BaseModel):
        street: str
        city: str

    class Person(BaseModel):
        name: str
        address: Address
        hobbies: list[str]

    person = Person(
        name="Bob",
        address=Address(street="1234 Elm St", city="Metropolis"),
        hobbies=["reading", "chess"],
    )
    print_model_tree(person)

    captured = capsys.readouterr()
    assert "Person" in captured.out
    assert "address" in captured.out
    assert "street: str" in captured.out
    assert "city: str" in captured.out
    assert "hobbies: list" in captured.out
    assert "[0]: str" in captured.out


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])

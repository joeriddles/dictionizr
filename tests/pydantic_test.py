from __future__ import annotations
from typing import Optional

from pydantic import BaseModel

import dictionizr
from .utils import eq

class PydanticTestModel(BaseModel):
    id: str
    age: Optional[int]


class ParentPydanticTestModel(BaseModel):
    child: PydanticTestModel
    optional_child: Optional[PydanticTestModel]


def test__pydantic_model__dictionize__works():
    data = PydanticTestModel(id="id", age=4)
    actual = dictionizr.dictionize(data)
    expected = { 'id': 'id', 'age': 4 }
    assert eq(expected, data)


def test__pydantic_model__dictionize__no_optional_value():
    data = PydanticTestModel(id="id")
    actual = dictionizr.dictionize(data)
    expected = { 'id': 'id' }
    assert eq(expected, data)


def test__pydantic_model__undictionize__works():
    data = { 'id': 'id', 'age': 4 }
    actual = dictionizr.undictionize(data, PydanticTestModel)
    expected = PydanticTestModel(id="id", age=4)
    assert eq(expected, actual)


def test__pydantic_model__undictionize__no_optional_value():
    data = { 'id': 'id' }
    actual = dictionizr.undictionize(data, PydanticTestModel)
    expected = PydanticTestModel(id="id")
    assert eq(expected, actual)


def test__pydantic_parent_model__undictionize__works():
    data = { "child": { "id": "id" } }
    actual = dictionizr.undictionize(data, ParentPydanticTestModel)
    expected_child = PydanticTestModel(id="id")
    expected = ParentPydanticTestModel(child=expected_child)
    assert eq(expected, actual)

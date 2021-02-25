from __future__ import annotations
from typing import Optional

from dictionizr import dictionize, undictionize

from .utils import eq


class Data():
    name: str
    sub_name: Optional[Data] = None
    data: Optional[Data] = None
    optional: Optional[str] = None
    datas: Optional[list[Data]] = None
    def __init__(self,
        name: str,
        sub_name: Optional[str] = None,
        data: Optional[Data] = None,
        datas: Optional[list[Data]] = None,
    ):
        self.name = name
        if sub_name is not None:
            self.sub_name = Data(sub_name)
        if data is not None:
            self.data = data
        if datas is not None:
            self.datas = datas

    def __eq__(self, o: Data) -> bool:
        return eq(self, o)

    def hello(self) -> str:
        return f'hello {self.name}'


def test__dictionize__property():
    data = Data('Joe')
    actual = dictionize(data)
    expected = { 'name': 'Joe' }
    assert expected == actual


def test__dictionize__no_functions():
    data = Data('Joe')
    actual = dictionize(data)
    expected = { 'name': 'Joe' }
    assert expected == actual


def test__dictionize__sub_objects():
    data = Data('Joe', data=Data('John'))
    actual = dictionize(data)
    expected = {
        'name': 'Joe',
        'data': { 'name': 'John'}
    }
    assert expected == actual


def test__undictionize__object():
    data = { 'name': 'Joe' }
    actual = undictionize(data, Data)
    expected = Data('Joe')
    assert expected == actual


def test__undictionize__sub_object():
    data = {
        'name': 'Joe',
        'data': { 'name': 'John'}
    }
    actual = undictionize(data, Data)
    expected = Data('Joe', data=Data('John'))
    assert expected == actual


def test__dictionize__array_of_sub_object():
    data = Data(
        'Joe',
        datas=[
            Data('John'),
            Data('Jesse')
        ]
    )
    actual = dictionize(data)
    expected = {
        'name': 'Joe',
        'datas': [
            { 'name': 'John' },
            { 'name': 'Jesse' }
        ]
    }
    assert expected == actual


def test__undictionize__array_of_sub_ojects():
    data = {
        'name': 'Joe',
        'datas': [
            { 'name': 'John' },
            { 'name': 'Jesse' }
        ]
    }
    actual = undictionize(data, Data)
    expected = Data(
        'Joe',
        datas=[
            Data('John'),
            Data('Jesse')
        ]
    )
    assert expected == actual


def test__undictionize__object_method_works():
    data = {
        'name': 'Joe',
    }
    actual_obj = undictionize(data, Data)
    actual = actual_obj.hello()
    expected = 'hello Joe'
    assert expected == actual


def test__undictionize__sub_object_method_works():
    data = {
        'name': 'Joe',
        'data': { 'name': 'John'}
    }
    actual_obj = undictionize(data, Data, module_path='tests.dictionizr_test')
    actual = actual_obj.data.hello()
    expected = 'hello John'
    assert expected == actual

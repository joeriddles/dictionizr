# Dictionizr

[![PyPI version](https://badge.fury.io/py/dictionizr.svg)](https://badge.fury.io/py/dictionizr)

This project was created because I kept creating the methods `to_dict()` and `from_dict()` on many of my python classes and I knew there must be a way to adhere to the DRY principal.

## Installation
`> pip install dictionizr`

## Usage

### `dictionize` basic object
```python
from dictionizr import dictionize


class Data():
    def __init__(self, name: str) -> None:
        self.name = name


data = Data('Joe')
output = dictionize(data)
print(output)
```
```
> {'name': 'Joe'}
```

### `dictionize` complex object
```python
from __future__ import annotations
from typing import Optional

from dictionizr import dictionize


class Data():
    def __init__(self, name: str, other_data: Optional[Data] = None) -> None:
        self.name = name
        self.other_data = other_data


data = Data('Joe')
new_data = Data('John', data)
output = dictionize(new_data)
print(output)
```
```
> {'name': 'Joe', 'other_data': {'name': 'John'}}
```

### `undictionize` simple object
```python
from dictionizr import undictionize


class Data():
    def __init__(self, name: str) -> None:
        self.name = name


dictionary = {'name': 'Joe'}
data: Data = undictionize(dictionary)
print(data.name)
```
```
> Joe
```

### `undictionize` complex object
```python
from __future__ import annotations
from typing import Optional

from dictionizr import undictionize


class Data():
    def __init__(self, name: str, other_data: Optional[Data] = None) -> None:
        self.name = name
        self.other_data = other_data


dictionary = {
    'name': 'Joe',
    'other_data': {
        'name': 'John'
    }
}
data: Data = undictionize(dictionary)
print(data.name)
print(data.other_data.name)
```
```
> Joe
> John
```

## Links
[PyPi](https://pypi.org/project/dictionizr/)

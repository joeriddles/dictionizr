from __future__ import annotations
import inspect
from typing import Optional, Type
from types import SimpleNamespace

def dictionize(data) -> dict:
    if data is None:
        return {}

    try:
        output = vars(data)
    except TypeError:
        output = {}
        for slot in data.__slots__:
            try:
                output[slot] = getattr(data, slot)
            except AttributeError:
                pass

    for key, value in output.items():
        if hasattr(value, '__dict__'):
            output[key] = dictionize(value)

    output = {
        key: value
        for key, value
        in output.items()
        if value is not None
    }
    return output


def undictionize(data: dict, class_: Optional[Type] = None):
    data = data.copy()
    if data is None:
        return None

    if class_ is None:
        obj = SimpleNamespace()
    else:
        obj = class_.__new__(class_)

    for key, value in data.items():
        if isinstance(value, dict):
            value = undictionize(value)
        setattr(obj, key, value)

    if class_ is not None and hasattr(class_.__init__, '__code__'):
        init_signature = inspect.signature(class_.__init__)
        init_parameters = init_signature.parameters
        init_args = []
        for param in init_parameters.values():
            if param.name == 'self':
                continue

            if param.kind == param.POSITIONAL_ONLY:
                value = data.pop(param.name, param.default)
                init_args.append(value)

            if param.name == 'args':
                pass
            elif param.name == 'kwargs':
                pass
            elif param.name in data:
                value = data.pop(param.name)
                init_args.append(value)

        obj.__init__(*init_args)
    return obj

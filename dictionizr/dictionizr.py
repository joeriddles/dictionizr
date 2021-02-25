from __future__ import annotations
import inspect
from typing import List, Optional, Set, Tuple, Type, Union
from types import SimpleNamespace

Iterables = Union[List, Set, Tuple]

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
        elif isinstance(value, dict):
            new_value = {}
            for sub_key, sub_value in value.items():
                if hasattr(sub_value, '__dict__'):
                    sub_value = dictionize(sub_value)
                new_value[sub_key] = sub_value
            output[key] = new_value
        elif not isinstance(value, str):
            try:
                for sub_value in value:
                    # we break to keep only the logic we're checking for a TypeError in the current scope
                    # `else` will handle the logic if the `value` is iterable
                    break
            except TypeError:
                pass
            else:
                new_value = []
                for sub_value in value:
                    if hasattr(sub_value, '__dict__'):
                        sub_value = dictionize(sub_value)
                        new_value.append(sub_value)
                    else:
                        new_value.append(sub_value)
                    output[key] = new_value

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
        positional_args = []
        keyword_args = {}
        for param in init_parameters.values():
            if param.name == 'self':
                continue

            # See: https://docs.python.org/3/library/inspect.html#inspect.Parameter.kind
            if param.kind == param.POSITIONAL_OR_KEYWORD or param.kind == param.POSITIONAL_ONLY:
                value = data.pop(param.name, param.default)
                positional_args.append(value)
            elif param.kind == param.KEYWORD_ONLY:
                value = data.pop(param.name, param.default)
                keyword_args[param.name] = value
            elif param.kind == param.VAR_POSITIONAL: # args
                if 'args' in data and isinstance(data['args'], list):
                    positional_args.extend(data['args'])
            elif param.kind == param.VAR_KEYWORD: # kwargs
                if 'kwargs' in data and isinstance(data['kwargs'], dict):
                    keyword_args.update(**data['kwargs'])

        obj.__init__(*positional_args, **keyword_args)

    return obj

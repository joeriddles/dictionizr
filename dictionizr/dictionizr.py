from __future__ import annotations
import inspect
from typing import Any, List, Optional, Set, Tuple, Type, Union
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


def undictionize(data: dict, class_: Optional[Type] = None) -> Any:
    data = data.copy()
    if data is None:
        return None

    if class_ is None:
        obj = SimpleNamespace()
    else:
        obj = class_.__new__(class_)

    if class_ is not None and hasattr(class_.__init__, '__code__'):
        init_signature = inspect.signature(class_.__init__)
        init_parameters = init_signature.parameters
        positional_args = []
        keyword_args = {}
        for param in init_parameters.values():
            name = param.name
            if name == 'self' or name.startswith('__'):
                continue

            value = data.pop(name, None)
            if param.kind == param.POSITIONAL_OR_KEYWORD or param.kind == param.POSITIONAL_ONLY:
                positional_args.append(value)
            elif param.kind == param.KEYWORD_ONLY:
                keyword_args[name] = value
            elif param.kind == param.VAR_POSITIONAL:
                if value is not None:
                    positional_args.extend(value)
            elif param.kind == param.VAR_KEYWORD:
                if value is not None:
                    keyword_args.update(**value)

        for key, value in data.items():
            if isinstance(value, dict):
                value = undictionize(value)
            keyword_args[key] = value

        try:
            obj.__init__(*positional_args, **keyword_args)
        except:
            keys = list(data.keys())
            while keys:
                key = keys.pop()
                keyword_args.pop(key)
                try:
                    obj.__init__(*positional_args, **keyword_args)
                except:
                    pass
                else:
                    break

    for key, value in data.items():
        if not hasattr(obj, key):    
            if isinstance(value, dict):
                value = undictionize(value)
        try:
            setattr(obj, key, value)
        except:
            pass

    return obj

from __future__ import annotations
from importlib import import_module
import inspect
import re
from typing import Optional, Type
from types import SimpleNamespace


def _find_class_by_name(class_name: str, module_path: Optional[str]):
    value_class = None
    match = re.search('.*\[(\w+)\].*', class_name)
    if match:
        class_name = match.groups()[0]
    try:
        module_ = import_module(module_path)
    except Exception:
        pass
    else:
        module_members = [
            (name, member)
            for name, member
            in inspect.getmembers(module_)
        ]
        module_classes = [
            (name, member)
            for name, member
            in module_members
            if inspect.isclass(member)
        ]
        value_module_classes = [
            member
            for name, member
            in module_classes
            if name == class_name
        ]
        if len(value_module_classes) > 0:
            value_class = value_module_classes[0]

    return value_class


def dictionize(data, omit_none_values: bool=True) -> dict:
    """
    Recursively converts obects to dictionaries.
    Omits values that have `None` by default. This can be overriden by passing `False` to `omit_none_values`
    """
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

    if omit_none_values:
        output = {
            key: value
            for key, value
            in output.items()
            if value is not None
        }
    return output


def undictionize(data: dict, class_: Optional[Type] = None, module_path: Optional[str] = None):
    """
    Attempts to create an object of type `class_` and recursively fill in properties.
    If the function can determine the type hint for a property on the created object, it will
    attempt to locate that class and set the property to an object of that class. Otherwise,
    `types.SimpleNamespace` will be used for complex properties. Passing `module_path` will
    help locate the module that contains the class(es). `module_path` can be omitted if `class_`
    has no properties that are other custom types, or if you do not need to use any methods on
    the properties of custom types.
    """
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

            if param.annotation is not inspect.Signature.empty:
                param_class = _find_class_by_name(param.annotation, module_path)
                if param_class is not None:
                    param_value = data.get(param.name, None)
                    if param_value is not None:
                        new_param_value = undictionize(param_value, param_class)
                        data[param.name] = new_param_value

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


def eq(a, b) -> bool:
    if a is None and b is None:
        return True
    elif a is None or b is None:
        return False

    a_can_vars, a_vars = can_vars(a)
    b_can_vars, b_vars = can_vars(b)
    if a_can_vars and b_can_vars:
        if len(a_vars) != len(b_vars):
            return False

        for a_key, a_value in a_vars.items():
            b_value = b_vars[a_key]
            if not eq(a_value, b_value):
                return False
        return True
    elif a_can_vars != b_can_vars:
        if isinstance(b, dict):
            a, b = b, a
        if isinstance(a, dict):
            for a_key, a_value in a.items():
                try:
                    b_value = getattr(b, a_key)
                    if not eq(a_value, b_value):
                        return False
                except AttributeError:
                    return False
            return True
    else:
        if isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                return False
            try:
                a = sorted(a)
                b = sorted(b)
            except ValueError:
                pass
            finally:
                for index, a_value in enumerate(a):
                    b_value = b[index]
                    if not eq(a_value, b_value):
                        return False
                return True

    # if all else fails...
    return a == b


def can_vars(obj) -> bool:
    try:
        obj_vars = vars(obj)
    except TypeError:
        return False, None
    else:
        return True, obj_vars

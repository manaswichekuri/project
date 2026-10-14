class BadRequest(ValueError):
    pass


def parse_int(value, name, default, minimum=None, maximum=None):
    """Parses an int query/body value, raising BadRequest on garbage and clamping to bounds."""
    if value is None or value == '':
        return default
    try:
        result = int(value)
    except (TypeError, ValueError):
        raise BadRequest(f"'{name}' must be an integer")
    if minimum is not None:
        result = max(minimum, result)
    if maximum is not None:
        result = min(maximum, result)
    return result

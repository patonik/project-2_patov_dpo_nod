import shlex

from .core import validate_value


def parse_values(type_values: list[tuple]):
    """
    Parse values ('val1', 28, true) -> list of str vals.
    """
    parsed_vals = []
    try:
        for typ, val in type_values:
            parsed_vals.append(validate_value(val, typ))
        return parsed_vals
    except ValueError:
        raise ValueError("Ошибка парсинга values.")


def parse_where(where_str, table_meta):
    """
    Parse where: col = val -> {'col': converted_val}
    """
    # Assume simple 'col = val', no AND/OR for now
    if not where_str:
        return {}
    parts = shlex.split(where_str)
    if len(parts) != 3 or parts[1] != '=':
        raise ValueError("Формат where: столбец = значение")
    col = parts[0].lower()
    val = parts[2].strip("'\"")  # Strip quotes
    return {col: validate_value(val, table_meta[col])}  # Conversion in core validate


def parse_set(set_str, table_meta):
    """
    Parse set: col = new_val -> {'col': new_val}
    """
    # Similar to where
    parts = shlex.split(set_str)
    if len(parts) != 3 or parts[1] != '=':
        raise ValueError("Формат set: столбец = значение")
    col = parts[0].lower()
    val = parts[2].strip("'\"")
    return {col: validate_value(val, table_meta[col])}

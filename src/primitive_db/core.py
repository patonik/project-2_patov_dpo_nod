VALID_TYPES = {'int', 'str', 'bool'}  # Supported types


def create_table(metadata, table_name, columns):
    """
    Create a new table in metadata. Auto-add ID:int.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata
    column_dict = {}
    for col in columns:
        if ':' not in col:
            print(f'Некорректное значение: "{col}". Формат: столбец:тип.')
            return metadata
        name, typ = col.split(':', 1)
        typ = typ
        if typ not in VALID_TYPES:
            print(
                f'Ошибка: Неподдерживаемый тип "{typ}". '
                f'Доступны: {", ".join(VALID_TYPES)}.')
            return metadata
        column_dict[name] = typ

    # Auto-add ID:int
    full_columns = {'id': 'int', **column_dict}
    metadata[table_name] = full_columns
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        f'{", ".join([f"{k}:{v}" for k, v in full_columns.items()])}')
    return metadata


def drop_table(metadata, table_name):
    """
    Drop a table from metadata.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """
    List all tables.
    """
    if not metadata:
        print('Нет таблиц.')
        return
    for table in metadata:
        print(f'- {table}')


def validate_value(value, typ):
    """
    Validate and convert value to type.
    """
    try:
        if typ == 'int':
            return int(value)
        elif typ == 'str':
            return str(value)
        elif typ == 'bool':
            return value.lower() in ['true', '1', 'yes', 'y']
    except ValueError:
        raise ValueError(f"Invalid value '{value}' for type '{typ}'")


def insert(user_columns, values, data):
    """
    Insert new record. Returns updated data.
    """
    record = {'id': data[-1]['id'] + 1 if len(data) > 0 else 1}
    for col, val in zip(user_columns, values):
        record[col] = val

    data.append(record)
    return data


def select(data, where_clause=None):
    """
    Select records. Returns filtered list.
    """
    if where_clause is None:
        return data

    filtered = []
    for record in data:
        match = True
        for col, val in where_clause.items():
            if record.get(col) != val:  # Simple equality
                match = False
                break
        if match:
            filtered.append(record)
    return filtered


def update(data, set_clause, where_clause):
    """
    Update records. Returns updated data.
    """
    for record in data:
        match = True
        for col, val in where_clause.items():
            if record.get(col) != val:
                match = False
                break
        if match:
            for col, new_val in set_clause.items():
                if col in record:
                    record[col] = new_val  # Assume type validated upstream
    return data


def delete(data, where_clause):
    """
    Delete records. Returns updated data.
    """
    new_data = []
    for record in data:
        match = True
        for col, val in where_clause.items():
            if record.get(col) != val:
                match = False
                break
        if not match:
            new_data.append(record)
    return new_data


def get_table_info(metadata, table_name, data):
    """
    Get table info.
    """
    columns = metadata[table_name]
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {', '.join([f'{k}:{v}' for k, v in columns.items()])}")
    print(f"Количество записей: {len(data)}")

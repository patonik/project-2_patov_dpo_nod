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
        if typ not in VALID_TYPES:
            print(
                f'Ошибка: Неподдерживаемый тип "{typ}". '
                f'Доступны: {", ".join(VALID_TYPES)}.')
            return metadata
        column_dict[name] = typ

    # Auto-add ID:int
    full_columns = {'ID': 'int', **column_dict}
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

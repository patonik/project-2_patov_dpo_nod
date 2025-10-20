import json

from .parser import parse_values, parse_where, parse_set
from .utils import load_table_data, save_table_data
from .decorators import handle_db_errors, confirm_action, log_time, create_cacher
from .utils import load_metadata, save_metadata
from enum import Enum

META_FILE = 'db_meta.json'

VALID_TYPES = {'int', 'str', 'bool'}

cacher = create_cacher()


class CacheAction(Enum):
    GET = 'get'
    CLEAR = 'clear'


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

    full_columns = {'id': 'int', **column_dict}
    metadata[table_name] = full_columns
    save_metadata(META_FILE, metadata)
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        f'{", ".join([f"{k}:{v}" for k, v in full_columns.items()])}')
    return metadata

@confirm_action("table removal")
def drop_table(metadata, table_name):
    """
    Drop a table from metadata.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    save_metadata(META_FILE, metadata)
    cacher(CacheAction.CLEAR.value, table_name)
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


@handle_db_errors
@log_time
def insert(args, metadata):
    table_name = args[2].lower()
    if table_name not in metadata.keys():
        raise KeyError(table_name)
    types = list(metadata[table_name].values())[1:]
    columns = list(metadata[table_name].keys())[1:]
    vals = args[4:]
    if len(types) != len(vals):
        raise ValueError(f"Ожидается {len(types)} значений, "
                         f"получено {len(vals)}.")
    values = parse_values(list(zip(types, args[4:])))
    data = load_table_data(table_name)
    data = append_values(columns, values, data)
    save_table_data(table_name, data)
    cacher(CacheAction.CLEAR.value, table_name)
    new_id = data[-1]['id']
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')


def append_values(user_columns, values, data):
    """
    Insert new record. Returns updated data.
    """
    record = {'id': data[-1]['id'] + 1 if len(data) > 0 else 1}
    for col, val in zip(user_columns, values):
        record[col] = val

    data.append(record)
    return data

@handle_db_errors
@log_time
def select(args, metadata):
    table_name = args[2].lower()
    if table_name not in metadata.keys():
        raise KeyError(table_name)
    where_clause = None
    if len(args) > 3 and args[3].lower() == 'where':
        where_str = ' '.join(args[4:])
        where_clause = parse_where(where_str, metadata[table_name])
    cache_key = (table_name, json.dumps(where_clause, sort_keys=True))
    data = load_table_data(table_name)

    def select_func():
        return filter_select(data, where_clause)

    results = cacher(CacheAction.GET.value, table_name, cache_key, select_func)
    types = metadata.get(table_name, {})
    return results, types



def filter_select(data, where_clause=None):
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

@handle_db_errors
def update(args, metadata):
    table_name = args[1].lower()
    where_str, set_str = set_params(args)
    if table_name not in metadata.keys():
        raise KeyError(table_name)
    set_clause = parse_set(set_str, metadata[table_name])
    where_clause = parse_where(where_str, metadata[table_name])
    data = load_table_data(table_name)
    data = replace(data, set_clause, where_clause)
    save_table_data(table_name, data)
    cacher(CacheAction.CLEAR.value, table_name)
    print(f'Запись в таблице "{table_name}" успешно обновлена.')


def set_params(args):
    where_str = None
    where_ind = -1
    for i, val in enumerate(args):
        if val.lower() == 'where':
            where_ind = i
            break
    if where_ind != -1:
        set_str = ' '.join(args[3:where_ind])
        where_str = ' '.join(args[where_ind + 1:])
    else:
        set_str = ' '.join(args[3:])
    return where_str, set_str


def replace(data, set_clause, where_clause):
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
                    record[col] = new_val
    return data

@handle_db_errors
@confirm_action('entry deletion')
def delete(args, metadata):
    table_name = args[2].lower()
    where_str = ' '.join(args[4:])
    if table_name not in metadata.keys():
        raise KeyError(table_name)
    where_clause = parse_where(where_str, metadata[table_name])
    data = load_table_data(table_name)
    data = remove(data, where_clause)
    save_table_data(table_name, data)
    cacher(CacheAction.CLEAR.value, table_name)
    print(f'Запись успешно удалена из таблицы "{table_name}".')


def remove(data, where_clause):
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

@handle_db_errors
def info(args, metadata):
    table_name = args[1].lower()
    if table_name not in metadata.keys():
        raise KeyError(table_name)
    data = load_table_data(table_name)
    get_table_info(metadata, table_name, data)


def get_table_info(metadata, table_name, data):
    """
    Get table info.
    """
    columns = metadata[table_name]
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {', '.join([f'{k}:{v}' for k, v in columns.items()])}")
    print(f"Количество записей: {len(data)}")


def get_db_schema():
    return load_metadata(META_FILE)

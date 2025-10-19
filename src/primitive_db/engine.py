import shlex

import prettytable

from .core import (
    create_table,
    delete,
    drop_table,
    get_table_info,
    insert,
    list_tables,
    select,
    update,
)
from .parser import parse_set, parse_values, parse_where
from .utils import load_metadata, load_table_data, save_metadata, save_table_data

META_FILE = 'db_meta.json'  # Constant for filepath


def run():
    print("***База данных***")
    print_help()  # Initial help
    while True:
        user_input = input(">>> Введите команду: ").strip()
        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError as e:
            print(f"Ошибка парсинга: {e}. Попробуйте снова.")
            continue

        command = args[0].lower()
        metadata = load_metadata(META_FILE)

        if command == 'insert':
            # Parse: insert into table values
            if (len(args) < 4 or args[1].lower() != 'into'
                    or args[3].lower() != 'values'):
                print("Формат: insert into <table> values (<val1> <val2> ...)")
                continue
            table_name = args[2].lower()
            try:
                if table_name not in metadata.keys():
                    raise KeyError(f"Table {table_name} does not exist")
                types = list(metadata[table_name].values())[1:]
                columns = list(metadata[table_name].keys())[1:]
                vals = args[4:]
                if len(types) != len(vals):
                    raise ValueError(f"Ожидается {len(types)} значений, "
                                     f"получено {len(vals)}.")
                values = parse_values(list(zip(types, args[4:])))
                data = load_table_data(table_name)
                data = insert(columns, values, data)
                save_table_data(table_name, data)
                new_id = data[-1]['id']
                print(
                    f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
            except (KeyError, ValueError) as e:
                print(f"Ошибка: {e}")

        elif command == 'select':
            # select from table [where col = val]
            if len(args) < 3 or args[1].lower() != 'from':
                print("Формат: select from <table> [where <cond>]")
                continue
            table_name = args[2].lower()
            where_clause = {}
            if len(args) > 3 and args[3].lower() == 'where':
                where_str = ' '.join(args[4:])
                try:
                    where_clause = parse_where(where_str, metadata[table_name])
                except ValueError as e:
                    print(f"Ошибка: {e}")
                    continue
            try:
                if table_name not in metadata.keys():
                    raise KeyError(f"Table {table_name} does not exist")
                data = load_table_data(table_name)
                results = select(data, where_clause)
                types = metadata.get(table_name, {})
                print_select_results(results, types)
            except KeyError as e:
                print(f"Ошибка: {e}")

        elif command == 'update':
            # update table set col = val where col = val
            if len(args) < 6 or args[2].lower() != 'set':
                print("Формат: update <table> set <col> = <val> where <cond>")
                continue
            table_name = args[1].lower()
            where_str = None
            where_ind = -1
            for i,val in enumerate(args):
                if val.lower() == 'where':
                    where_ind = i
                    break
            if where_ind != -1:
                set_str = ' '.join(args[3:where_ind])
                where_str = ' '.join(args[where_ind + 1:])
            else:
                set_str = ' '.join(args[3:])
            try:
                if table_name not in metadata.keys():
                    raise KeyError(f"Table {table_name} does not exist")
                set_clause = parse_set(set_str, metadata[table_name])
                where_clause = parse_where(where_str, metadata[table_name])
                data = load_table_data(table_name)
                data = update(data, set_clause, where_clause)
                save_table_data(table_name, data)
                print(f'Запись в таблице "{table_name}" успешно обновлена.')
            except (KeyError, ValueError) as e:
                print(f"Ошибка: {e}")

        elif command == 'delete':
            # delete from table where col = val
            if len(args) < 4 or args[1].lower() != 'from' or args[3].lower() != 'where':
                print("Формат: delete from <table> where <cond>")
                continue
            table_name = args[2].lower()
            where_str = ' '.join(args[4:])
            try:
                if table_name not in metadata.keys():
                    raise KeyError(f"Table {table_name} does not exist")
                where_clause = parse_where(where_str, metadata[table_name])
                data = load_table_data(table_name)
                data = delete(data, where_clause)
                save_table_data(table_name, data)
                print(f'Запись успешно удалена из таблицы "{table_name}".')
            except (KeyError, ValueError) as e:
                print(f"Ошибка: {e}")

        elif command == 'info':
            if len(args) != 2:
                print("Формат: info <table>")
                continue
            table_name = args[1].lower()
            try:
                if table_name not in metadata.keys():
                    raise KeyError(f"Table {table_name} does not exist")
                data = load_table_data(table_name)
                get_table_info(metadata, table_name, data)
            except KeyError as e:
                print(f"Ошибка: {e}")

        elif command == 'create_table':
            if len(args) < 3:
                print("Некорректное значение. "
                      "Формат: create_table <имя> <столбец1:тип> ...")
                continue
            table_name = args[1].lower()
            types = [t.lower() for t in args[2:]]
            metadata = create_table(metadata, table_name, types)
        elif command == 'drop_table':
            if len(args) != 2:
                print("Некорректное значение. Формат: drop_table <имя>")
                continue
            table_name = args[1].lower()
            metadata = drop_table(metadata, table_name)
        elif command == 'list_tables':
            list_tables(metadata)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            print("Выход из программы.")
            break
        else:
            print(f'Функции "{command}" нет. Попробуйте снова.')

        # Save only if metadata changed (create/drop)
        if command in ['create_table', 'drop_table']:
            save_metadata(META_FILE, metadata)


def print_select_results(records, columns):
    """
    Print select with prettytable.
    """
    if not records:
        print("Нет записей.")
        return
    table = prettytable.PrettyTable()
    table.field_names = list(columns.keys())  # ID first
    for rec in sorted(records, key=lambda x: x['id']):  # Sort by ID
        row = [rec.get(col, '') for col in columns]
        table.add_row(row)
    print(table)


def print_help():
    print("\n***База данных***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1> <значение2> ...) - создать запись.")
    print(
        "<command> select from <имя_таблицы> "
        "where <столбец> = <значение> - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись.")
    print(
        "<command> delete from <имя_таблицы> "
        "where <столбец> = <значение> - удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> create_table <имя_таблицы> "
          "<столбец1:тип> <столбец2:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

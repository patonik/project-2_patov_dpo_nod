import shlex

import prettytable

from .core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
    info, get_db_schema
)



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
        metadata = get_db_schema()

        if command == 'insert':
            if (len(args) < 4 or args[1].lower() != 'into'
                    or args[3].lower() != 'values'):
                print("Формат: insert into <table> values (<val1> <val2> ...)")
                continue
            insert(args, metadata)

        elif command == 'select':
            if len(args) < 3 or args[1].lower() != 'from':
                print("Формат: select from <table> [where <cond>]")
                continue
            result = select(args, metadata)
            if result:
                print_select_results(*result)

        elif command == 'update':
            if len(args) < 6 or args[2].lower() != 'set':
                print("Формат: update <table> set <col> = <val> where <cond>")
                continue
            update(args, metadata)

        elif command == 'delete':
            if len(args) < 4 or args[1].lower() != 'from' or args[3].lower() != 'where':
                print("Формат: delete from <table> where <cond>")
                continue
            delete(args, metadata)

        elif command == 'info':
            if len(args) != 2:
                print("Формат: info <table>")
                continue
            info(args, metadata)

        elif command == 'create_table':
            if len(args) < 3:
                print("Некорректное значение. "
                      "Формат: create_table <имя> <столбец1:тип> ...")
                continue
            table_name = args[1].lower()
            types = [t.lower() for t in args[2:]]
            create_table(metadata, table_name, types)

        elif command == 'drop_table':
            if len(args) != 2:
                print("Некорректное значение. Формат: drop_table <имя>")
                continue
            table_name = args[1].lower()
            drop_table(metadata, table_name)
        elif command == 'list_tables':
            list_tables(metadata)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            print("Выход из программы.")
            break
        else:
            print(f'Функции "{command}" нет. Попробуйте снова.')


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

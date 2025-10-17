import shlex

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata

META_FILE = 'db_meta.json'  # Constant for filepath


def print_help():
    """
    Prints the help message for the current mode.
    """
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> "
          "<столбец1:тип> <столбец2:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


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

        if command == 'create_table':
            if len(args) < 3:
                print("Некорректное значение. "
                      "Формат: create_table <имя> <столбец1:тип> ...")
                continue
            table_name = args[1]
            columns = args[2:]
            metadata = create_table(metadata, table_name, columns)
        elif command == 'drop_table':
            if len(args) != 2:
                print("Некорректное значение. Формат: drop_table <имя>")
                continue
            table_name = args[1]
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

import time
from json import JSONDecodeError
from typing import Literal

import prompt


def handle_db_errors(func):
    """
    Decorator to handle common database errors.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. Возможно, база данных не инициализирована.")
        except JSONDecodeError as e:
            print(f"Data Extraction Error: {e}")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

    return wrapper


def confirm_action(action_name):
    """
    Decorator to confirm dangerous actions.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            response = prompt.string(f'Вы уверены, что хотите выполнить '
                                     f'"{action_name}"? [y/n]: ')
            if response.lower() != 'y':
                print(f'Операция "{action_name}" отменена.')
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """
    Decorator to log execution time.
    """

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f'Функция {func.__name__} выполнилась за {end - start:.3f} секунд.')
        return result

    return wrapper


def create_cacher():
    """
    Create a caching function using closure.
    """
    cache = {}

    def cache_result(action: Literal['get', 'clear'], table_name, key=None,
                     value_func=None):
        """
        Check cache; compute and store if not present.
        """
        match action:
            case 'get':
                if table_name in cache:
                    if key in cache[table_name]:
                        return cache[table_name][key]
                else:
                    cache[table_name] = {}
                result = value_func()
                cache[table_name][key] = result
                return result
            case 'clear':
                if table_name in cache:
                    cache.pop(table_name)
                return None
            case _:
                return None

    return cache_result

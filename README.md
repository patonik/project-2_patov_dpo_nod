# project-2_patov_dpo_nod

## Управление таблицами

Команды:

- `create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...` - Создать таблицу (
  типы: int, str, bool). Авто-добавляется ID:int.
- `list_tables` - Список таблиц.
- `drop_table <имя_таблицы>` - Удалить таблицу.
- `help` - Справка.
- `exit` - Выход.

Пример использования:
<details>
<summary>Click to play the recording</summary>

<a title="Labyrinth of Treasures Demo" href="https://asciinema.org/a/eBWgUxX9o3EUConARdGK8DlDU?autoplay=1" target="_blank">
<img src="https://asciinema.org/a/eBWgUxX9o3EUConARdGK8DlDU.svg" style="max-width:100%;" alt="asciicast" />
</a>
</details>

## CRUD-операции

Новые команды:
- `insert into <table> values (<val1>, <val2>, ...)` - Добавить запись (без ID).
- `select from <table> [where <col> = <val>]` - Выбрать записи.
- `update <table> set <col> = <new_val> where <col> = <val>` - Обновить.
- `delete from <table> where <col> = <val>` - Удалить.
- `info <table>` - Инфо о таблице.

Пример:
<details>
<summary>Click to play the recording</summary>

<a title="Labyrinth of Treasures Demo" href="https://asciinema.org/a/f77820xJ0Lp50UddEzGkn3rba?autoplay=1" target="_blank">
<img src="https://asciinema.org/a/f77820xJ0Lp50UddEzGkn3rba.svg" style="max-width:100%;" alt="asciicast" />
</a>
</details>





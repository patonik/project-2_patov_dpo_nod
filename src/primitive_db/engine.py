#!/usr/bin/env python3

from prompt import string


def welcome():
    print("""Первая попытка запустить проект!

 ***
 <command> exit - выйти из программы
 <command> help - справочная информация
 Введите команду: help
 
 <command> exit - выйти из программы
 <command> help - справочная информация""")
    string("Введите команду: _")


if __name__ == '__main__':
    welcome()
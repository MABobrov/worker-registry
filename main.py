"""Программа учёта работников ООО «Турбо».

Действия:
1. Ввод данных работников с клавиатуры.
2. Вывод фамилий работников, чей стаж превышает введённое значение.
3. Сообщение, если таких работников нет.
"""

from __future__ import annotations

import logging
import sys

from worker_registry import WORKER, WorkerRegistry, WorkerValidationError
from worker_registry.worker import POSITIONS

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def ask_int(prompt: str, minimum: int = 0) -> int:
    """Запрашивает целое число не меньше minimum. Повторяет запрос при ошибке."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print(f"  Ошибка: «{raw}» не является целым числом. Повторите ввод.")
            continue
        if value < minimum:
            print(f"  Ошибка: значение должно быть не меньше {minimum}.")
            continue
        return value


def input_worker(index: int) -> WORKER:
    """Вводит данные одного работника с клавиатуры и создаёт объект WORKER."""
    print(f"\nРаботник № {index}")
    while True:
        try:
            full_name = input("  Фамилия и инициалы: ")
            position = input("  Должность: ")
            salary = input("  Зарплата, руб.: ")
            hire_year = input("  Год поступления на работу: ")
            return WORKER(full_name, position, salary, int(hire_year))
        except (WorkerValidationError, ValueError) as exc:
            print(f"  Ошибка: {exc}. Повторите ввод работника.")


def print_positions() -> None:
    """Выводит справочник должностей."""
    print("Справочник должностей ООО «Турбо»:")
    for pos in POSITIONS:
        print(f"  - {pos}")


def main() -> int:
    print("=== Учёт работников ООО «Турбо» (Турбо Облако) ===")
    print_positions()

    count = ask_int("\nСколько работников ввести? ", minimum=1)
    registry = WorkerRegistry()
    for i in range(1, count + 1):
        registry.add(input_worker(i))

    print("\nВведённые работники:")
    for worker in registry:
        print("  " + worker.display())

    threshold = ask_int("\nВведите стаж (полных лет). Показать работников со стажем больше: ")
    names = registry.names_with_seniority_over(threshold)

    print()
    if names:
        print(f"Работники со стажем больше {threshold} лет:")
        for name in names:
            print(f"  - {name}")
    else:
        print(f"Работников со стажем больше {threshold} лет нет.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nВвод прерван.")
        sys.exit(1)

"""Модуль worker — класс WORKER и реестр работников.

Класс WORKER хранит данные одного работника ООО «Турбо».
Класс WorkerRegistry хранит список работников и выполняет выборки.
"""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Iterable, Iterator

logger = logging.getLogger(__name__)

# Должности, принятые в ООО «Турбо» (бренд «Турбо Облако»).
POSITIONS: tuple[str, ...] = (
    "Генеральный директор",
    "Технический директор",
    "Руководитель продукта",
    "Архитектор",
    "Lead ML Engineer",
    "ML-инженер",
    "Инженер DevOps",
    "Разработчик",
    "Системный аналитик",
    "Инженер по тестированию",
    "Инженер эксплуатации",
    "Менеджер по продажам",
)

FOUNDATION_YEAR = 2012  # год основания облачного бизнеса «Турбо Облако»


class WorkerValidationError(ValueError):
    """Ошибка проверки данных работника."""


class WORKER:
    """Работник организации.

    Поля класса закрыты. Доступ к полям выполняют свойства и методы.

    Attributes:
        full_name: Фамилия и инициалы, например «Иванов И. И.».
        position: Название должности из списка POSITIONS.
        salary: Зарплата в рублях.
        hire_year: Год поступления на работу.
    """

    _instances: int = 0  # счётчик живых объектов (для деструктора и тестов)

    # ------------------------------------------------------------------
    # Конструкторы
    # ------------------------------------------------------------------
    def __init__(
        self,
        full_name: str = "Не указано",
        position: str = "Разработчик",
        salary: Decimal | int | float | str = 0,
        hire_year: int | None = None,
    ) -> None:
        """Конструктор. Без аргументов работает как конструктор по умолчанию."""
        self._full_name: str = ""
        self._position: str = ""
        self._salary: Decimal = Decimal(0)
        self._hire_year: int = 0

        self.full_name = full_name
        self.position = position
        self.salary = salary
        self.hire_year = date.today().year if hire_year is None else hire_year

        WORKER._instances += 1
        logger.debug("WORKER создан: %s", self)

    @classmethod
    def from_name_and_position(cls, full_name: str, position: str) -> "WORKER":
        """Конструктор с двумя параметрами. Зарплата — 0, год — текущий."""
        return cls(full_name=full_name, position=position)

    @classmethod
    def from_csv_line(cls, line: str, sep: str = ";") -> "WORKER":
        """Конструктор из строки вида «Фамилия И. О.;Должность;Зарплата;Год»."""
        parts = [p.strip() for p in line.split(sep)]
        if len(parts) != 4:
            raise WorkerValidationError(
                f"Ожидается 4 поля через «{sep}», получено {len(parts)}: {line!r}"
            )
        full_name, position, salary, year = parts
        return cls(full_name, position, salary, int(year))

    @classmethod
    def from_dict(cls, data: dict) -> "WORKER":
        """Конструктор из словаря с ключами full_name, position, salary, hire_year."""
        try:
            return cls(
                data["full_name"], data["position"], data["salary"], int(data["hire_year"])
            )
        except KeyError as exc:
            raise WorkerValidationError(f"Нет обязательного поля {exc}") from exc

    # ------------------------------------------------------------------
    # Деструктор
    # ------------------------------------------------------------------
    def __del__(self) -> None:
        """Деструктор. Уменьшает счётчик объектов и пишет сообщение в журнал."""
        WORKER._instances = max(0, WORKER._instances - 1)
        logger.debug("WORKER удалён: %s", getattr(self, "_full_name", "?"))

    @classmethod
    def instances(cls) -> int:
        """Возвращает число живых объектов WORKER."""
        return cls._instances

    # ------------------------------------------------------------------
    # Свойства (инкапсуляция + проверка)
    # ------------------------------------------------------------------
    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        value = str(value).strip()
        if not value:
            raise WorkerValidationError("Фамилия и инициалы не могут быть пустыми")
        self._full_name = value

    @property
    def position(self) -> str:
        return self._position

    @position.setter
    def position(self, value: str) -> None:
        value = str(value).strip()
        if not value:
            raise WorkerValidationError("Должность не может быть пустой")
        if value not in POSITIONS:
            logger.warning("Должность «%s» отсутствует в справочнике", value)
        self._position = value

    @property
    def salary(self) -> Decimal:
        return self._salary

    @salary.setter
    def salary(self, value: Decimal | int | float | str) -> None:
        try:
            amount = Decimal(str(value).replace(" ", "").replace(",", "."))
        except InvalidOperation as exc:
            raise WorkerValidationError(f"Зарплата должна быть числом: {value!r}") from exc
        if amount < 0:
            raise WorkerValidationError("Зарплата не может быть отрицательной")
        self._salary = amount.quantize(Decimal("0.01"))

    @property
    def hire_year(self) -> int:
        return self._hire_year

    @hire_year.setter
    def hire_year(self, value: int) -> None:
        try:
            year = int(value)
        except (TypeError, ValueError) as exc:
            raise WorkerValidationError(f"Год должен быть целым числом: {value!r}") from exc
        current = date.today().year
        if not FOUNDATION_YEAR <= year <= current:
            raise WorkerValidationError(
                f"Год поступления должен быть в диапазоне {FOUNDATION_YEAR}–{current}"
            )
        self._hire_year = year

    # ------------------------------------------------------------------
    # Методы по заданию
    # ------------------------------------------------------------------
    def seniority(self, on_year: int | None = None) -> int:
        """Возвращает стаж работы в организации в полных годах."""
        year = date.today().year if on_year is None else on_year
        return max(0, year - self._hire_year)

    def update(
        self,
        full_name: str | None = None,
        position: str | None = None,
        salary: Decimal | int | float | str | None = None,
        hire_year: int | None = None,
    ) -> None:
        """Изменяет переданные поля. Поля со значением None не меняются."""
        if full_name is not None:
            self.full_name = full_name
        if position is not None:
            self.position = position
        if salary is not None:
            self.salary = salary
        if hire_year is not None:
            self.hire_year = hire_year

    def display(self) -> str:
        """Возвращает строку для вывода на дисплей."""
        return (
            f"{self._full_name:<22} {self._position:<26} "
            f"{self._salary:>12,.2f} руб.  {self._hire_year}  стаж {self.seniority()} лет"
        )

    def to_dict(self) -> dict:
        """Возвращает поля в виде словаря."""
        return {
            "full_name": self._full_name,
            "position": self._position,
            "salary": str(self._salary),
            "hire_year": self._hire_year,
        }

    # ------------------------------------------------------------------
    # Служебные методы
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return self.display()

    def __repr__(self) -> str:
        return (
            f"WORKER({self._full_name!r}, {self._position!r}, "
            f"{self._salary!r}, {self._hire_year})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WORKER):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:
        return hash((self._full_name, self._position, self._salary, self._hire_year))


class WorkerRegistry:
    """Реестр работников. Хранит объекты WORKER в стандартном списке list."""

    def __init__(self, workers: Iterable[WORKER] = ()) -> None:
        self._workers: list[WORKER] = list(workers)

    def add(self, worker: WORKER) -> None:
        """Добавляет работника в реестр."""
        if not isinstance(worker, WORKER):
            raise TypeError("В реестр можно добавить только объект WORKER")
        self._workers.append(worker)

    def remove(self, full_name: str) -> bool:
        """Удаляет первого работника с указанной фамилией. Возвращает True при успехе."""
        for i, w in enumerate(self._workers):
            if w.full_name == full_name:
                del self._workers[i]
                return True
        return False

    def with_seniority_over(self, years: int, on_year: int | None = None) -> list[WORKER]:
        """Возвращает работников, чей стаж строго превышает years."""
        if years < 0:
            raise WorkerValidationError("Стаж не может быть отрицательным")
        return [w for w in self._workers if w.seniority(on_year) > years]

    def names_with_seniority_over(self, years: int, on_year: int | None = None) -> list[str]:
        """Возвращает фамилии работников со стажем больше years."""
        return [w.full_name for w in self.with_seniority_over(years, on_year)]

    def __len__(self) -> int:
        return len(self._workers)

    def __iter__(self) -> Iterator[WORKER]:
        return iter(self._workers)

    def __getitem__(self, index: int) -> WORKER:
        return self._workers[index]

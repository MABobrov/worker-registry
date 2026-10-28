"""Тесты класса WORKER и реестра WorkerRegistry."""

import gc
from datetime import date
from decimal import Decimal

import pytest

from worker_registry import WORKER, WorkerRegistry, WorkerValidationError

YEAR = date.today().year


def test_default_constructor():
    w = WORKER()
    assert w.full_name == "Не указано"
    assert w.position == "Разработчик"
    assert w.salary == Decimal("0.00")
    assert w.hire_year == YEAR


def test_full_constructor():
    w = WORKER("Иванов И. И.", "ML-инженер", 250000, 2020)
    assert w.full_name == "Иванов И. И."
    assert w.position == "ML-инженер"
    assert w.salary == Decimal("250000.00")
    assert w.hire_year == 2020


def test_alternative_constructors():
    w1 = WORKER.from_name_and_position("Петров П. П.", "Архитектор")
    assert w1.salary == 0 and w1.hire_year == YEAR
    w2 = WORKER.from_csv_line("Сидоров С. С.;Инженер DevOps;180 000,50;2019")
    assert w2.salary == Decimal("180000.50") and w2.hire_year == 2019
    w3 = WORKER.from_dict(
        {"full_name": "Кузнецов К. К.", "position": "Разработчик", "salary": "1", "hire_year": 2015}
    )
    assert w3.full_name == "Кузнецов К. К."


@pytest.mark.parametrize(
    "kwargs",
    [
        {"full_name": "  "},
        {"position": ""},
        {"salary": -1},
        {"salary": "abc"},
        {"hire_year": 1990},
        {"hire_year": YEAR + 1},
        {"hire_year": "год"},
    ],
)
def test_validation_errors(kwargs):
    base = {"full_name": "Иванов И. И.", "position": "Разработчик", "salary": 1, "hire_year": 2020}
    base.update(kwargs)
    with pytest.raises(WorkerValidationError):
        WORKER(**base)


def test_csv_wrong_field_count():
    with pytest.raises(WorkerValidationError):
        WORKER.from_csv_line("a;b;c")


def test_encapsulation_no_public_fields():
    w = WORKER("Иванов И. И.", "Разработчик", 1, 2020)
    assert not hasattr(w, "full_name_")  # нет открытых полей-дубликатов
    assert all(name.startswith("_") for name in vars(w))


def test_update_and_display():
    w = WORKER("Иванов И. И.", "Разработчик", 100000, 2018)
    w.update(position="Lead ML Engineer", salary="300000")
    assert w.position == "Lead ML Engineer"
    assert w.salary == Decimal("300000.00")
    text = w.display()
    assert "Иванов И. И." in text and "Lead ML Engineer" in text and "2018" in text


def test_seniority():
    w = WORKER("Иванов И. И.", "Разработчик", 1, 2020)
    assert w.seniority(on_year=2026) == 6
    assert w.seniority(on_year=2019) == 0


def test_registry_filter_and_empty_message_case():
    reg = WorkerRegistry()
    reg.add(WORKER("Иванов И. И.", "Разработчик", 1, 2015))
    reg.add(WORKER("Петров П. П.", "Архитектор", 1, 2022))
    reg.add(WORKER("Сидоров С. С.", "ML-инженер", 1, 2025))
    assert reg.names_with_seniority_over(3, on_year=2026) == ["Иванов И. И.", "Петров П. П."]
    assert reg.names_with_seniority_over(11, on_year=2026) == []
    assert len(reg) == 3
    assert reg.remove("Петров П. П.") is True
    assert reg.remove("Нет Н. Н.") is False
    with pytest.raises(WorkerValidationError):
        reg.with_seniority_over(-1)
    with pytest.raises(TypeError):
        reg.add("не работник")  # type: ignore[arg-type]


def test_destructor_decrements_counter():
    gc.collect()  # освобождаем объекты предыдущих тестов
    before = WORKER.instances()
    w = WORKER("Временный В. В.", "Разработчик", 1, 2020)
    assert WORKER.instances() == before + 1
    del w
    gc.collect()
    assert WORKER.instances() == before


def test_equality_and_dict_roundtrip():
    w = WORKER("Иванов И. И.", "Разработчик", "100", 2020)
    assert WORKER.from_dict(w.to_dict()) == w

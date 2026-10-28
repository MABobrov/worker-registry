"""Пакет worker_registry — учёт работников ООО «Турбо».

Экспортирует класс WORKER и реестр WorkerRegistry.
"""

from .worker import WORKER, WorkerRegistry, WorkerValidationError

__all__ = ["WORKER", "WorkerRegistry", "WorkerValidationError"]
__version__ = "1.0.0"

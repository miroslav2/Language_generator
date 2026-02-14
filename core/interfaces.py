from abc import ABC, abstractmethod
from typing import Any, Dict, List

class SignalUnit(ABC):
    """
    Базовая единица коммуникации (Звук, Жест, Свет).
    """
    def __init__(self, raw_value: Any, notation: str, features: Dict = None):
        self.raw_value = raw_value
        self.notation = notation
        self.features = features or {}

    def __repr__(self):
        return f"Signal({self.notation})"

class IModule(ABC):
    """
    Интерфейс для всех логических модулей.
    """
    def __init__(self, config: Dict):
        self.config = config

    @abstractmethod
    def process(self, input_data: Any) -> Any:
        pass
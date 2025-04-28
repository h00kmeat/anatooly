from abc import ABC, abstractmethod
from typing import Any, Tuple

class Detector(ABC):
    def __init__(self, directory: str):
        self.directory = directory

    @abstractmethod
    def detect(self) -> Tuple[bool, Any]:
        pass

    @abstractmethod
    def confidence(self) -> float:
        pass

from abc import ABC, abstractmethod


class TagExpressionElement(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

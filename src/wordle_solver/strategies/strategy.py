from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def select_guess(
        self,
        candidates: set[str],
    ) -> str:
        ...

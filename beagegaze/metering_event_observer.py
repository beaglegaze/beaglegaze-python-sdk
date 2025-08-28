from abc import ABC, abstractmethod
from .metering_event import MeteringEvent

class MeteringEventObserver(ABC):
    """
    Observer interface for handling metering events.
    """
    @abstractmethod
    async def handle(self, event: MeteringEvent) -> None:
        pass

    @abstractmethod
    def is_in_error_state(self) -> bool:
        pass

from dataclasses import dataclass
from .metering_event import MeteringEvent

@dataclass
class BatchReadyEvent(MeteringEvent):
    """
    Event fired when a batch is ready to be processed.
    """
    batch_sum: int

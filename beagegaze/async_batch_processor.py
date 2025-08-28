import asyncio
import threading
from .batch_mode import BatchMode
from .metering_event_observer import MeteringEventObserver
from .batch_ready_event import BatchReadyEvent

class AsyncBatchProcessor:
    def __init__(self, batch_mode: BatchMode):
        self.observers = []
        self.batch_mode = batch_mode
        self.batch_sum = 0
        self.lock = threading.Lock()

    def add_observer(self, observer: MeteringEventObserver):
        self.observers.append(observer)

    async def register_call_async(self, price_per_invocation: int):
        self._add_to_current_batch(price_per_invocation)

        if self._should_process_batch():
            await self._process_batch_async()

    def _add_to_current_batch(self, price_per_invocation: int):
        with self.lock:
            self.batch_sum += price_per_invocation

    def _should_process_batch(self) -> bool:
        return self.batch_mode.hit()

    async def _process_batch_async(self):
        print(f"Processing batch with sum {self.batch_sum}...")
        current_batch_sum = self._get_current_batch_sum()
        self._reset_batch()
        await self._notify_observers_async(BatchReadyEvent(current_batch_sum))

    def _get_current_batch_sum(self) -> int:
        with self.lock:
            return self.batch_sum

    def _reset_batch(self):
        with self.lock:
            self.batch_sum = 0

    async def _notify_observers_async(self, event: BatchReadyEvent):
        for observer in self.observers:
            await observer.handle(event)

    def is_in_error_state(self) -> bool:
        return any(observer.is_in_error_state() for observer in self.observers)

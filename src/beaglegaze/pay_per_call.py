import functools
import asyncio
from .async_batch_processor import AsyncBatchProcessor
from .metering_event_observer import MeteringEventObserver

_async_batch_processor = None

def set_processor(async_batch_processor: AsyncBatchProcessor):
    global _async_batch_processor
    _async_batch_processor = async_batch_processor

def add_event_observer(observer: MeteringEventObserver):
    if _async_batch_processor:
        _async_batch_processor.add_observer(observer)

def pay_per_call(price: int = 0, contract_address: str = None, network_url: str = None):
    """
    Decorator to mark methods that require a micro-payment for each call.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not _async_batch_processor:
                raise Exception("AsyncBatchProcessor not set")

            await _async_batch_processor.register_call_async(price)
            if _async_batch_processor.is_in_error_state():
                raise Exception("Micro-payment processing is in error state, method execution blocked.")

            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

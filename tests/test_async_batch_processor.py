import pytest
from unittest.mock import Mock, patch
from beaglegaze.async_batch_processor import AsyncBatchProcessor
from beaglegaze.batch_mode import BatchMode
from beaglegaze.contract_consumer import ContractConsumer
from beaglegaze.batch_ready_event import BatchReadyEvent
from beaglegaze.metering_event_observer import MeteringEventObserver

FIRST_CALL_AMOUNT = 50

@pytest.fixture
def async_processor():
    return AsyncBatchProcessor(BatchMode.OFF)

@pytest.mark.asyncio
async def test_should_notify_observers_when_batch_is_ready(async_processor, mocker):
    contract_consumer = mocker.Mock(spec=ContractConsumer)
    contract_consumer.handle = mocker.AsyncMock()
    async_processor.add_observer(contract_consumer)

    await async_processor.register_call_async(FIRST_CALL_AMOUNT)

    batch_ready_event = BatchReadyEvent(FIRST_CALL_AMOUNT)
    contract_consumer.handle.assert_called_once()
    called_event = contract_consumer.handle.call_args[0][0]
    assert called_event.batch_sum == batch_ready_event.batch_sum

@pytest.mark.asyncio
async def test_should_go_into_error_state_when_observer_throws_exception(async_processor):
    class FailingObserver(MeteringEventObserver):
        async def handle(self, event):
            raise RuntimeError("Observer failed")
        def is_in_error_state(self) -> bool:
            return True

    async_processor.add_observer(FailingObserver())

    assert async_processor.is_in_error_state()

@pytest.mark.asyncio
async def test_should_process_batch_when_batch_mode_is_random(mocker):
    async_processor = AsyncBatchProcessor(BatchMode.RANDOM)
    contract_consumer = mocker.Mock(spec=ContractConsumer)
    contract_consumer.handle = mocker.AsyncMock()
    async_processor.add_observer(contract_consumer)

    for i in range(50):
        await async_processor.register_call_async(5)

    assert contract_consumer.handle.call_count <= 49
    assert contract_consumer.handle.call_count >= 1

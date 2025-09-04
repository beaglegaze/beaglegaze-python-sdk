import pytest
from unittest.mock import Mock, patch
from beaglegaze.contract_consumer import ContractConsumer, IllegalStateException
from beaglegaze.batch_ready_event import BatchReadyEvent

BATCH_AMOUNT = 100
SUFFICIENT_FUNDS = 100
INSUFFICIENT_FUNDS = 50

@pytest.fixture
def mock_smart_contract(mocker):
    mock = mocker.Mock()
    # Mock has_valid_subscription to return False by default for existing tests
    mock.has_valid_subscription.return_value = False
    return mock

@pytest.fixture
def contract_consumer(mock_smart_contract):
    return ContractConsumer(mock_smart_contract)

@pytest.mark.asyncio
async def test_should_keep_throwing_exceptions_while_blocked(contract_consumer, mock_smart_contract):
    # setup
    mock_smart_contract.consume.side_effect = RuntimeError("Insufficient funds")

    # block consumer
    initial_batch_event = BatchReadyEvent(BATCH_AMOUNT)
    with pytest.raises(RuntimeError):
        await contract_consumer.handle(initial_batch_event)
    assert contract_consumer.is_in_error_state()

    # verify subsequent calls throw IllegalStateException
    second_batch_event = BatchReadyEvent(50)
    with pytest.raises(IllegalStateException):
        await contract_consumer.handle(second_batch_event)
    assert contract_consumer.is_in_error_state()

    third_batch_event = BatchReadyEvent(25)
    with pytest.raises(IllegalStateException):
        await contract_consumer.handle(third_batch_event)
    assert contract_consumer.is_in_error_state()

@pytest.mark.asyncio
async def test_should_unblock_when_receving_unblocking_attempt_event_with_sufficient_funds(contract_consumer, mock_smart_contract):
    # block consumer
    mock_smart_contract.consume.side_effect = RuntimeError("Insufficient funds")
    initial_batch_event = BatchReadyEvent(BATCH_AMOUNT)
    with pytest.raises(RuntimeError):
        await contract_consumer.handle(initial_batch_event)
    assert contract_consumer.is_in_error_state()

    # setup for unblocking
    mock_smart_contract.consume.side_effect = None
    mock_smart_contract.consume.return_value = True
    mock_smart_contract.get_client_funding.return_value = SUFFICIENT_FUNDS

    # attempt to handle batch event
    unblocking_batch_event = BatchReadyEvent(BATCH_AMOUNT)
    await contract_consumer.handle(unblocking_batch_event)

    assert not contract_consumer.is_in_error_state()
    assert mock_smart_contract.consume.call_count == 2

@pytest.mark.asyncio
async def test_should_remain_blocked_when_funding_is_insufficient_for_pending_batch(contract_consumer, mock_smart_contract):
    # block consumer
    mock_smart_contract.consume.side_effect = RuntimeError("Insufficient funds")
    initial_batch_event = BatchReadyEvent(BATCH_AMOUNT)
    with pytest.raises(RuntimeError):
        await contract_consumer.handle(initial_batch_event)
    assert contract_consumer.is_in_error_state()

    # setup for insufficient funding
    mock_smart_contract.get_client_funding.return_value = INSUFFICIENT_FUNDS

    # attempt to handle batch event
    batch_event = BatchReadyEvent(BATCH_AMOUNT)
    with pytest.raises(IllegalStateException):
        await contract_consumer.handle(batch_event)

    assert contract_consumer.is_in_error_state()
    assert mock_smart_contract.consume.call_count == 1

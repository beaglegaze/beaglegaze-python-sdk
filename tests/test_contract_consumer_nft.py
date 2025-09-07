import pytest
from unittest.mock import Mock
from beaglegaze.contract_consumer import ContractConsumer
from beaglegaze.batch_ready_event import BatchReadyEvent

BATCH_AMOUNT = 100

@pytest.fixture
def mock_smart_contract_with_subscription(mocker):
    mock = mocker.Mock()
    mock.has_valid_subscription.return_value = True
    return mock

@pytest.fixture
def mock_smart_contract_without_subscription(mocker):
    mock = mocker.Mock()
    mock.has_valid_subscription.return_value = False
    return mock

@pytest.fixture
def contract_consumer_with_subscription(mock_smart_contract_with_subscription):
    return ContractConsumer(mock_smart_contract_with_subscription)

@pytest.fixture
def contract_consumer_without_subscription(mock_smart_contract_without_subscription):
    return ContractConsumer(mock_smart_contract_without_subscription)

@pytest.mark.asyncio
async def test_should_check_for_nft_subscription_before_consuming_from_contract(
    contract_consumer_with_subscription, mock_smart_contract_with_subscription
):
    """
    Test that the contract consumer checks for a valid NFT subscription before
    consuming from the contract.
    """
    mock_smart_contract_with_subscription.consume.return_value = True

    batch_event = BatchReadyEvent(BATCH_AMOUNT)

    await contract_consumer_with_subscription.handle(batch_event)

    # Verify that subscription check was called
    mock_smart_contract_with_subscription.has_valid_subscription.assert_called_once()
    
    # Verify that consume was NOT called since subscription is valid
    mock_smart_contract_with_subscription.consume.assert_not_called()

    # Verify consumer is not in error state
    assert not contract_consumer_with_subscription.is_in_error_state()

@pytest.mark.asyncio
async def test_should_consume_normally_when_no_valid_subscription(
    contract_consumer_without_subscription, mock_smart_contract_without_subscription
):
    """
    Test that when no valid subscription exists, normal consumption occurs.
    """
    mock_smart_contract_without_subscription.consume.return_value = True

    batch_event = BatchReadyEvent(BATCH_AMOUNT)

    await contract_consumer_without_subscription.handle(batch_event)

    # Verify that subscription check was called
    mock_smart_contract_without_subscription.has_valid_subscription.assert_called_once()
    
    # Verify that consume was called since no valid subscription
    mock_smart_contract_without_subscription.consume.assert_called_once_with(BATCH_AMOUNT)

    # Verify consumer is not in error state
    assert not contract_consumer_without_subscription.is_in_error_state()

@pytest.mark.asyncio
async def test_should_handle_subscription_check_error_gracefully(
    contract_consumer_without_subscription, mock_smart_contract_without_subscription
):
    """
    Test that if subscription check fails, it falls back to normal consumption.
    """
    # Simulate subscription check failure
    mock_smart_contract_without_subscription.has_valid_subscription.side_effect = Exception("Network error")
    mock_smart_contract_without_subscription.consume.return_value = True

    batch_event = BatchReadyEvent(BATCH_AMOUNT)

    await contract_consumer_without_subscription.handle(batch_event)

    # Verify that subscription check was attempted
    mock_smart_contract_without_subscription.has_valid_subscription.assert_called_once()
    
    # Verify that consume was called as fallback
    mock_smart_contract_without_subscription.consume.assert_called_once_with(BATCH_AMOUNT)

    # Verify consumer is not in error state
    assert not contract_consumer_without_subscription.is_in_error_state()
"""
Example demonstrating the NFT subscription functionality in the BeagleGaze Python SDK.

This example shows how clients can purchase NFT subscriptions for flat-rate access
instead of paying per method call.
"""

import asyncio
from unittest.mock import Mock
from beaglegaze import SmartContract, ContractConsumer, BatchReadyEvent

async def nft_subscription_example():
    """
    Demonstrates the NFT subscription workflow:
    1. Client without subscription pays per call
    2. Client with subscription gets free access
    """
    print("🔥 BeagleGaze NFT Subscription Example")
    print("=" * 50)
    
    # Create mock smart contract for demonstration
    mock_contract = Mock()
    
    # Scenario 1: Client without subscription
    print("\n📱 Scenario 1: Client without valid subscription")
    mock_contract.has_valid_subscription.return_value = False
    mock_contract.consume.return_value = True
    
    consumer = ContractConsumer(mock_contract)
    batch_event = BatchReadyEvent(batch_sum=100)
    
    await consumer.handle(batch_event)
    
    print("✓ Subscription check called")
    print("✓ No valid subscription found")
    print("✓ Normal consumption executed (client charged)")
    print(f"  - consume() called: {mock_contract.consume.called}")
    
    # Scenario 2: Client with valid subscription
    print("\n🎫 Scenario 2: Client with valid NFT subscription")
    mock_contract.reset_mock()
    mock_contract.has_valid_subscription.return_value = True
    
    consumer2 = ContractConsumer(mock_contract)
    await consumer2.handle(batch_event)
    
    print("✓ Subscription check called")
    print("✓ Valid NFT subscription found")
    print("✓ Consumption skipped (client not charged)")
    print(f"  - consume() called: {mock_contract.consume.called}")
    
    # Scenario 3: Subscription check fails gracefully
    print("\n⚠️  Scenario 3: Subscription check error (graceful fallback)")
    mock_contract.reset_mock()
    mock_contract.has_valid_subscription.side_effect = Exception("Network error")
    mock_contract.consume.return_value = True
    
    consumer3 = ContractConsumer(mock_contract)
    await consumer3.handle(batch_event)
    
    print("✓ Subscription check failed gracefully")
    print("✓ Fallback to normal consumption")
    print(f"  - consume() called: {mock_contract.consume.called}")
    
    print("\n🎉 Example completed successfully!")
    print("\nKey Benefits:")
    print("- Clients can purchase NFT subscriptions for flat-rate access")
    print("- Automatic subscription validation before charging")
    print("- Backward compatible with existing pay-per-call model")
    print("- Graceful error handling for subscription checks")

if __name__ == "__main__":
    asyncio.run(nft_subscription_example())
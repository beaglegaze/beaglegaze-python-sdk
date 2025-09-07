import pytest
import json
import asyncio
from web3 import Web3
from beaglegaze.demo import Demo
from beaglegaze.async_batch_processor import AsyncBatchProcessor
from beaglegaze.batch_mode import BatchMode
from beaglegaze.smart_contract import SmartContract
from beaglegaze.contract_consumer import ContractConsumer
from beaglegaze.pay_per_call import set_processor
from tests.api.integration_test_base import hardhat_container, ethereum_testnet, CLIENT_ACCOUNT, SMART_CONTRACT_OWNER

@pytest.fixture
def w3(hardhat_container):
    return Web3(Web3.HTTPProvider(hardhat_container.get_network_address()))

@pytest.fixture
def deployed_contract(w3):
    with open('contracts/UsageContract_sol_UsageContract.abi', 'r') as f:
        abi = json.load(f)
    with open('contracts/UsageContract_sol_UsageContract.bin', 'r') as f:
        bytecode = f.read()

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    account = w3.eth.account.from_key(SMART_CONTRACT_OWNER)
    subscription_price = 1000000000000000000  # 1 ETH in wei
    tx_hash = contract.constructor(subscription_price).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
    })

    signed_tx = w3.eth.account.sign_transaction(tx_hash, private_key=account.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return w3.eth.contract(address=receipt.contractAddress, abi=abi)

@pytest.fixture
def setup_processor(w3, deployed_contract):
    async_processor = AsyncBatchProcessor(BatchMode.OFF)
    smart_contract = SmartContract(
        deployed_contract.address,
        w3.provider.endpoint_uri,
        CLIENT_ACCOUNT,
        10
    )
    contract_consumer = ContractConsumer(smart_contract)
    async_processor.add_observer(contract_consumer)
    set_processor(async_processor)
    return async_processor

@pytest.mark.asyncio
async def test_should_consume_correct_price_from_annotation(w3, deployed_contract, ethereum_testnet, setup_processor):
    ethereum_testnet.fund(10, deployed_contract.address)

    demo = Demo()
    for i in range(10):
        await demo.greet(f"JUnit{i}")

    await asyncio.sleep(5)

    client_funding = deployed_contract.functions.getClientFunding().call({'from': ethereum_testnet.get_address()})
    assert client_funding == 0

@pytest.mark.asyncio
async def test_should_block_tracked_method_after_consume_failure(setup_processor, deployed_contract, ethereum_testnet):
    ethereum_testnet.fund(1, deployed_contract.address)
    demo = Demo()
    await demo.greet("Success")
    await asyncio.sleep(1)

    with pytest.raises(Exception, match="Failed to consume from contract"):
        await demo.greet("Failure")

@pytest.mark.asyncio
async def test_should_unblock_tracked_method_after_refunding(deployed_contract, ethereum_testnet, setup_processor):
    ethereum_testnet.fund(1, deployed_contract.address)
    demo = Demo()
    await demo.greet("Success")
    await asyncio.sleep(1)

    with pytest.raises(Exception, match="Failed to consume from contract"):
        await demo.greet("Failure")

    ethereum_testnet.fund(10, deployed_contract.address)
    
    await asyncio.sleep(1)

    await demo.greet("Success after refund")

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
from tests.api.integration_test_base import hardhat_container, ethereum_testnet, CLIENT_ACCOUNT, SMART_CONTRACT_OWNER, DEVELOPER_ACCOUNT

@pytest.fixture(scope="module")
def w3(hardhat_container):
    return Web3(Web3.HTTPProvider(hardhat_container.get_network_address()))

@pytest.fixture(scope="function")
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

@pytest.mark.asyncio
async def test_should_associate_funding_with_client_and_only_pay_out_on_consume(w3, deployed_contract, ethereum_testnet):
    # Setup
    async_batch_processor = AsyncBatchProcessor(BatchMode.OFF)
    smart_contract = SmartContract(
        deployed_contract.address,
        w3.provider.endpoint_uri,
        CLIENT_ACCOUNT,
        10
    )
    contract_consumer = ContractConsumer(smart_contract)
    async_batch_processor.add_observer(contract_consumer)
    set_processor(async_batch_processor)

    # Fund client
    ethereum_testnet.fund(50, deployed_contract.address)

    # Verify initial funding
    client_funding = deployed_contract.functions.getClientFunding().call({'from': ethereum_testnet.get_address()})
    assert client_funding == 50

    # Trigger payable method call
    demo = Demo()
    await demo.greet("JUnit")
    await asyncio.sleep(2)

    # Verify funding after consumption
    client_funding_after = deployed_contract.functions.getClientFunding().call({'from': ethereum_testnet.get_address()})
    assert client_funding_after == 49

@pytest.mark.asyncio
async def test_should_track_developer_balances_and_allow_withdrawal(w3, deployed_contract, ethereum_testnet):
    # Setup
    async_batch_processor = AsyncBatchProcessor(BatchMode.OFF)
    smart_contract = SmartContract(
        deployed_contract.address,
        w3.provider.endpoint_uri,
        CLIENT_ACCOUNT,
        10
    )
    contract_consumer = ContractConsumer(smart_contract)
    async_batch_processor.add_observer(contract_consumer)
    set_processor(async_batch_processor)

    # Fund client
    ethereum_testnet.fund(50, deployed_contract.address)

    developer_account = w3.eth.account.from_key(SMART_CONTRACT_OWNER)

    # Verify initial developer balance
    initial_developer_balance = deployed_contract.functions.getDeveloperBalance().call({'from': developer_account.address})
    assert initial_developer_balance == 0

    # Trigger payment
    demo = Demo()
    await demo.greet("JUnit")
    await asyncio.sleep(2)

    # Verify developer balance is tracked
    developer_balance = deployed_contract.functions.getDeveloperBalance().call({'from': developer_account.address})
    assert developer_balance == 1

    # Verify developer can withdraw their balance
    tx_hash = deployed_contract.functions.withdrawBalance().build_transaction({
        'from': developer_account.address,
        'nonce': w3.eth.get_transaction_count(developer_account.address),
    })
    signed_tx = w3.eth.account.sign_transaction(tx_hash, private_key=developer_account.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

    final_developer_balance = deployed_contract.functions.getDeveloperBalance().call({'from': developer_account.address})
    assert final_developer_balance == 0

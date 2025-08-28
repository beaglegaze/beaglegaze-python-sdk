import pytest
import json
from web3 import Web3
from tests.api.integration_test_base import hardhat_container, ethereum_testnet, CLIENT_ACCOUNT, SMART_CONTRACT_OWNER

@pytest.fixture
def w3(hardhat_container):
    return Web3(Web3.HTTPProvider(hardhat_container.get_network_address()))

@pytest.fixture
def deployed_contract(w3):
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abi_path = os.path.join(base_dir, 'contracts', 'UsageContract_sol_UsageContract.abi')
    bin_path = os.path.join(base_dir, 'contracts', 'UsageContract_sol_UsageContract.bin')

    with open(abi_path, 'r') as f:
        abi = json.load(f)
    with open(bin_path, 'r') as f:
        bytecode = f.read()

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    account = w3.eth.account.from_key(SMART_CONTRACT_OWNER)

    tx_hash = contract.constructor().build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
    })

    signed_tx = w3.eth.account.sign_transaction(tx_hash, private_key=account.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return w3.eth.contract(address=receipt.contractAddress, abi=abi)

def get_client_contract(w3, contract_address):
    with open('contracts/UsageContract_sol_UsageContract.abi', 'r') as f:
        abi = json.load(f)
    return w3.eth.contract(address=contract_address, abi=abi)

@pytest.fixture(autouse=True)
def show_container_logs(hardhat_container, request):
    yield
    print("\n--- Hardhat Container Logs ---")
    print(hardhat_container.get_logs())
    print("--- End of Logs ---")

@pytest.mark.asyncio
async def test_should_payout_non_consumed_funds_to_client(w3, deployed_contract, ethereum_testnet):
    funding_amount = 1000
    ethereum_testnet.fund(funding_amount, deployed_contract.address)

    client_contract = get_client_contract(w3, deployed_contract.address)
    client_account = w3.eth.account.from_key(CLIENT_ACCOUNT)

    assert client_contract.functions.getClientFunding().call({'from': client_account.address}) == funding_amount

    tx_hash = client_contract.functions.requestPayout().build_transaction({
        'from': client_account.address,
        'nonce': w3.eth.get_transaction_count(client_account.address),
    })
    signed_tx = w3.eth.account.sign_transaction(tx_hash, private_key=client_account.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

    assert client_contract.functions.getClientFunding().call({'from': client_account.address}) == 0

@pytest.mark.asyncio
async def test_should_fail_payout_when_client_has_no_funds(w3, deployed_contract):
    client_contract = get_client_contract(w3, deployed_contract.address)
    client_account = w3.eth.account.from_key(CLIENT_ACCOUNT)

    with pytest.raises(Exception):
        tx_hash = client_contract.functions.requestPayout().build_transaction({
            'from': client_account.address,
            'nonce': w3.eth.get_transaction_count(client_account.address),
        })
        signed_tx = w3.eth.account.sign_transaction(tx_hash, private_key=client_account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash, raise_on_revert=True)

@pytest.mark.asyncio
async def test_should_payout_partial_funds_after_consumption(w3, deployed_contract, ethereum_testnet):
    funding_amount = 1000
    consume_amount = 300
    expected_remaining = funding_amount - consume_amount

    ethereum_testnet.fund(funding_amount, deployed_contract.address)

    client_contract = get_client_contract(w3, deployed_contract.address)
    client_account = w3.eth.account.from_key(CLIENT_ACCOUNT)

    tx_hash = client_contract.functions.consume(consume_amount).build_transaction({
        'from': client_account.address,
        'nonce': w3.eth.get_transaction_count(client_account.address),
    })
    signed_tx = w3.eth.account.sign_transaction(tx_hash, private_key=client_account.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

    assert client_contract.functions.getClientFunding().call({'from': client_account.address}) == expected_remaining

    tx_hash = client_contract.functions.requestPayout().build_transaction({
        'from': client_account.address,
        'nonce': w3.eth.get_transaction_count(client_account.address),
    })
    signed_tx = w3.eth.account.sign_transaction(tx_hash, private_key=client_account.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

    assert client_contract.functions.getClientFunding().call({'from': client_account.address}) == 0

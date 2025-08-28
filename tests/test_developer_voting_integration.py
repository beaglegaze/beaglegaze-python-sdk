from tests.api.integration_test_base import hardhat_container, DEVELOPER_ACCOUNT, SMART_CONTRACT_OWNER
import pytest
import json
from web3 import Web3


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

    tx_hash = contract.constructor().build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
    })

    signed_tx = w3.eth.account.sign_transaction(tx_hash, private_key=account.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return w3.eth.contract(address=receipt.contractAddress, abi=abi)

def load_contract_for_account(w3, contract_address, private_key):
    with open('contracts/UsageContract_sol_UsageContract.abi', 'r') as f:
        abi = json.load(f)
    return w3.eth.contract(address=contract_address, abi=abi)

@pytest.mark.asyncio
async def test_should_register_contract_owner_as_first_developer(w3, deployed_contract):
    owner_account = w3.eth.account.from_key(SMART_CONTRACT_OWNER)
    assert deployed_contract.functions.isDeveloper().call({'from': owner_account.address})

@pytest.mark.asyncio
async def test_should_register_second_developer_with_owner_approval(w3, deployed_contract):
    requesting_developer_account = w3.eth.account.from_key(DEVELOPER_ACCOUNT)
    requesting_developer_contract = load_contract_for_account(w3, deployed_contract.address, DEVELOPER_ACCOUNT)

    tx_hash = requesting_developer_contract.functions.requestDeveloperRegistration().build_transaction({
        'from': requesting_developer_account.address,
        'nonce': w3.eth.get_transaction_count(requesting_developer_account.address),
    })
    signed_tx = w3.eth.account.sign_transaction(tx_hash, private_key=requesting_developer_account.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

    assert not requesting_developer_contract.functions.isDeveloper().call({'from': requesting_developer_account.address})

    owner_account = w3.eth.account.from_key(SMART_CONTRACT_OWNER)
    tx_hash = deployed_contract.functions.voteForDeveloper(requesting_developer_account.address, True).build_transaction({
        'from': owner_account.address,
        'nonce': w3.eth.get_transaction_count(owner_account.address),
    })
    signed_tx = w3.eth.account.sign_transaction(tx_hash, private_key=owner_account.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

    assert requesting_developer_contract.functions.isDeveloper().call({'from': requesting_developer_account.address})

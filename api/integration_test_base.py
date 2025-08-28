import pytest
from .custom_ethereum_testnet_container import CustomEthereumTestnetContainer
from .ethereum_testnet import EthereumTestnet

CLIENT_ACCOUNT = "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
SMART_CONTRACT_OWNER = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
DEVELOPER_ACCOUNT = "0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"

@pytest.fixture(scope="module")
def hardhat_container():
    with CustomEthereumTestnetContainer("hardhat-testnet") as container:
        container.wait_for_ready()
        yield container

@pytest.fixture(scope="module")
def ethereum_testnet(hardhat_container):
    network_address = hardhat_container.get_network_address()
    return EthereumTestnet(network_address, CLIENT_ACCOUNT)

def fund_client(ethereum_testnet, amount, contract_address):
    ethereum_testnet.fund(amount, contract_address)

def fund_as_client(ethereum_testnet, private_key, contract_address, amount):
    ethereum_testnet.fund_as_client(private_key, contract_address, amount)

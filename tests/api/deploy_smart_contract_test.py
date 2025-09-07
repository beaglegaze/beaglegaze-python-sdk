import pytest
import json
from web3 import Web3
from .ethereum_testnet import EthereumTestnet

SMART_CONTRACT_ADDRESS = "0x289b72ceeab48832266d62e3daa87fd90b024"

@pytest.mark.skip(reason="This test deploys the smart contract and should not be run in a CI environment.")
class TestDeploySmartContract:
    def setup_method(self):
        self.w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
        with open('beaglegaze-python-sdk/contracts/UsageContract_sol_UsageContract.abi', 'r') as f:
            self.abi = json.load(f)
        with open('beaglegaze-python-sdk/contracts/UsageContract_sol_UsageContract.bin', 'r') as f:
            self.bytecode = f.read()
        self.subscription_price = 1000000000000000000  # 1 ETH in wei

    def test_setup_local_eth_node(self):
        self.deploy_smart_contract()
        self.fund_as_client()

    def deploy_smart_contract(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        account = self.w3.eth.account.from_key("0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

        tx_hash = contract.constructor().build_transaction({
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx_hash, private_key=account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        global SMART_CONTRACT_ADDRESS
        SMART_CONTRACT_ADDRESS = receipt.contractAddress
        print(f"Smart contract deployed at: {SMART_CONTRACT_ADDRESS}")

    def test_fund_address(self):
        account = self.w3.eth.account.from_key("0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        tx = {
            'to': "0x88f9B82462f6C4bf4a0Fb15e5c3971559a316e7f",
            'value': self.w3.to_wei(10000000, 'gwei'),
            'gas': 21000,
            'gasPrice': self.w3.to_wei('50', 'gwei'),
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'from': account.address
        }
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaction hash: {tx_hash.hex()}")

    def fund_as_client(self):
        client_account = self.w3.eth.account.from_key("0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        contract = self.w3.eth.contract(address=SMART_CONTRACT_ADDRESS, abi=self.abi)

        tx_hash = contract.functions.fund().build_transaction({
            'from': client_account.address,
            'nonce': self.w3.eth.get_transaction_count(client_account.address),
            'value': 2000
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx_hash, private_key=client_account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction hash: {receipt.transactionHash.hex()}")

    def test_get_client_funds(self):
        ethereum_testnet = EthereumTestnet("http://localhost:8545", "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        balance = ethereum_testnet.get_funds()
        print(f"Balance: {balance}")

    def test_get_smart_contract_client_funding(self):
        client_account = self.w3.eth.account.from_key("0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        contract = self.w3.eth.contract(address=SMART_CONTRACT_ADDRESS, abi=self.abi)
        balance = contract.functions.getClientFunding().call({'from': client_account.address})
        print(f"Client balance: {balance}")

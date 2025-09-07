import json
import threading
from web3 import Web3

class SmartContract:
    def __init__(self, contract_address, network_address, client_private_key, low_funding_threshold):
        self.w3 = Web3(Web3.HTTPProvider(network_address))
        self.client_account = self.w3.eth.account.from_key(client_private_key)
        self.contract_address = contract_address
        self.low_funding_threshold = low_funding_threshold
        self.transaction_lock = threading.Lock()

        with open('contracts/UsageContract_sol_UsageContract.abi', 'r') as f:
            abi = json.load(f)

        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)

    def consume(self, value):
        with self.transaction_lock:
            try:
                tx_hash = self.contract.functions.consume(value).build_transaction({
                    'from': self.client_account.address,
                    'nonce': self.w3.eth.get_transaction_count(self.client_account.address),
                })
                signed_tx = self.w3.eth.account.sign_transaction(tx_hash, private_key=self.client_account.key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                self._log_client_funding_if_low()
                return receipt.status == 1
            except Exception as e:
                print(f"Failed to consume from contract: {e}")
                raise RuntimeError("Failed to consume from contract") from e

    def _log_client_funding_if_low(self):
        client_funding = self.get_client_funding()
        if client_funding < self.low_funding_threshold:
            print("Client funding is low. Consider refunding to avoid interruptions.")

    def get_client_funding(self):
        try:
            return self.contract.functions.getClientFunding().call({'from': self.client_account.address})
        except Exception as e:
            print(f"Failed to get client funding: {e}")
            return 0

    def has_valid_subscription(self):
        try:
            return self.contract.functions.hasValidSubscription().call({'from': self.client_account.address})
        except Exception as e:
            print(f"Failed to check subscription status: {e}")
            return False

import json
import logging
from web3 import Web3

class EthereumTestnet:
    def __init__(self, url, private_key):
        self.ethereum_network_url = url
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(self.ethereum_network_url))
        self.account = self.w3.eth.account.from_key(private_key)

    def fund(self, amount, address):
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        abi_path = os.path.join(base_dir, 'contracts', 'UsageContract_sol_UsageContract.abi')
        with open(abi_path, 'r') as f:
            abi = json.load(f)
        contract = self.w3.eth.contract(address=address, abi=abi)
        tx_hash = contract.functions.fund().build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'value': amount
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx_hash, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        funding = contract.functions.getClientFunding().call({'from': self.account.address})
        logging.info(f"Client funding for address {self.account.address}: {funding}")

    def fund_as_client(self, private_key, address, amount):
        try:
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            abi_path = os.path.join(base_dir, 'contracts', 'UsageContract_sol_UsageContract.abi')
            
            with open(abi_path, 'r') as f:
                abi = json.load(f)

            client_account = self.w3.eth.account.from_key(private_key)
            contract = self.w3.eth.contract(address=address, abi=abi)

            tx_hash = contract.functions.fund().build_transaction({
                'from': client_account.address,
                'nonce': self.w3.eth.get_transaction_count(client_account.address),
                'value': amount
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx_hash, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logging.info(f"Client funding for address {client_account.address}: {amount}")
        except Exception as e:
            logging.error(f"Error funding client: {e}")

    def get_address(self):
        return self.account.address

    def get_funds(self):
        try:
            return self.w3.eth.get_balance(self.account.address)
        except Exception as e:
            logging.error(f"Error getting funds: {e}")
            return 0

from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
import requests
import time

class CustomEthereumTestnetContainer(DockerContainer):
    def __init__(self, image, **kwargs):
        super(CustomEthereumTestnetContainer, self).__init__(image, **kwargs)
        self.with_exposed_ports(8545)

    def get_network_address(self):
        host = self.get_container_host_ip()
        port = self.get_exposed_port(8545)
        return f"http://{host}:{port}"

    def wait_for_ready(self):
        # First wait for the logs to indicate Hardhat has started
        wait_for_logs(self, "Started HTTP and WebSocket JSON-RPC server at")
        
        # Then wait for the HTTP endpoint to be actually accessible
        network_address = self.get_network_address()
        
        for attempt in range(30):  # Try for 30 seconds
            try:
                response = requests.post(
                    network_address,
                    json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                    timeout=2
                )
                if response.status_code == 200:
                    break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                pass
            time.sleep(1)
        else:
            raise Exception(f"Hardhat testnet did not become ready at {network_address}")
        
        return self

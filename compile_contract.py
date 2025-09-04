import json
from solcx import compile_files, install_solc

# Install solc version 0.8.0
install_solc('0.8.0')

# Compile the contract
compiled_sol = compile_files(
    ['contracts/UsageContract.sol'],
    output_values=['abi', 'bin'],
    solc_version='0.8.0'
)

# Get the contract interface
contract_id, contract_interface = compiled_sol.popitem()

# Save ABI
with open('contracts/UsageContract_sol_UsageContract.abi', 'w') as f:
    json.dump(contract_interface['abi'], f)

# Save bytecode
with open('contracts/UsageContract_sol_UsageContract.bin', 'w') as f:
    f.write(contract_interface['bin'])

print("Contract compiled successfully. ABI and bytecode saved.")

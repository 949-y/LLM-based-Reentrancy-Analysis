import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_contract(file_path: str) -> str:
    full_path = (
        Path(file_path) if os.path.isabs(file_path) else BASE_DIR / file_path
    )
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def load_contracts_from_directory(directory: str) -> dict:
    contracts = {}
    full_dir = (
        Path(directory)
        if os.path.isabs(directory)
        else BASE_DIR / directory
    )
    for root, _dirs, files in os.walk(full_dir):
        for f in files:
            if f.endswith(".sol"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, full_dir)
                contracts[rel_path] = load_contract(full_path)
    return contracts


# Test contracts with ground-truth labels.
# "vulnerable" = True  → contract contains a known reentrancy bug.
# "vulnerable" = False → contract is the fixed (safe) version.
TEST_CONTRACTS = [
    {
        "name": "02_reentrancy/InsecureEtherVault",
        "path": "contracts/solidity-security-by-example/02_reentrancy/InsecureEtherVault.sol",
        "vulnerable": True,
        "description": "Basic reentrancy — no lock, CEI pattern violated",
        "category": "single",
    },
    {
        "name": "02_reentrancy/FixedEtherVault",
        "path": "contracts/solidity-security-by-example/02_reentrancy/FixedEtherVault.sol",
        "vulnerable": False,
        "description": "Fixed with ReentrancyGuard + CEI pattern",
        "category": "single",
    },
    {
        "name": "03_reentrancy_via_modifier/InsecureAirdrop",
        "path": "contracts/solidity-security-by-example/03_reentrancy_via_modifier/InsecureAirdrop.sol",
        "vulnerable": True,
        "description": "Reentrancy via incorrect modifier ordering",
        "category": "single",
    },
    {
        "name": "03_reentrancy_via_modifier/FixedAirdrop",
        "path": "contracts/solidity-security-by-example/03_reentrancy_via_modifier/FixedAirdrop.sol",
        "vulnerable": False,
        "description": "Fixed with correct modifier order + noReentrant",
        "category": "single",
    },
    {
        "name": "04_cross_function_reentrancy/InsecureEtherVault",
        "path": "contracts/solidity-security-by-example/04_cross_function_reentrancy/InsecureEtherVault.sol",
        "vulnerable": True,
        "description": "Cross-function reentrancy — transfer() lacks lock",
        "category": "single",
    },
    {
        "name": "04_cross_function_reentrancy/FixedEtherVault",
        "path": "contracts/solidity-security-by-example/04_cross_function_reentrancy/FixedEtherVault.sol",
        "vulnerable": False,
        "description": "Fixed — all state-modifying functions protected",
        "category": "single",
    },
    {
        "name": "05_cross_contract_reentrancy/InsecureMoonVault",
        "path": "contracts/solidity-security-by-example/05_cross_contract_reentrancy/InsecureMoonVault.sol",
        "vulnerable": True,
        "description": "Cross-contract reentrancy — burn after external call",
        "category": "multi",
    },
    {
        "name": "05_cross_contract_reentrancy/FixedMoonVault",
        "path": "contracts/solidity-security-by-example/05_cross_contract_reentrancy/FixedMoonVault.sol",
        "vulnerable": False,
        "description": "Fixed — burn before external call (CEI)",
        "category": "multi",
    },
]

# Etherscan mainnet contracts (for optional testing)
ETHERSCAN_CONTRACTS = [
    {
        "address": "0xf91546835f756DA0c10cFa0CDA95b15577b84aA7",
        "name": "LedgerChannel",
    },
    {
        "address": "0xbb9bc244d798123fde783fcc1c72d3bb8c189413",
        "name": "TheDAO",
    },
    {
        "address": "0x0eee3e3828a45f7601d5f54bf49bb01d1a9df5ea",
        "name": "MoneyMarket",
    },
]

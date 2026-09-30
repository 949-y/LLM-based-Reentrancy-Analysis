import re

try:
    import solcx
except ImportError:
    solcx = None

try:
    from slither import Slither
    SLITHER_AVAILABLE = True
except ImportError:
    SLITHER_AVAILABLE = False


def _get_solc_version(contract_path: str) -> str:
    """Extract the Solidity compiler version from the pragma directive."""
    with open(contract_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"pragma\s+solidity\s+([^;]+);", content)
    if not match:
        return "0.8.13"
    versions = re.findall(r"(\d+\.\d+\.\d+)", match.group(1))
    return versions[0] if versions else "0.8.13"


def _ensure_solc(version: str):
    """Install the required solc version and return its binary path."""
    if solcx is None:
        return None
    try:
        installed = [str(v) for v in solcx.get_installed_solc_versions()]
    except Exception:
        installed = []

    if version not in installed:
        try:
            print(f"  [Slither] Installing solc {version}...")
            solcx.install_solc(version)
        except Exception as e:
            print(f"  [Slither] Failed to install solc {version}: {e}")
            return None

    # Construct the solc binary path from the install folder.
    # py-solc-x stores binaries at: {install_folder}/solc-v{version}/solc[.exe]
    try:
        import os
        install_folder = solcx.get_solcx_install_folder()
        binary = "solc.exe" if os.name == "nt" else "solc"
        solc_path = os.path.join(
            install_folder, f"solc-v{version}", binary
        )
        if os.path.exists(solc_path):
            return solc_path
    except Exception:
        pass
    return None


def _safe_attr(obj, attr, default=None):
    """Safely get an attribute that may differ across Slither versions."""
    val = getattr(obj, attr, default)
    return val if val is not None else default


def analyze_contract(contract_path: str) -> str:
    """Run Slither on a contract and extract reentrancy-relevant static info.

    Returns a formatted text summary including:
    - Contract names and inheritance
    - State variables
    - Per-function: visibility, state vars read/written, modifiers, calls
    """
    if not SLITHER_AVAILABLE:
        return "[Slither not installed — run: pip install slither-analyzer py-solc-x]"

    version = _get_solc_version(contract_path)
    solc_path = _ensure_solc(version)

    try:
        if solc_path:
            slither = Slither(contract_path, solc=solc_path)
        else:
            slither = Slither(contract_path)
    except Exception as e:
        return f"[Slither analysis failed: {e}]"

    lines = []
    for contract in _safe_attr(slither, "contracts", []):
        lines.append(f"=== Contract: {contract.name} ===")

        inheritance = [c.name for c in _safe_attr(contract, "inheritance", [])]
        if inheritance:
            lines.append(f"Inherits: {', '.join(inheritance)}")

        state_vars = [
            v.name for v in _safe_attr(contract, "state_variables", [])
        ]
        if state_vars:
            lines.append(f"State variables: {', '.join(state_vars)}")

        lines.append("")

        for func in _safe_attr(contract, "functions", []):
            if not getattr(func, "implemented", True):
                continue

            lines.append(f"  Function: {func.name}")
            lines.append(
                f"    Visibility: {_safe_attr(func, 'visibility', 'unknown')}"
            )

            sv_read = [
                v.name for v in _safe_attr(func, "state_variables_read", [])
            ]
            sv_written = [
                v.name
                for v in _safe_attr(func, "state_variables_written", [])
            ]
            lines.append(f"    State vars read:    {sv_read}")
            lines.append(f"    State vars written: {sv_written}")

            modifiers_raw = _safe_attr(func, "modifiers", [])
            modifiers = [
                m.name if hasattr(m, "name") else str(m)
                for m in modifiers_raw
            ]
            lines.append(f"    Modifiers: {modifiers}")

            # Low-level calls: .call(), .send(), .transfer() — key reentrancy vectors
            ll_calls = _safe_attr(func, "low_level_calls", [])
            if ll_calls:
                ll_strs = []
                for c in ll_calls:
                    expr = getattr(c, "expression", None)
                    ll_strs.append(str(expr) if expr else str(c))
                lines.append(f"    Low-level calls: {ll_strs}")

            # High-level calls: external contract method calls
            hl_calls = _safe_attr(func, "high_level_calls", [])
            if hl_calls:
                hl_strs = []
                for c in hl_calls:
                    expr = getattr(c, "expression", None)
                    hl_strs.append(str(expr) if expr else str(c))
                lines.append(f"    High-level calls: {hl_strs}")

            # External call expressions
            ext_calls = _safe_attr(
                func, "external_calls_as_expressions", []
            )
            if ext_calls:
                lines.append(
                    f"    External calls: {[str(c) for c in ext_calls]}"
                )

            int_calls = _safe_attr(func, "internal_calls", [])
            if int_calls:
                lines.append(
                    f"    Internal calls: {[str(c) for c in int_calls]}"
                )

            lines.append("")

    return "\n".join(lines) if lines else "[No contracts found]"

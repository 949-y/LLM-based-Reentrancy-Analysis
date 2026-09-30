import re


def remove_comments(code: str) -> str:
    """Strip single-line and multi-line comments."""
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    code = re.sub(r"//.*?$", "", code, flags=re.MULTILINE)
    return code


def _find_function_end(lines: list, start_idx: int) -> int:
    """Return the index of the line containing the matching closing brace."""
    depth = 0
    found_brace = False
    for i in range(start_idx, len(lines)):
        for char in lines[i]:
            if char == "{":
                depth += 1
                found_brace = True
            elif char == "}":
                depth -= 1
                if found_brace and depth == 0:
                    return i
    return len(lines) - 1


def _is_view_or_pure(text: str) -> bool:
    return bool(re.search(r"\b(view|pure)\b", text))


def _has_external_call(lines: list, start: int, end: int) -> bool:
    """Check whether the function makes any external call."""
    text = "\n".join(lines[start : end + 1])
    builtin_objects = {
        "msg", "block", "tx", "address", "this", "type",
        "abi", "require", "assert", "revert", "keccak256",
    }
    # Low-level Ether transfer
    if re.search(r"\.(call|transfer|send)\s*[\{(]", text):
        return True
    # External contract method calls
    for obj, _method in re.findall(r"(\w+)\.(\w+)\s*\(", text):
        if obj not in builtin_objects:
            return True
    return False


def _is_getter_only(lines: list, start: int, end: int) -> bool:
    """A function is 'getter-only' if it's view/pure AND has no external calls."""
    header = " ".join(lines[start : min(start + 3, end + 1)])
    if not _is_view_or_pure(header):
        return False
    return not _has_external_call(lines, start, end)


def trim_contract(code: str) -> str:
    """Trim a Solidity source file to reentrancy-relevant parts.

    Removes comments, blank lines, and view/pure getter functions
    that do not make external calls — these are irrelevant to
    reentrancy analysis and only add noise for the LLM.
    """
    code = remove_comments(code)
    lines = code.split("\n")
    skip = set()

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if re.match(r"function\s+\w+", stripped):
            end_idx = _find_function_end(lines, i)
            if _is_getter_only(lines, i, end_idx):
                skip.update(range(i, end_idx + 1))
            i = end_idx + 1
        else:
            i += 1

    result = "\n".join(
        line for idx, line in enumerate(lines) if idx not in skip
    )
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()

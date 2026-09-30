import json
import re
import time

from src.llm_client import LLMClient
from src.contract_loader import load_contract, TEST_CONTRACTS, BASE_DIR
from src.code_trimmer import trim_contract
from src.slither_analyzer import analyze_contract as slither_analyze
from src.prompts import (
    BASELINE_SYSTEM,
    BASELINE_USER_TEMPLATE,
    TRIMMED_SYSTEM,
    TRIMMED_USER_TEMPLATE,
    SLITHER_SYSTEM,
    SLITHER_USER_TEMPLATE,
    ENGINEERED_SYSTEM,
    ENGINEERED_USER_TEMPLATE,
)

RESULTS_DIR = BASE_DIR / "results"


def save_result(contract_name, approach, response, elapsed, ground_truth):
    RESULTS_DIR.mkdir(exist_ok=True)
    output = {
        "contract": contract_name,
        "approach": approach,
        "ground_truth_vulnerable": ground_truth,
        "response": response,
        "elapsed_seconds": round(elapsed, 2),
    }
    filename = f"{contract_name.replace('/', '_')}__{approach}.json"
    with open(RESULTS_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


def parse_verdict(response_text):
    """Extract the LLM's verdict (True/False/None) from its response."""
    # Try JSON parsing (prompt_engineered approach)
    text = response_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        data = json.loads(text)
        return data.get("vulnerable")
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback: keyword matching
    lower = response_text.lower()
    if any(
        kw in lower
        for kw in [
            "not vulnerable",
            "no reentrancy",
            "is not vulnerable",
            "not vulnerable to reentrancy",
            "no reentrancy vulnerability",
        ]
    ):
        return False
    if "vulnerable" in lower:
        return True
    return None


def run_one(client, approach_name, system_prompt, user_prompt, contract):
    name = contract["name"]
    ground_truth = contract["vulnerable"]
    print(f"  [{approach_name}] Analyzing {name} ...", end=" ", flush=True)
    start = time.time()
    try:
        response = client.analyze(system_prompt, user_prompt)
    except Exception as e:
        response = f"[ERROR] {e}"
    elapsed = time.time() - start
    save_result(name, approach_name, response, elapsed, ground_truth)
    verdict = parse_verdict(response)
    correct = verdict == ground_truth if verdict is not None else "?"
    symbol = "Y" if correct is True else "N" if correct is False else "?"
    print(f"done ({elapsed:.1f}s) verdict={'VULN' if verdict else 'SAFE'} [{symbol}]")


def main():
    print("=" * 70)
    print("  LLM-based Reentrancy Analysis")
    print("  Model: Zhipu AI (GLM-4-Flash)")
    print("=" * 70)

    client = LLMClient()
    print(f"  Model: {client.model}")
    print(f"  Test contracts: {len(TEST_CONTRACTS)}")
    print()

    for contract in TEST_CONTRACTS:
        name = contract["name"]
        path = contract["path"]
        vulnerable = contract["vulnerable"]
        desc = contract["description"]

        print(f"\n{'=' * 70}")
        print(f"  Contract : {name}")
        print(f"  Truth    : {'VULNERABLE' if vulnerable else 'SAFE'}")
        print(f"  Desc     : {desc}")
        print(f"{'=' * 70}")

        code = load_contract(path)

        # Approach 1 — Baseline
        user_prompt = BASELINE_USER_TEMPLATE.format(code=code)
        run_one(client, "baseline", BASELINE_SYSTEM, user_prompt, contract)

        # Approach 2 — Code Trimming
        trimmed = trim_contract(code)
        user_prompt = TRIMMED_USER_TEMPLATE.format(trimmed_code=trimmed)
        run_one(client, "code_trimming", TRIMMED_SYSTEM, user_prompt, contract)

        # Approach 3 — Slither-Assisted
        full_path = str(BASE_DIR / path)
        slither_info = slither_analyze(full_path)
        user_prompt = SLITHER_USER_TEMPLATE.format(
            code=code, slither_info=slither_info
        )
        run_one(
            client, "slither_assisted", SLITHER_SYSTEM, user_prompt, contract
        )

        # Approach 4 — Prompt Engineering
        user_prompt = ENGINEERED_USER_TEMPLATE.format(code=code)
        run_one(
            client,
            "prompt_engineered",
            ENGINEERED_SYSTEM,
            user_prompt,
            contract,
        )

    print("\n" + "=" * 70)
    print("  All analyses complete! Results saved to results/")
    print("=" * 70)


if __name__ == "__main__":
    main()

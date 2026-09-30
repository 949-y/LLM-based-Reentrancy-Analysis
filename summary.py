"""Generate a summary comparison table from the analysis results."""

import json
import os
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"

APPROACHES = ["baseline", "code_trimming", "slither_assisted", "prompt_engineered"]


def load_results():
    results = {}
    for fname in os.listdir(RESULTS_DIR):
        if not fname.endswith(".json"):
            continue
        with open(RESULTS_DIR / fname, "r", encoding="utf-8") as f:
            data = json.load(f)
        key = (data["contract"], data["approach"])
        results[key] = data
    return results


def parse_verdict(response_text):
    """Extract the LLM's verdict from the response text."""
    import re

    text = response_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        data = json.loads(text)
        return data.get("vulnerable")
    except (json.JSONDecodeError, TypeError):
        pass

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


def main():
    results = load_results()

    # Collect all contract names
    contracts = sorted({k[0] for k in results.keys()})

    print("=" * 90)
    print("  Reentrancy Analysis — Summary Comparison")
    print("=" * 90)
    print()

    # Header
    header = f"{'Contract':<45} {'Truth':<12}"
    for ap in APPROACHES:
        header += f"{ap:<18}"
    print(header)
    print("-" * 90)

    stats = {ap: {"correct": 0, "wrong": 0, "unknown": 0} for ap in APPROACHES}

    for contract in contracts:
        truth = None
        for ap in APPROACHES:
            data = results.get((contract, ap))
            if data:
                truth = data["ground_truth_vulnerable"]
                break

        row = f"{contract:<45} {'VULN' if truth else 'SAFE':<12}"
        for ap in APPROACHES:
            data = results.get((contract, ap))
            if not data:
                row += f"{'?':<18}"
                continue
            verdict = parse_verdict(data["response"])
            if verdict is None:
                row += f"{'?':<18}"
                stats[ap]["unknown"] += 1
            elif verdict == truth:
                row += f"{'✓ ' + ('VULN' if verdict else 'SAFE'):<18}"
                stats[ap]["correct"] += 1
            else:
                row += f"{'✗ ' + ('VULN' if verdict else 'SAFE'):<18}"
                stats[ap]["wrong"] += 1
        print(row)

    print("-" * 90)
    print()

    # Accuracy
    print("  Accuracy:")
    for ap in APPROACHES:
        s = stats[ap]
        total = s["correct"] + s["wrong"] + s["unknown"]
        acc = s["correct"] / total * 100 if total > 0 else 0
        print(
            f"    {ap:<20} {s['correct']}/{total} correct ({acc:.1f}%)  "
            f"wrong={s['wrong']}  unknown={s['unknown']}"
        )
    print()

    # Elapsed time
    print("  Average response time:")
    for ap in APPROACHES:
        times = [
            results[(c, ap)]["elapsed_seconds"]
            for c in contracts
            if (c, ap) in results
        ]
        if times:
            avg = sum(times) / len(times)
            print(f"    {ap:<20} {avg:.1f}s")
    print()
    print("=" * 90)


if __name__ == "__main__":
    main()

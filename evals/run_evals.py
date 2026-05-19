"""
Eval harness for Meridian Sales Intelligence Agent.
Runs golden Q&A pairs against the deployed Cortex Agent and scores each assertion.

Usage:
    python evals/run_evals.py                  # run all evals
    python evals/run_evals.py --id eval_01     # run single eval
    python evals/run_evals.py --category trust_rule  # run by category
"""

import json
import os
import re
import sys
import argparse
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

AGENT_FQN = "MERIDIAN_SALES.GOLD.MERIDIAN_SALES_AGENT"
EVALS_FILE = Path(__file__).parent / "golden_qa.json"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        authenticator=os.environ.get("SNOWFLAKE_AUTHENTICATOR", "externalbrowser"),
        role=os.environ.get("SNOWFLAKE_ROLE", "MERIDIAN_ENGINEER"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "MERIDIAN_SALES"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "GOLD"),
    )


def call_agent(cursor, question: str) -> dict:
    """Call the Cortex Agent and return parsed answer text and source SQL."""
    payload = json.dumps({
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": question}]}
        ]
    })
    cursor.execute(
        f"SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN('{AGENT_FQN}', %s)",
        (payload,)
    )
    raw = cursor.fetchone()[0]
    response = json.loads(raw)

    answer_text = ""
    source_sql = ""

    if "content" in response:
        for block in response["content"]:
            block_type = block.get("type", "")
            if block_type == "text":
                answer_text += block.get("text", "")
            elif block_type == "tool_result":
                content_list = block.get("content", [])
                for item in content_list:
                    if isinstance(item, dict) and item.get("type") == "json":
                        json_data = item.get("json", {})
                        if "sql" in json_data and ("result_set" in json_data or "query_id" in json_data):
                            source_sql = json_data["sql"]
    elif "message" in response:
        answer_text = response["message"]

    return {"answer": answer_text, "sql": source_sql}


def extract_sections(text: str) -> dict:
    """Parse ANSWER / DATA / FLAG sections from agent response."""
    sections = {"answer": "", "data": "", "flag": "", "full": text}
    lower = text.lower()

    answer_pos = lower.find("answer:")
    data_pos = lower.find("data:")
    flag_pos = lower.find("flag:")

    if answer_pos != -1:
        end = data_pos if data_pos != -1 else (flag_pos if flag_pos != -1 else len(text))
        sections["answer"] = text[answer_pos + 7:end].strip()

    if data_pos != -1:
        end = flag_pos if flag_pos != -1 else len(text)
        sections["data"] = text[data_pos + 5:end].strip()

    if flag_pos != -1:
        sections["flag"] = text[flag_pos + 5:].strip()

    return sections


def run_assertions(sections: dict, assertions: dict) -> list:
    """Run all assertions against the parsed response. Returns list of (name, passed, detail)."""
    results = []
    full_lower = sections["full"].lower()

    # expected_contains
    for term in assertions.get("expected_contains", []):
        found = term.lower() in full_lower
        results.append((
            f"contains '{term}'",
            found,
            "found in response" if found else f"'{term}' not found in response"
        ))

    # must_not_contain
    for term in assertions.get("must_not_contain", []):
        found = term.lower() in full_lower
        results.append((
            f"does not contain '{term}'",
            not found,
            "correctly absent" if not found else f"'{term}' incorrectly appeared in response"
        ))

    # must_flag
    must_flag = assertions.get("must_flag")
    if must_flag:
        flag_text = (sections["flag"] + sections["full"]).lower()
        found = must_flag.lower() in flag_text
        results.append((
            f"flags '{must_flag}'",
            found,
            "flag present" if found else f"'{must_flag}' not flagged in response"
        ))

    # must_lead_with_coverage
    if assertions.get("must_lead_with_coverage"):
        answer_section = sections["answer"].lower() or full_lower
        cov_pos = answer_section.find("quota coverage")
        att_pos = answer_section.find("attainment")
        if cov_pos == -1:
            passed = False
            detail = "quota coverage not mentioned in answer section"
        elif att_pos == -1:
            passed = True
            detail = "leads with quota coverage (attainment not mentioned)"
        else:
            passed = cov_pos < att_pos
            detail = "quota coverage appears before attainment" if passed else "attainment appears before quota coverage — trust rule violation"
        results.append(("leads with quota coverage", passed, detail))

    # sql_grounded: agent must have produced SQL
    # (soft check — warn only)
    return results


def score_eval(eval_case: dict, response: dict) -> dict:
    sections = extract_sections(response["answer"])
    assertion_results = run_assertions(sections, eval_case["assertions"])

    passed = sum(1 for _, p, _ in assertion_results if p)
    total = len(assertion_results)
    all_passed = passed == total

    return {
        "id": eval_case["id"],
        "question": eval_case["question"],
        "category": eval_case["category"],
        "rationale": eval_case["rationale"],
        "passed": all_passed,
        "score": f"{passed}/{total}",
        "assertion_results": assertion_results,
        "response_text": response["answer"],
        "source_sql": response["sql"],
    }


def print_result(result: dict):
    status = f"{GREEN}{BOLD}PASS{RESET}" if result["passed"] else f"{RED}{BOLD}FAIL{RESET}"
    print(f"\n{'='*70}")
    print(f"{BOLD}{result['id']}{RESET}  [{result['category']}]  {status}  ({result['score']})")
    print(f"{CYAN}Q: {result['question']}{RESET}")
    print(f"   {result['rationale']}")
    print()

    for name, passed, detail in result["assertion_results"]:
        icon = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"  {icon}  {name}")
        if not passed:
            print(f"     {YELLOW}→ {detail}{RESET}")

    if not result["passed"]:
        print(f"\n  {BOLD}Agent response:{RESET}")
        for line in result["response_text"].strip().splitlines():
            print(f"    {line}")
        if result["source_sql"]:
            print(f"\n  {BOLD}Source SQL:{RESET}")
            for line in result["source_sql"].strip().splitlines():
                print(f"    {line}")


def print_summary(results: list):
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    print(f"\n{'='*70}")
    print(f"{BOLD}EVAL SUMMARY{RESET}")
    print(f"{'='*70}")
    print(f"Total:  {total}")
    print(f"Passed: {GREEN}{passed}{RESET}")
    print(f"Failed: {RED}{total - passed}{RESET}")
    print()

    by_category: dict = {}
    for r in results:
        cat = r["category"]
        by_category.setdefault(cat, {"passed": 0, "total": 0})
        by_category[cat]["total"] += 1
        if r["passed"]:
            by_category[cat]["passed"] += 1

    print(f"{BOLD}By category:{RESET}")
    for cat, counts in sorted(by_category.items()):
        bar = f"{GREEN}✓{RESET}" if counts["passed"] == counts["total"] else f"{RED}✗{RESET}"
        print(f"  {bar}  {cat:<20} {counts['passed']}/{counts['total']}")

    failed = [r for r in results if not r["passed"]]
    if failed:
        print(f"\n{BOLD}Failed evals:{RESET}")
        for r in failed:
            print(f"  {RED}✗{RESET}  {r['id']} — {r['question'][:60]}...")

    print()
    if passed == total:
        print(f"{GREEN}{BOLD}All evals passed.{RESET}")
    else:
        print(f"{YELLOW}Fix failing evals before presenting.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Run Meridian eval harness")
    parser.add_argument("--id", help="Run a single eval by ID (e.g. eval_01)")
    parser.add_argument("--category", help="Run evals by category (trust_rule, business_rule, key_number)")
    args = parser.parse_args()

    with open(EVALS_FILE) as f:
        all_evals = json.load(f)

    if args.id:
        evals = [e for e in all_evals if e["id"] == args.id]
        if not evals:
            print(f"Eval '{args.id}' not found.")
            sys.exit(1)
    elif args.category:
        evals = [e for e in all_evals if e["category"] == args.category]
        if not evals:
            print(f"No evals found for category '{args.category}'.")
            sys.exit(1)
    else:
        evals = all_evals

    print(f"{BOLD}Meridian Sales Intelligence — Eval Harness{RESET}")
    print(f"Running {len(evals)} eval(s) against {AGENT_FQN}")
    print(f"{'='*70}")

    conn = get_connection()
    cursor = conn.cursor()

    results = []
    for i, eval_case in enumerate(evals, 1):
        print(f"\n[{i}/{len(evals)}] {eval_case['id']}: {eval_case['question'][:60]}...", end="", flush=True)
        response = call_agent(cursor, eval_case["question"])
        result = score_eval(eval_case, response)
        results.append(result)
        status = f"{GREEN}PASS{RESET}" if result["passed"] else f"{RED}FAIL{RESET}"
        print(f" {status}")

    cursor.close()
    conn.close()

    for result in results:
        print_result(result)

    print_summary(results)

    failed_count = sum(1 for r in results if not r["passed"])
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()

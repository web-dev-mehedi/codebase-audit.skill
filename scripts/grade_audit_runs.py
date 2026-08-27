"""
Grade eval runs for the codebase-audit skill.

For each eval (with_skill and without_skill), reads the report.md and the
fixed source file, checks each assertion in eval_metadata.json, and writes
grading.json with the results.

Grading is heuristic — checks for keyword/phrase presence and structural
elements. The output format matches what generate_review.py expects:
{ expectations: [{ text, passed, evidence }] }
"""

import json
import re
from pathlib import Path

WORKSPACE = Path("/home/z/my-project/skills/codebase-audit-workspace/iteration-1")
EVALS = [
    ("eval-1-react-state-race-condition", ["with_skill", "without_skill"]),
    ("eval-2-node-api-errors",            ["with_skill", "without_skill"]),
    ("eval-3-python-pipeline",             ["with_skill", "without_skill"]),
]


def find_files(run_dir):
    outputs = run_dir / "outputs"
    report = outputs / "report.md"
    fixed_files = list(outputs.glob("*.fixed"))
    return report, fixed_files


def read_report(run_dir):
    report, _ = find_files(run_dir)
    if not report.exists():
        return ""
    return report.read_text()


def read_fixed_source(run_dir):
    _, fixed_files = find_files(run_dir)
    if not fixed_files:
        return ""
    return fixed_files[0].read_text()


def has_pattern(text, patterns):
    text_lower = text.lower()
    for p in patterns:
        if p.lower() in text_lower:
            return True, f"matched: '{p}'"
    return False, "no matching pattern found"


def grade_eval_1(report, fixed):
    results = []
    p, e = has_pattern(report, ["abortcontroller", "abort(", "request cancellation", "no cancellation"])
    results.append({"text": "Identifies missing AbortController + cleanup as race condition (BUG 1)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["debounce", "no debounce", "missing debounce"])
    results.append({"text": "Identifies missing debounce on search input (BUG 2)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["stale closure", "stale-closure", "captur", "itemsref", "useRef"])
    results.append({"text": "Identifies stale closure in setTimeout capturing old items (BUG 3)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["mutat", "immutab", "spread", "results.push"])
    results.append({"text": "Identifies direct mutation of searchResults array (BUG 4)", "passed": p, "evidence": e})
    p1, e1 = has_pattern(report, ["dependency array", "dep array", "dependencies", "useeffect", "dependency"])
    p2, e2 = has_pattern(report, ["selectedid"])
    results.append({"text": "Identifies missing selectedId in useEffect dep array (BUG 5)", "passed": p1 and p2, "evidence": f"deps mention: {e1}; selectedId mention: {e2}"})
    p1, e1 = has_pattern(report, ["json.parse", "try/catch", "try catch", "localstorage"])
    p2, e2 = has_pattern(report, ["try", "catch", "guard"])
    results.append({"text": "Identifies localStorage JSON.parse without try/catch (BUG 6)", "passed": p1 and p2, "evidence": e1 + " | " + e2})
    p, e = has_pattern(report, ["error ui", "error state", "spinner", "loading", "no error", "missing error", "error handling"])
    results.append({"text": "Identifies missing error UI / infinite spinner on fetch failure (BUG 7)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["root cause"])
    results.append({"text": "Applies fixes at root cause, not symptom patches", "passed": p, "evidence": e})
    p1, _ = has_pattern(report, ["executive summary"])
    p2, _ = has_pattern(report, ["severity"])
    p3, _ = has_pattern(report, ["regression"])
    p4, _ = has_pattern(report, ["validation"])
    p5, _ = has_pattern(report, ["p0", "p1", "p2", "p3"])
    results.append({"text": "Delivers structured report with BUG-001 format, severity tags, validation status", "passed": p1 and p2 and p3 and p4 and p5, "evidence": f"exec_summary={p1}, severity={p2}, regression={p3}, validation={p4}, P0-P3={p5}"})
    p = "Dashboard" in fixed and "Sidebar" in fixed and "SearchBox" in fixed and "Spinner" in fixed
    results.append({"text": "Does NOT rewrite the entire file unnecessarily", "passed": p, "evidence": "all original component names still present" if p else "component names missing — possible rewrite"})
    return results


def grade_eval_2(report, fixed):
    results = []
    p, e = has_pattern(report, ["sql injection", "injection", "string concatenation", "parameterized", "concat"])
    results.append({"text": "Identifies SQL injection in getUserByEmail via string concatenation (BUG 1)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["try/catch", "try catch", "unhandled", "async", "asyncaandler", "asynchandler", "wrapper"])
    results.append({"text": "Identifies missing try/catch in async route handlers (BUG 2)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["error middleware", "error-handling middleware", "error handling middleware", "global error"])
    results.append({"text": "Identifies missing global error-handling middleware (BUG 3)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["mass assignment", "mass-assignment", "allowlist", "whitelist", "role:admin", "role: 'admin'", "role=admin"])
    results.append({"text": "Identifies mass assignment allowing role:admin (BUG 4)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["idor", "ownership", "insecure direct", "ownership check"])
    results.append({"text": "Identifies IDOR — no ownership check (BUG 5)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["validation", "input validation", "validate"])
    results.append({"text": "Identifies missing input validation on /login (BUG 6)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["rate limit", "rate-limit", "ratelimit", "brute force"])
    results.append({"text": "Identifies missing rate limiting on /login (BUG 7)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["jwt secret", "hardcoded", "hard-coded", "weak secret"])
    results.append({"text": "Identifies hardcoded weak JWT secret (BUG 8)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["reset", "expir", "expiresin", "expires_in"])
    results.append({"text": "Identifies password reset token never expires (BUG 9)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["connection leak", "leak", "release", "getconnection", "finally"])
    results.append({"text": "Identifies connection leak in /api/orders error path (BUG 10)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["root cause"])
    results.append({"text": "Applies fixes at root cause", "passed": p, "evidence": e})
    p1, _ = has_pattern(report, ["executive summary"])
    p2, _ = has_pattern(report, ["severity"])
    p3, _ = has_pattern(report, ["regression"])
    p4, _ = has_pattern(report, ["validation"])
    p5, _ = has_pattern(report, ["p0", "p1", "p2", "p3"])
    results.append({"text": "Delivers structured report with BUG-001 format, severity tags, validation status", "passed": p1 and p2 and p3 and p4 and p5, "evidence": f"exec_summary={p1}, severity={p2}, regression={p3}, validation={p4}, P0-P3={p5}"})
    return results


def grade_eval_3(report, fixed):
    results = []
    p, e = has_pattern(report, ["nonetype", "none type", "none", "validate_row", "returns none", "return none"])
    results.append({"text": "Identifies NoneType access when validate_row returns None (BUG 1)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["upsert", "on conflict", "unique constraint", "duplicate", "idempotent"])
    results.append({"text": "Identifies missing upsert/unique constraint causing duplicate inserts (BUG 2)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["transaction", "commit", "rollback", "atomic"])
    results.append({"text": "Identifies missing transaction around inserts (BUG 3)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["bom", "encoding", "utf-8-sig", "empty row", "header validation"])
    results.append({"text": "Identifies CSV edge cases: BOM, empty rows, header validation (BUG 4)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["sql injection", "f-string", "f string", "parameterized", "injection"])
    results.append({"text": "Identifies SQL injection via f-string in get_user_by_email (BUG 5)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["connection", "finally", "close", "leak", "cleanup"])
    results.append({"text": "Identifies missing connection cleanup on exception (BUG 6)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["bare except", "swallow", "except exception", "except:", "silent"])
    results.append({"text": "Identifies bare except swallowing errors (BUG 9)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["decimal", "float", "monetary", "money"])
    results.append({"text": "Identifies float used for monetary amount (BUG 8)", "passed": p, "evidence": e})
    p, e = has_pattern(report, ["root cause"])
    results.append({"text": "Applies fixes at root cause", "passed": p, "evidence": e})
    p1, _ = has_pattern(report, ["executive summary"])
    p2, _ = has_pattern(report, ["severity"])
    p3, _ = has_pattern(report, ["regression"])
    p4, _ = has_pattern(report, ["validation"])
    p5, _ = has_pattern(report, ["p0", "p1", "p2", "p3"])
    results.append({"text": "Delivers structured report with BUG-001 format, severity tags, validation status", "passed": p1 and p2 and p3 and p4 and p5, "evidence": f"exec_summary={p1}, severity={p2}, regression={p3}, validation={p4}, P0-P3={p5}"})
    return results


GRADERS = {
    "eval-1-react-state-race-condition": grade_eval_1,
    "eval-2-node-api-errors":            grade_eval_2,
    "eval-3-python-pipeline":            grade_eval_3,
}


def main():
    for eval_name, configs in EVALS:
        for config in configs:
            run_dir = WORKSPACE / eval_name / config
            report = read_report(run_dir)
            fixed = read_fixed_source(run_dir)
            if not report:
                print(f"  [WARN] no report.md for {eval_name}/{config}")
                continue
            grader = GRADERS[eval_name]
            expectations = grader(report, fixed)
            passed = sum(1 for e in expectations if e["passed"])
            total = len(expectations)
            grading = {"expectations": expectations, "passed": passed, "total": total, "pass_rate": passed / total if total else 0}
            out = run_dir / "grading.json"
            out.write_text(json.dumps(grading, indent=2))
            print(f"  {eval_name}/{config}: {passed}/{total} ({passed/total*100:.0f}%)")


if __name__ == "__main__":
    main()

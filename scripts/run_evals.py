#!/usr/bin/env python3
"""
Re-run all evals for the codebase-audit skill.

This is a thin orchestrator that:
  1. Spawns parallel subagents (with-skill + baseline) against each fixture
  2. Grades the outputs
  3. Aggregates into a benchmark

Usage:
    python scripts/run_evals.py

Prerequisites:
    - The skill-creator package available at skills/skill-creator/
    - GLM CLI (for spawning subagents) — or run from inside a GLM session

Note: This script is a placeholder. The full eval pipeline lives in the
parent skill-creator workflow. See evals/evals.json for the test prompts
and assertions, and grade_audit_runs.py for the grading logic.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
EVALS_FILE = REPO_ROOT / "evals" / "evals.json"
FIXTURES_DIR = REPO_ROOT / "assets"


def main():
    if not EVALS_FILE.exists():
        print(f"[ERR] evals.json not found at {EVALS_FILE}")
        sys.exit(1)

    evals = json.loads(EVALS_FILE.read_text())
    print(f"Found {len(evals['evals'])} eval cases.")
    print()
    print("To run the full eval pipeline, you have two options:")
    print()
    print("  1. From a GLM session with skill-creator access:")
    print("     Ask: 'run the codebase-audit evals'")
    print()
    print("  2. Manually spawn subagents:")
    print("     For each eval, spawn two subagents — one with SKILL.md in")
    print("     context, one without — give them the eval prompt, and")
    print("     point them at the matching fixture in assets/. Then run:")
    print("       python scripts/grade_audit_runs.py")
    print()
    print("Eval cases:")
    for e in evals["evals"]:
        print(f"  - eval-{e['id']}: {e['name']}")
        print(f"    prompt: {e['prompt'][:100]}...")


if __name__ == "__main__":
    main()

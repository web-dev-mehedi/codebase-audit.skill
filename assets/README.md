# Test fixtures

These are tiny, intentionally-buggy codebases used to evaluate the skill. Each fixture has planted bugs across the categories the skill is supposed to find.

## Fixtures

| Fixture | Stack | Planted Bugs | Symptoms (what the user reports) |
|---------|-------|--------------|----------------------------------|
| `test-fixture-react/` | React + TypeScript | 7 | "Page crashes with 'Cannot read property map of undefined' when clicking sidebar items quickly. Search shows results for previous query." |
| `test-fixture-node/` | Node.js + Express + MySQL | 10 | "API crashes in production with unhandled promise rejections. Possible SQL injection." |
| `test-fixture-python/` | Python + psycopg2 + CSV | 9 | "Pipeline occasionally fails with 'NoneType has no attribute X'. Inserted duplicate records last week." |

## Reading the fixtures

Each fixture file has a comment block at the top listing every planted bug with a number (BUG 1, BUG 2, etc.). The grader script (`scripts/grade_audit_runs.py`) checks whether the audit report mentions each bug.

## Using them locally

To audit one of these fixtures yourself:

```bash
# Tell GLM:
# "Audit /home/z/my-project/skills/codebase-audit/assets/test-fixture-react/myapp/src/components/Dashboard.tsx"
```

The skill should fire, perform the audit, fix the file in place, and produce a structured report.

## Adding a new fixture

See [CONTRIBUTING.md](../../CONTRIBUTING.md) → "Adding a new test fixture".

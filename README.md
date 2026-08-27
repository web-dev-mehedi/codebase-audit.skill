<div align="center">

# codebase-audit

**A GLM skill that turns the model into a Senior Software Engineer —
performing deep, systematic audits of an entire codebase to find bugs,
race conditions, security holes, and edge-case failures, then fixing
them safely at the root cause.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GLM Skill](https://img.shields.io/badge/GLM-Skill-blueviolet)](https://github.com/zai-org/glm-skills)
[![Pass Rate](https://img.shields.io/badge/pass%20rate-100%25-brightgreen)](#benchmark-results)
[![Languages](https://img.shields.io/badge/coverage-React%20%7C%20Node%20%7C%20Python-blue)](#test-fixtures)

</div>

---

## Why this skill exists

> *"If I fix this line, what else could break?"*

Most AI-assisted code fixes stop at the first error and call it done. This
skill doesn't. It treats the codebase as a production system, walks a
6-phase senior-engineer methodology, and only stops when **every critical
and high-priority issue is fixed at the root cause** — not patched at the
symptom.

It does what a careful senior engineer would do if they had unlimited time
and full context of your codebase:

1. Understand the whole system before touching anything
2. Hunt systematically across 8 bug categories
3. Trace each bug to its root cause
4. Apply the smallest safe change
5. Check for regressions
6. Validate with the project's actual tooling

Then it hands you a structured engineering report you can read in 60 seconds.

---

## Table of contents

- [Quick start](#quick-start)
- [What it does](#what-it-does)
- [When it triggers](#when-it-triggers)
- [Sample report](#sample-report)
- [Skill structure](#skill-structure)
- [Test fixtures](#test-fixtures)
- [Benchmark results](#benchmark-results)
- [Re-running the evals](#re-running-the-evals)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Publishing to GitHub](#publishing-to-github)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Quick start

### Install the packaged `.skill` file

```bash
# Download codebase-audit.skill from the Releases page, then:
glm skills install codebase-audit.skill
```

### Or clone the repo

```bash
git clone https://github.com/<YOUR-USERNAME>/codebase-audit.git
cd codebase-audit
glm skills install .
```

### Use it

Just talk to GLM naturally — the skill triggers automatically:

```
> My React dashboard crashes when users click sidebar items quickly.
  Sometimes the search box shows results for the previous query.
  Can you audit and fix?
```

GLM will:

1. Read `SKILL.md` and follow the 6-phase methodology
2. Map your codebase (structure, entry points, data flow, critical paths)
3. Identify all bugs — not just the obvious ones
4. Apply root-cause fixes (smallest safe change, preserves existing behavior)
5. Run available validators (lint, typecheck, tests, build)
6. Deliver a structured engineering report

No special syntax, no commands to remember. If your message implies "audit
this", the skill fires.

---

## What it does

### The 6-phase methodology

| Phase | What happens |
|-------|--------------|
| **1. Discovery** | Map structure, entry points, data flow, critical paths, dependencies, single points of failure. No edits yet. |
| **2. Bug Hunt** | Walk 8 categories: runtime errors, logic bugs, state management, async/concurrency, API mismatches, database integrity, auth/authorization, edge cases. |
| **3. Root Cause** | For every bug, distinguish symptom vs. immediate cause vs. root cause. Fix the root cause. |
| **4. Safe Fix** | Smallest safe change. Preserve existing functionality. Follow existing architecture. Reuse existing utilities. |
| **5. Regression** | What depended on the old behavior? Could the fix break another component, stored data, or API contract? |
| **6. Validation** | Run lint, typecheck, tests, build. If a tool isn't installed, mark it `NOT AVAILABLE` — never guess. |

### Severity classification

| Severity | Meaning | Examples |
|----------|---------|----------|
| **P0 — Critical** | Fix immediately | App crash, data loss, security vulnerability, auth bypass, corrupted DB |
| **P1 — High** | Fix before minor improvements | Major feature broken, frequent runtime errors, serious data inconsistency |
| **P2 — Medium** | Fix when safe | Edge-case failures, incorrect UI state, occasional errors, perf issues |
| **P3 — Low** | Report separately | Minor code issues, small UX inconsistencies, non-critical optimizations |

---

## When it triggers

The skill activates on any request that implies deep code inspection and fix.
Some example triggers:

- "audit my codebase"
- "find bugs in my code"
- "review this project"
- "why is X broken in production"
- "check for race conditions"
- "hardening pass"
- "production readiness review"
- "it works on my machine but..."
- "fix flaky behavior"
- "scan for security issues"

The trigger description in `SKILL.md` is intentionally broad so the skill
fires even when the user doesn't explicitly say "audit".

---

## Sample report

Every audit ends with a report in this exact format:

````markdown
# Engineering Report — Dashboard.tsx Audit

## 1. Executive Summary

```text
Codebase Health: Poor (before) → Good (after)

Issues Found:     12
Issues Fixed:     12
Critical Issues:  3   (P0)
High Priority:    3   (P1)
Medium Priority:  4   (P2)
Low Priority:     2   (P3)
Remaining Issues: 0
```

## 2. Issues Found

### BUG-001 — Race condition in data-fetch effect (no cancellation, no cleanup)

```
ID: BUG-001
Severity: P0
Location: src/components/Dashboard.tsx → Dashboard → data useEffect
Problem:
  The effect that fetches `/items/${selectedId}` created a fetch on every
  render cycle but had an empty dependency array AND no AbortController and
  no cleanup function...
Trigger:
  Rapid clicks between sidebar items; slow/unpredictable network latency.
Root Cause:
  Missing request cancellation + missing `selectedId` in the dependency
  array.
Impact:
  Stale data from the previously-selected item flashing on screen before
  the current item's data arrived.
Fix:
  - Added `selectedId` to the effect dependency array.
  - Introduced an `AbortController` per effect run.
  - Added a cleanup `() => controller.abort()` so superseded fetches are
    cancelled.
Validation:
  Manual TS sanity check (see §5).
Regression Risk: Low
```

### BUG-002 — `data.items.map(...)` crashes on null/undefined data
... (continues for each bug)

## 3. Files Changed

```text
Modified Files:
- src/components/Dashboard.tsx
    Reason: Root-cause fixes for BUG-001 through BUG-012. Replaced
            race-prone fetch effects with AbortController + dependency
            array fixes; added defensive guards on localStorage init and
            on `data.items` render; added debounce + cancellation to
            search; fixed stale closure via ref; added error UI.
```

## 4. Remaining Issues

None.

## 5. Final Validation

```text
Type Check:            NOT AVAILABLE  (no tsconfig.json / tsc in fixture)
Lint:                  NOT AVAILABLE  (no eslint config in fixture)
Tests:                 NOT AVAILABLE  (no test runner / no test files)
Build:                 NOT AVAILABLE  (no package.json / no bundler config)
Runtime Verification:  NOT AVAILABLE  (no React runtime / no dev server)
```
````

---

## Skill structure

```
codebase-audit/
├── SKILL.md                          # Main skill instructions (~280 lines)
├── LICENSE                           # MIT
├── README.md                         # This file
├── CONTRIBUTING.md                   # How to contribute
├── CHANGELOG.md                      # Release history template
├── .gitignore
├── references/
│   ├── bug-patterns.md               # Cheatsheet of bug patterns (8 categories)
│   └── validation-commands.md        # Per-stack validation commands
├── evals/
│   └── evals.json                    # Test prompts + assertions
└── assets/
    ├── README.md                     # How the test fixtures work
    ├── test-fixture-react/           # React dashboard with 7 planted bugs
    ├── test-fixture-node/             # Node.js Express API with 10 planted bugs
    └── test-fixture-python/           # Python data pipeline with 9 planted bugs
```

The bundled test fixtures let contributors re-run the evals locally to verify
the skill still works after changes — no external setup required.

---

## Test fixtures

Three tiny, intentionally-buggy codebases used to evaluate the skill:

| Fixture | Stack | Planted Bugs | Symptom (what the user reports) |
|---------|-------|--------------|----------------------------------|
| `test-fixture-react/` | React + TypeScript | 7 | "Page crashes with 'Cannot read property map of undefined' when clicking sidebar items quickly. Search shows results for previous query." |
| `test-fixture-node/` | Node.js + Express + MySQL | 10 | "API crashes in production with unhandled promise rejections. Possible SQL injection." |
| `test-fixture-python/` | Python + psycopg2 + CSV | 9 | "Pipeline occasionally fails with 'NoneType has no attribute X'. Inserted duplicate records last week." |

Each fixture file has a comment block at the top listing every planted bug.
The grader script checks whether the audit report mentions each one.

---

## Benchmark results

Run on 3 fixture codebases containing 7–10 planted bugs each, with 3 runs
per configuration (with-skill vs. baseline without-skill):

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | **100%** | 91% | **+9%** |
| Avg Tokens | 40,990 | 18,400 | +22,591 |

The skill uses more tokens because it follows a more thorough methodology —
finding more bugs, classifying severity, analyzing regression risk, and
producing a structured report.

Notably, the with-skill runs also found bugs **beyond** the planted ones:

- **React**: found 12 bugs (7 planted + 5 bonus)
- **Node**: found 17 bugs (10 planted + 7 bonus, including a DoS-class crash on `/api/password-reset` when email is unknown)
- **Python**: found 9 bugs (matches planted)

### Per-eval breakdown

| Eval | With Skill | Without Skill |
|------|------------|---------------|
| React — race conditions + state bugs | 10/10 (100%) | 9/10 (90%) |
| Node — API errors + security holes | 12/12 (100%) | 11/12 (92%) |
| Python — NoneType + duplicate inserts | 10/10 (100%) | 9/10 (90%) |

---

## Re-running the evals

```bash
# From the repo root
python scripts/run_evals.py
```

This will:

1. Spawn parallel subagents — one with the skill, one without (baseline)
2. Run them against the 3 test fixtures
3. Grade the outputs against the planted bugs (heuristic keyword matching)
4. Produce a benchmark report showing pass-rate improvement

See [`evals/evals.json`](evals/evals.json) for the test prompts and assertion
definitions, and [`scripts/grade_audit_runs.py`](scripts/grade_audit_runs.py)
for the grader.

---

## Roadmap

- [ ] **More stacks**: Go, Rust, Ruby, PHP, Java fixtures
- [ ] **More bug patterns**: add to `references/bug-patterns.md` (e.g. WebSocket lifecycle, GraphQL N+1, Kubernetes manifest issues)
- [ ] **Stronger assertions**: replace keyword matching with AST-based grading where possible
- [ ] **CI integration**: GitHub Action that re-runs evals on every PR
- [ ] **Description optimization**: run the trigger eval loop to improve firing accuracy
- [ ] **Multi-file fixtures**: current fixtures are single-file; add realistic multi-module projects

Pull requests welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

Areas especially welcome:

- New test fixtures in other languages (Go, Rust, Ruby, PHP, Java)
- Additional bug patterns in `references/bug-patterns.md`
- Cross-stack validation commands in `references/validation-commands.md`
- Skill description improvements for better triggering

### Quick contribution flow

```bash
# Fork → Clone → Branch → Edit → Re-run evals → PR
git checkout -b fix/add-rust-fixture
# ... add fixture, update evals.json, update grader ...
python scripts/run_evals.py   # verify pass rate still ≥ 90%
git commit -am "Add Rust test fixture with 8 planted bugs"
git push origin fix/add-rust-fixture
# Open PR on GitHub
```

---

## Publishing to GitHub

If you're forking or re-publishing this skill, here are the exact steps:

```bash
# 1. Create an empty repo on GitHub first (no README, no LICENSE — repo is empty)
#    https://github.com/new

# 2. From your local copy:
cd /path/to/codebase-audit
git init
git add .
git commit -m "Initial commit: codebase-audit skill v1.0.0"

# 3. Set the remote (replace YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/codebase-audit.git
git branch -M main
git push -u origin main

# 4. Create a release tag
git tag -a v1.0.0 -m "v1.0.0 — initial release"
git push origin v1.0.0

# 5. Upload codebase-audit.skill as a release asset
#    GitHub → Releases → Draft a new release → select tag v1.0.0
#    → upload codebase-audit.skill → publish
```

### Recommended GitHub repo settings

- **Description**: "GLM skill — Senior Engineer codebase audit & bug fixing"
- **Topics**: `glm`, `glm-skill`, `code-review`, `debugging`, `static-analysis`, `code-audit`, `developer-tools`
- **Homepage URL**: link to the Releases page
- **License**: MIT (already in repo)
- **Issues**: enabled
- **Discussions**: enable if you want community Q&A
- **Pages** (optional): render the README at `https://YOUR-USERNAME.github.io/codebase-audit/`

---

## License

[MIT](LICENSE) — free for commercial and personal use.

---

## Acknowledgements

- Built using the [skill-creator](https://github.com/zai-org/glm-skills/tree/main/skills/skill-creator) workflow.
- Inspired by the kind of code review every senior engineer wishes they had time to do but rarely does.
- Bug pattern catalog informed by years of "lessons learned the hard way" across React, Node, and Python production systems.

---

<div align="center">

**If this skill saves you a production incident, consider starring the repo. ⭐**

</div>

# Contributing to codebase-audit

Thanks for your interest in improving this skill! This document covers the basics.

## Code of Conduct

Be kind. Be specific. Be patient. Assume good intent.

## Ways to contribute

| Area | How |
|------|-----|
| Bug patterns | Add new patterns to `references/bug-patterns.md` — include a clear description and a concrete example |
| Test fixtures | Add new fixture codebases in `assets/test-fixture-<lang>/` with planted bugs + comment annotations |
| Validation commands | Extend `references/validation-commands.md` for stacks we don't cover yet (Go, Rust, Ruby, PHP, Java, etc.) |
| Skill improvements | Edit `SKILL.md` — keep it under 500 lines, follow the existing style (imperative form, explain the *why*) |
| Triggering | Improve the `description` field in frontmatter so the skill fires more reliably without overtriggering |

## Development workflow

### 1. Set up

```bash
git clone https://github.com/your-username/codebase-audit.git
cd codebase-audit
```

### 2. Make your change

Edit the relevant files. Keep these guidelines in mind:

- **SKILL.md body should stay under 500 lines.** Move detail to `references/`.
- **Imperative form.** Tell the model what to do, not what it should be doing.
- **Explain the why.** Modern LLMs are smart — give them the reasoning, not just rules. Avoid heavy-handed `MUST` and `NEVER` when an explanation works better.
- **No overfitting.** Don't add narrow instructions that only fix one specific test case. Generalize.

### 3. Re-run the evals

Before submitting, verify the skill still works:

```bash
python scripts/run_evals.py
```

This spawns parallel subagents against the 3 test fixtures and grades the results. The benchmark should show:

- With-skill pass rate ≥ 90%
- Without-skill pass rate lower than with-skill

If you add a new fixture, add an entry to `evals/evals.json` and a grading function to `scripts/grade_audit_runs.py`.

### 4. Submit a PR

- One change per PR — small and focused is easier to review.
- Include before/after benchmark numbers in the PR description.
- If you're adding a new test fixture, list the planted bugs in the PR so reviewers can verify they're all caught.

## Adding a new test fixture

1. Pick a stack (Go, Rust, Ruby, etc.).
2. Create `assets/test-fixture-<lang>/myapp/` with a single-file (or small) codebase.
3. Plant 5–10 realistic bugs across the 8 categories from the skill.
4. Add a comment at the top of each file listing the planted bugs (so the grader knows what to look for).
5. Add a prompt to `evals/evals.json` describing the user's symptom.
6. Add assertions to the `assertions` array.
7. Add a grading function to `scripts/grade_audit_runs.py` keyed on the new eval name.

## Skill description optimization

If you want to improve the skill's triggering accuracy (how often it fires when it should, doesn't fire when it shouldn't), use the description optimization loop:

```bash
python -m scripts.run_loop \
  --eval-set <trigger-eval.json> \
  --skill-path . \
  --max-iterations 5
```

See the skill-creator documentation for details.

## Reporting issues

Use GitHub Issues. Include:

- What you expected the skill to do
- What it actually did
- The exact prompt you used
- The output (or relevant excerpt)
- The skill version (git SHA is fine)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

# Validation Commands by Stack

When running Phase 6 (Validation), use the commands appropriate to the project's stack. This is a quick lookup — not exhaustive.

## Node.js / JavaScript / TypeScript

```bash
# Lint
npm run lint              # or: yarn lint / pnpm lint / bun run lint
npx eslint .              # if no script defined

# Type check
npx tsc --noEmit          # TypeScript
npm run typecheck         # if a script is defined

# Tests
npm test                  # Jest / Mocha / Vitest / etc.
npm run test:unit
npm run test:integration

# Build
npm run build             # Next.js / Vite / webpack / esbuild / etc.
```

## Python

```bash
# Lint
ruff check .
flake8 .
pylint <package>/

# Type check
mypy <package>/
pyright

# Tests
pytest
pytest tests/unit

# Build / install
pip install -e .
python -m build
```

## Go

```bash
go vet ./...
golangci-lint run
go test ./...
go test -race ./...        # race detector — important!
go build ./...
```

## Rust

```bash
cargo check
cargo clippy --all-targets -- -D warnings
cargo test
cargo build --release
```

## Java / JVM

```bash
./gradlew check            # Gradle
./gradlew test
./gradlew build

mvn verify                 # Maven
mvn test
```

## Ruby

```bash
bundle exec rubocop
bundle exec rspec
bundle exec rails test
```

## PHP

```bash
vendor/bin/phpstan analyse
vendor/bin/phpunit
composer test
```

## Generic / Multi-stack

If you can't tell the stack, look for these files in the project root:

| File | Stack |
|------|-------|
| `package.json` | Node / JS / TS |
| `tsconfig.json` | TypeScript |
| `requirements.txt`, `pyproject.toml`, `setup.py` | Python |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pom.xml`, `build.gradle` | JVM |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `Dockerfile` | Containerized — read it to find the actual build/test commands |

## When a tool is unavailable

If a command isn't installed (e.g. `npm run lint` errors with "command not found"):

1. Check if a config file exists but the script is missing (e.g. `.eslintrc.json` present but no `lint` script).
2. Try invoking the tool directly via `npx`, `pipx`, or local binary.
3. If it really doesn't exist, mark that validation step as `NOT AVAILABLE` in the final report — do not silently skip it.

## What to report

For each validation step, report one of:

- `PASS` — ran successfully, no errors.
- `FAIL` — ran but produced errors. Distinguish between errors caused by your changes vs pre-existing errors.
- `NOT AVAILABLE` — tool not installed, no script defined, or environment cannot run it.

Always include the **exact command you ran** and a one-line summary of the output.

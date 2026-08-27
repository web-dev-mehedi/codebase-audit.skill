# GitHub Repository Setup — for `web-dev-mehedi`

Complete, copy-paste guide to publish the `codebase-audit` skill on your GitHub account.

---

## 1. Repository metadata (paste into GitHub's "About" section)

### Short description (≤350 chars — what shows next to the repo name in lists)

```
GLM skill that turns the model into a Senior Software Engineer — performing deep codebase audits to find bugs, race conditions, security holes, and edge-case failures, then fixing them safely at the root cause. React · Node · Python fixtures included.
```

### Topics (add all of these — they're how people discover the repo)

```
glm  glm-skill  code-review  debugging  static-analysis  code-audit  developer-tools  bug-fixing  security-audit  ai-skill
```

### Homepage URL

```
https://github.com/web-dev-mehedi/codebase-audit/releases
```

### README headline (for the repo page — already in your README)

```
codebase-audit — A GLM skill for Senior Engineer codebase audits & root-cause bug fixing
```

---

## 2. Create the empty repo on GitHub

Go to: **https://github.com/new**

Fill in:

| Field | Value |
|-------|-------|
| Repository name | `codebase-audit` |
| Description | (paste the short description above) |
| Public / Private | **Public** (you want to open-source it) |
| Add a README file | ☐ **Uncheck** — your local copy already has one |
| Add .gitignore | **None** — your local copy already has one |
| Choose a license | **None** — your local copy already has MIT |

Click **Create repository**.

You'll be redirected to: `https://github.com/web-dev-mehedi/codebase-audit`

---

## 3. Push your local code

Open a terminal and run these exact commands (each block is one logical step):

### Step 3.1 — Init the git repo locally

```bash
cd /home/z/my-project/skills/codebase-audit
git init
git add .
git commit -m "feat: initial release of codebase-audit skill v1.0.0

- SKILL.md with 6-phase senior-engineer methodology
- 3 bug-planted test fixtures (React, Node, Python)
- Bug-pattern cheatsheet and per-stack validation commands
- Benchmark: 100% with-skill vs 91% baseline pass rate
- MIT license, README, CONTRIBUTING, CHANGELOG"
```

### Step 3.2 — Connect to your GitHub repo

```bash
git remote add origin https://github.com/web-dev-mehedi/codebase-audit.git
git branch -M main
git push -u origin main
```

The first push will prompt for your GitHub credentials. If you have 2FA on (recommended), use a Personal Access Token instead of your password:

- Go to: https://github.com/settings/tokens
- Generate new token (classic) → check `repo` scope → generate
- Paste the token as your password when prompted

Or, even easier — use the GitHub CLI:

```bash
# Install once (if not installed)
# Debian/Ubuntu: sudo apt install gh
# macOS: brew install gh

gh auth login
# Follow the prompts (browser-based auth, no token pasting needed)

# Then push — no password needed
git push -u origin main
```

### Step 3.3 — Verify the push

Refresh `https://github.com/web-dev-mehedi/codebase-audit` in your browser.

You should see:
- The polished README with hero header + badges
- 15 files in the file tree
- `MIT` license auto-detected on the right sidebar

---

## 4. Set repo metadata on GitHub

On your repo page (`https://github.com/web-dev-mehedi/codebase-audit`):

### Add topics + description

1. Click the **⚙️ gear icon** next to "About" on the right sidebar
2. **Description**: paste the short description from section 1
3. **Website**: paste the homepage URL from section 1
4. **Topics**: add each topic one by one (press Enter after each):
   ```
   glm  glm-skill  code-review  debugging  static-analysis
   code-audit  developer-tools  bug-fixing  security-audit  ai-skill
   ```
5. Check **Releases** ✓
6. Check **Packages** ☐ (leave unchecked)
7. Click **Save changes**

### Enable Issues + Discussions (recommended)

1. Click **⚙️ Settings** (top tab)
2. Scroll to **Features**
3. ☑ Issues — for bug reports and feature requests
4. ☑ Discussions — for community Q&A (optional but nice)
5. ☑ Projects — for tracking roadmap items
6. ☑ Wiki — leave unchecked (README + CONTRIBUTING is enough)

### Enable GitHub Pages (optional, makes README render as a website)

1. **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / `(root)`
4. Click **Save**
5. Wait 1-2 minutes — your README will be live at:
   ```
   https://web-dev-mehedi.github.io/codebase-audit/
   ```

---

## 5. Create the first release (v1.0.0)

### Tag the release locally

```bash
cd /home/z/my-project/skills/codebase-audit
git tag -a v1.0.0 -m "v1.0.0 — initial release

First public release of the codebase-audit GLM skill.

Features:
- 6-phase senior-engineer methodology
- Severity classification P0-P3
- Structured engineering report format
- 3 bug-planted test fixtures (React, Node, Python)
- Benchmark: 100% with-skill vs 91% baseline pass rate

Bundled:
- references/bug-patterns.md (8-category cheatsheet)
- references/validation-commands.md (per-stack commands)
- evals/evals.json (3 test prompts + assertions)
- scripts/grade_audit_runs.py + run_evals.py

License: MIT"

git push origin v1.0.0
```

### Create the release on GitHub

1. Go to: `https://github.com/web-dev-mehedi/codebase-audit/releases/new`
2. **Choose a tag**: `v1.0.0` (it'll appear after the local push)
3. **Release title**: `v1.0.0 — Initial Release`
4. **Description** (paste this):

```markdown
## 🎉 First release of codebase-audit

A GLM skill that turns the model into a Senior Software Engineer — performing deep codebase audits to find bugs, race conditions, security holes, and edge-case failures, then fixing them safely at the root cause.

### What's included

- **SKILL.md** — 6-phase senior-engineer methodology (Discovery → Bug Hunt → Root Cause → Safe Fix → Regression → Validation)
- **3 test fixtures** — React + Node + Python codebases with 7-10 planted bugs each
- **Bug-patterns cheatsheet** — 8-category reference (runtime, logic, state, async, API, DB, auth, edge cases)
- **Validation commands** — per-stack lookup (Node, Python, Go, Rust, Java, Ruby, PHP)
- **Eval grader** — heuristic keyword/pattern matching with benchmark output

### Benchmark

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | **100%** | 91% | **+9%** |
| Avg Tokens | 40,990 | 18,400 | +22,591 |

The skill uses more tokens because it follows a more thorough methodology — finding more bugs, classifying severity, analyzing regression risk, and producing a structured report.

Notably, the with-skill runs also found bugs **beyond** the planted ones:
- React: found 12 bugs (7 planted + 5 bonus)
- Node: found 17 bugs (10 planted + 7 bonus, including a DoS-class crash)
- Python: found 9 bugs (matches planted)

### Installation

```bash
# Download codebase-audit.skill from this release's assets, then:
glm skills install codebase-audit.skill
```

Or clone the repo:

```bash
git clone https://github.com/web-dev-mehedi/codebase-audit.git
cd codebase-audit
glm skills install .
```

### Usage

Just talk to GLM naturally — the skill triggers automatically:

```
> My React dashboard crashes when users click sidebar items quickly.
  Sometimes the search box shows results for the previous query.
  Can you audit and fix?
```

### License

MIT — free for commercial and personal use.

---

**Full changelog**: https://github.com/web-dev-mehedi/codebase-audit/blob/main/CHANGELOG.md
```

5. **Attach binaries**: drag and drop `/home/z/my-project/download/codebase-audit.skill` (36 KB) into the "Assets" area
6. Check ☑ **Set as the latest release**
7. Click **Publish release**

---

## 6. Final URL checklist

After everything's published, your skill lives at:

| What | URL |
|------|-----|
| Repo | https://github.com/web-dev-mehedi/codebase-audit |
| README | https://github.com/web-dev-mehedi/codebase-audit/blob/main/README.md |
| Latest release | https://github.com/web-dev-mehedi/codebase-audit/releases/latest |
| v1.0.0 release | https://github.com/web-dev-mehedi/codebase-audit/releases/tag/v1.0.0 |
| Skill file download | https://github.com/web-dev-mehedi/codebase-audit/releases/download/v1.0.0/codebase-audit.skill |
| Issues | https://github.com/web-dev-mehedi/codebase-audit/issues |
| Discussions | https://github.com/web-dev-mehedi/codebase-audit/discussions |
| GitHub Pages (optional) | https://web-dev-mehedi.github.io/codebase-audit/ |
| Clone URL | `https://github.com/web-dev-mehedi/codebase-audit.git` |

---

## 7. Share it

Once published, share the repo link in:

- The GLM skills community (if there's a Discord/Slack)
- Twitter/X: *"Open-sourced a GLM skill that turns the model into a Senior Engineer for codebase audits. 100% pass rate on planted bugs. MIT licensed: https://github.com/web-dev-mehedi/codebase-audit"*
- Reddit r/programming, r/devops, r/MachineLearning (post title: *"I open-sourced a GLM skill that audits codebases like a senior engineer — finds bugs, fixes them at the root cause, delivers a structured report"*)
- Hacker News (Show HN: *"Show HN: A GLM skill that audits codebases like a senior engineer"*)

---

## 8. Maintenance checklist (ongoing)

- [ ] Watch the repo for issues — respond within 48h
- [ ] Pin issues that are common questions
- [ ] Add a `good first issue` label to easy contributions
- [ ] Update CHANGELOG.md on every release
- [ ] Re-run evals before each release: `python scripts/run_evals.py`
- [ ] Bump version tag (`v1.1.0` for features, `v1.0.1` for bug fixes)

---

## Quick reference — all commands in one block

```bash
# 1. Init and commit
cd /home/z/my-project/skills/codebase-audit
git init
git add .
git commit -m "feat: initial release of codebase-audit skill v1.0.0

- SKILL.md with 6-phase senior-engineer methodology
- 3 bug-planted test fixtures (React, Node, Python)
- Bug-pattern cheatsheet and per-stack validation commands
- Benchmark: 100% with-skill vs 91% baseline pass rate
- MIT license, README, CONTRIBUTING, CHANGELOG"

# 2. Push to GitHub (replace web-dev-mehedi if needed)
git remote add origin https://github.com/web-dev-mehedi/codebase-audit.git
git branch -M main
git push -u origin main

# 3. Tag the first release
git tag -a v1.0.0 -m "v1.0.0 — initial release"
git push origin v1.0.0

# 4. Then on GitHub.com:
#    - Go to https://github.com/web-dev-mehedi/codebase-audit/releases/new
#    - Select tag v1.0.0
#    - Paste the release description from section 5
#    - Upload codebase-audit.skill as an asset
#    - Publish
```

That's it. Your skill is now open-source on GitHub.

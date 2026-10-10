---
status: current
---

# Validation

Version 1.0.0 passed its initial local macOS validation on September 4, 2026
(PDT). That dated evidence is recorded below. The maintained commands are
`bin/check` and `bin/smoke-qmd`.

## Current automated checks

The [maintainer workflow](../.github/workflows/check.yml) runs `bin/check` on
the latest Ubuntu and macOS runner images for pull requests and pushes to `main`. It records
tool versions in each run. See the
[workflow runs](https://github.com/jubishop/project-starter/actions/workflows/check.yml)
for results tied to exact commits.

Since 2.0.0, the behavior suite runs only here, against copies of the bundle
itself, so adopter documents never become test fixtures. It covers:

- Knowledge tooling: setup, search routing, freshness, refresh coordination,
  hooks, worktrees, model caches, diagnostics, and refresh-log timestamps.
- Check modes: `bin/check-application` runs only under `--full`, only after
  the foundation checks pass, and its failures propagate, while syntax, lint,
  and whitespace errors still fail the routine modes.
- `bin/sync`: initial adoption, hash and block enforcement with overrides,
  updates between tagged releases with conflict refusal and `--force`, 1.x
  migration through recorded source revisions, and fleet `--status`. The
  adoption test also confirms that the copied CI workflow runs
  `bin/check --full`.
- Setup: `bin/setup-application` runs only after a successful foundation
  setup, must be executable, and its failure fails setup.

Adopters run the same check modes, verify managed-file hashes against the
release that passed this suite, and add their own `bin/check-application`.
actionlint validates both maintained and copyable workflows; it is a
maintainer dependency. QMD and direnv are simulated in automated tests, which
do not establish real-QMD compatibility on a CI runner.

## Current real-QMD commands

The [QMD maintenance guide](qmd-maintenance.md) records the current runtime,
weekly compatibility workflow, dependency updates, and strict diagnostic checks.


Run `bin/smoke-qmd` for the bundle or
`bin/smoke-qmd --project /absolute/path/to/adopter` for a current adopter
snapshot. Both use `~/.cache/qmd/models`. Reports identify the source and
models under `.cache/validation/`. The adopter mode tests uncommitted source
without changing its checkout. Local Git settings and external hook managers
still need verification in the real checkout. Automated regression checks
verify adopter-specific setup failures propagate and leave source files intact.

Model-cache regressions exercise unrelated repositories, linked worktrees,
separate Git metadata, verified duplicate removal, conflict preservation,
external symlink migration, and broken-link repair in isolated home directories.

## Release 2.0 and fleet migration — 2026-10-09

Version 2.0.0 and patch 2.0.1 passed `bin/check` (57 tests) and the starter
checks on Ubuntu 24.04 and macOS 15. Strict real-QMD smoke checks passed on
the 2.0 bundle with QMD 2.8.3 and node-llama-cpp 3.22.1 on an Apple M5 Pro
running macOS 27.0.1, using both the validation lockfile and the shared
runtime.

All 21 adopters moved from 1.x manifests to 2.0.0 with `bin/sync`, then to
2.0.1. Three pilots (health, screenr, podhaven) preceded the other 18. Each
adopter's `bin/check` passed with verified managed-file hashes, and its
`bin/check --full` passed locally except where noted below. GitHub Actions
passed for every pushed commit in the 20 repositories with workflows;
podhaven has no test CI and passed its `bin/test-all --ensure` gate instead.
`bin/sync --status` reported every adopter at 2.0.1 with no drift; podhaven
records two overrides.

The pilots found three starter defects, fixed with regression tests before
the sweep or in 2.0.1: 1.x migration treated `.envrc` as an obsolete managed
file, hook guidance named a moved section, and the managed `AGENTS.md` block
omitted the 1.x decisions-and-secrets rule. Fixture-coupled project tests in
podhaven needed `docs/foundation/` and `LICENSE.project-starter`.

Limits: screenr's two TMDB-dependent application tests failed locally for
lack of catalog configuration in the test environment, and passed in its CI
for the same commit. Removing duplicated `.gitignore` lines was verified per
adopter by comparing ignored untracked files before and after.

## Release 2.1 and latest-stable toolchains — 2026-10-09

Versions 2.1.0 and 2.1.1 passed `bin/check` (53 tests) and both workflows. The
QMD compatibility job now installs the newest QMD and backend on the newest
Node LTS with no lockfile; on October 9 that resolved to QMD 2.8.3 and
node-llama-cpp 3.22.1. All 21 adopters synced to 2.1.1 with `bin/check`
passing, and GitHub Actions passed for every repository's latest commit.

Sixteen adopters replaced exact runtime pins with minimums, `lts/*` or
`3.x` selectors, and `check-latest: true`, adding tests that newer major
versions are accepted. CI then installed Node 24.21.0 everywhere and Python
3.14.8; Python 3.15.0, released the same day, was not yet in GitHub's
version manifest. The VPS's shared Node runtime moved kidsbank from Node 20
and screenr from 24.20.0 to 24.21.0, with local and public health checks
returning 200, and the end-of-life NodeSource package was removed.

## Environment

| Component | Executed version |
| --- | --- |
| Platform | macOS 26.6.2, Apple silicon |
| Python | 3.12.7 |
| Git | 2.50.1, Apple Git-155 |
| QMD | 2.1.0, build `3eaa7db` |
| direnv | 2.37.1 |
| ShellCheck | 0.11.0 |

## Copied-bundle checks

`bin/check` passed all 20 tests. These copy the foundation into disposable
Git repositories and use simulated QMD and direnv programs. They cover:

- Setup and search from subdirectories, including `git knowledge`.
- Repeat setup, unchanged inputs, and code-only changes.
- Missing optional tools and an installed but failing QMD.
- Home-memory opt-in, edits, deletions, missing paths, and removal.
- Read-only diagnostics, stale input detection, and a missing database.
- Preservation of default and configured existing hooks.
- External forwarding, including arguments, post-rewrite stdin, and an
  existing hook's nonzero exit status.
- Worktrees with separate Git metadata, isolated databases, existing model
  preservation, model sharing, and conditional environment approval.
- Concurrent requests, changes during an active refresh, and failure recovery.
- Metadata, filename agreement, index coverage, archive rules, heading anchors,
  reference links, paths with spaces/parentheses, and deliberate exclusions.

The command also passed document checks for the guide and bundle, Python
syntax checks, ShellCheck, and Git whitespace checks. A separate syntax pass
accepted the Python tools with Python 3.9's grammar; runtime execution used
Python 3.12.7. Executable file modes and the matching MIT notices were checked.

## Real-QMD smoke check

`bin/smoke-qmd --models /absolute/path/to/existing/models` passed eight groups
of checks using real QMD and existing local model files:

1. Initial setup and document validation in a copied repository.
2. Keyword retrieval, collection descriptions, focused reads, and subdirectory routing.
3. Exclusion of archived memory, PR review records, and archived docs.
4. Real embedding generation and semantic retrieval.
5. Home-memory opt-in and removal from actual search results.
6. Read-only diagnostics and repeat setup that skips reindexing.
7. Separate worktree databases, shared models, and refresh after uncommitted edits.
8. Disposable worktree removal and verification.

The worktree test verified that a term added to one checkout did not appear
in the primary checkout's search results. Diagnostics left the inspected
files unchanged. Temporary repositories were removed. The smoke command
writes its local machine-readable report under `.cache/validation/`.

## Initial validation limits

Linux execution was deliberately omitted from the September 4 delivery.
The optional Ubuntu workflow was supplied as an integration example and was
not run then. Other QMD versions and project-specific hook managers need their own
integration checks. Runtime diagnostics verify recorded input freshness and
the index's presence; they do not perform a SQLite integrity scan.

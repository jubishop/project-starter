---
status: current
---

# Validation

Version 1.0.0 passed its initial local macOS validation on September 4, 2026
(PDT). That dated evidence is recorded below. The maintained commands are
`bin/check` and `bin/smoke-qmd`.

## Current automated checks

The [maintainer workflow](../.github/workflows/check.yml) runs `bin/check` on
Ubuntu 24.04 and macOS 15 for pull requests and pushes to `main`. It records
tool versions in each run. See the
[workflow runs](https://github.com/jubishop/project-starter/actions/workflows/check.yml)
for results tied to exact commits.

The command runs the base foundation tests and a GitHub adoption regression.
The regression copies the actual optional workflow into a disposable project,
links it from the README and development docs, then runs the three document
tests that create further copies. This detects missing workflow files in
those test fixtures. The base tests also verify use without GitHub files.

A separate adoption regression adds an existing resolved memory page before
running the copied archive checks. It verifies that those checks accept an
existing `memory/archive/` directory and preserve the archived source page.

actionlint validates both maintained and copyable workflows. It is a
maintainer dependency; copied projects still require only ShellCheck for
their foundation checks. QMD and direnv are simulated in automated tests.
These checks do not establish real-QMD compatibility on a CI runner.

Copied projects now use a fast default `bin/check` for document, syntax,
ShellCheck, and whitespace validation. `--documents-only` checks Markdown;
`--full` adds the behavior suite. Regression tests verify mode selection,
failure propagation, required test files, and retained syntax/lint/whitespace
checks. The adoption regression also verifies that copied CI uses `--full`.

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

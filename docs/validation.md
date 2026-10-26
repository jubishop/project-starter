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
  `bin/check --full`. Feature tests enable a feature at adoption and later,
  keep it across syncs, refuse to disable a changed copy, refuse a project
  file in a feature's path until it is removed, and leave adopters without
  the feature unchanged by a release that changes only feature files; each
  enabled adopter passes `bin/check --documents-only`.
- Memory audit feature: `bin/memory-audit` in an adopter that enabled it, with
  fake `claude`, `gh`, `qmd`, `osascript`, and `launchctl` and real Git
  remotes: proposal and session validation, publishing and rebasing, the
  change gate, failure issues and their labels, and the settings. The
  LaunchAgent installer tests run only on macOS.
- Setup: `bin/setup-application` runs only after a successful foundation
  setup, must be executable, and its failure fails setup. A new worktree and
  `bin/prep-worktree` run it too; its failure fails `bin/prep-worktree` but
  never `git worktree add`.
- Check reuse: `bin/check --full` skips `bin/check-application` only for a
  clean checkout whose tree and environment passed it within 12 hours,
  including in a linked worktree; uncommitted changes, a new tree, changed
  `.venv` packages, an older pass, a failed run, and `--no-reuse` run it.

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

## Release 2.2 and Markdown-only CI — 2026-10-14

Version 2.2.0 passed `bin/check` (53 tests), the starter checks on Ubuntu and
macOS, and the QMD compatibility job. All 22 adopters synced to 2.2.0 with
`bin/check` passing, and `bin/sync --status` reported no drift; podhaven
still records two overrides. The 21 adopters with push or pull-request
workflows now skip runs for Markdown-only changes, and `actionlint` passed
on each changed workflow. trading re-includes the two strategy pages its
application serves and its tests render. Adopters ran `bin/check`, not
`bin/check --full`, because the release changed only a policy page, the
manifest, and workflow triggers.

GitHub Actions passed for the pushed commit in all nine public repositories
with workflows, and news and screenr deployed. In the twelve private
repositories, jobs did not start because the account's Actions spending
limit was reached, so CI was unavailable for those commits, not passed.
kidsbank's deployment rule found nothing to deploy.

## Release 2.3 and floating action tags — 2026-10-15

Version 2.3.0 passed `bin/check` (53 tests), the starter checks on Ubuntu and
macOS, and the QMD compatibility job, which runs the floating
`actions/checkout`, `actions/setup-node`, and `actions/upload-artifact` tags.
Twenty of the 21 adopters synced to 2.3.0 with no drift; podhaven still
records two overrides. trading's sync went to
[a pull request](https://github.com/jubishop/trading/pull/21), as its branch
rule requires for non-Markdown changes. Its workflow had already moved to
major tags.

Every commit-SHA or exact-version action reference moved to its major tag,
and podhaven's Sentry CLI moved to its latest release. The only remaining
pins are `tailscale/github-action` in the news and screenr deploy jobs, with
the reason beside each. `actionlint` passed on every changed workflow and
`bin/check` passed in each adopter; news, sourdough, and trading ran
`bin/check --full`, as their instructions require.

The Actions spending limit no longer blocked private repositories. Hosted
CI passed for every pushed commit with a push workflow, public and private,
and for trading's pull request. The news and screenr deploy jobs ran with the
new tags and deployed. podhaven's only workflow runs on a daily schedule, so
its first run on the new tags comes later.

## Release 2.4 and direct starter syncs — 2026-10-15

Version 2.4.0 lets a sync go directly to an adopter's default branch. Untagged
2.3.1 commits that floated `tailscale/*` in deployment jobs were superseded
before release; the user kept that pin. 2.4.0 passed `bin/check` (53 tests).
Its last non-Markdown commit, `dbc2094`, passed the starter checks on Ubuntu
and macOS and the QMD compatibility job. The release commit changed only
Markdown, so the local check was its gate.

All 21 adopters synced to 2.4.0 directly on their default branches, with no
drift. That includes trading, after its branch rule adopted the carve-out.
Each passed `bin/check`; news, sourdough, and trading ran `bin/check --full`.
Hosted CI passed for the pushed commit in all 20 repositories with a push
workflow, including the news and screenr deploy jobs. A manual run of
podhaven's scheduled Sentry Feedback workflow passed on the new action tags
and the latest Sentry CLI.

## Release 2.4.1 and the session-rotation rule — 2026-10-15

Version 2.4.1 removes the task workflow's warning against rotating td sessions
to bypass review checks. All 21 adopters synced to 2.4.1 on their default
branches with no drift; podhaven still records two overrides. At the user's
direction, no checks ran. Its commits were pushed with 2.5.0, which made
unchecked sync-only releases the process.

## Release 2.11 and root README search — 2026-10-24

Versions 2.11.0 and 2.11.1 let a knowledge collection name one Markdown file
and add a `readme` collection for each project's root `README.md`. They passed
`bin/check` (55 and 56 tests), the starter checks on Ubuntu and macOS, and the
QMD compatibility job. The real-QMD smoke check now finds a marker in the
README and confirms that a root-level `NOTES.md`, a nested `notes/README.md`,
and `worktrees/feature/README.md` stay out of the `readme` collection. The
strict check passed locally with QMD 2.8.3 and node-llama-cpp 3.22.2 on an
Apple M5 Pro running macOS 27.0.1.

podhaven's `bin/check --full` found a 2.11.0 defect: its memory audit searches
a sparse copy of the checkout without the README, and the missing-file error
failed 26 of its tests. 2.11.1 indexes nothing for a missing file instead, and
no adopter committed 2.11.0.

All 22 adopters synced to 2.11.1 on their default branches and added the
`readme` collection to `.config/knowledge.json`. podhaven merged the change
into its `bin/_knowledge.py` override and its collection test. In each
adopter, `bin/check` and `bin/qmd-index` passed, `bin/doctor --json` reported
current freshness with one `readme` document, and a search for a distinctive
README term returned `qmd://readme/README.md`. news, stories, radio, and
podhaven also passed `bin/check --full`, as their instructions require.
will's root `plans` collection already ignored `README.md`. `bin/sync --status`
reported no drift; podhaven still records two overrides.

Hosted CI passed for the pushed commit in ten repositories: jeeves,
jubishop.github.io, news, pantrydates, printing, radio, scoreboard, sourdough,
steam-starter, and td-dashboard, and news deployed. In ten private
repositories (artisanalsoftware.com, health, home-infra, kidsbank, stories,
taxes, trading, vidservey, vps-infra, and will), jobs did not start because
the account's Actions spending limit was reached, so CI was unavailable, not
passed. Each passed its workflow's commands locally on the pushed revision,
and trading's Python floor job passed on Python 3.12.15 in a disposable clone.
screenr's CI failed on a test that expects the week of 2026-10-19 to be
finished, which is unrelated to the sync, so its deploy was skipped;
[screenr#316](https://github.com/jubishop/screenr/issues/316) tracks it.
podhaven has no push workflow.

## Release 2.12 and orphaned vector cleanup — 2026-10-24

Version 2.12.0 runs `qmd cleanup` after `qmd embed` on every refresh whose
inputs changed ([issue #3](https://github.com/jubishop/project-starter/issues/3)).
New tests failed first for the expected reasons: a replaced page left one
orphaned vector, no cleanup ran under the worker lock, and a lookup succeeded
with cleanup set to fail, because none ran. They passed after the change, and `bin/check` passed 58
tests. The real-QMD smoke check now asserts that a linked worktree's refresh
after an edit leaves no orphaned vectors; without the change it reported
`Orphaned: 1 embedding chunks (6%)`. The strict check passed locally with QMD
2.8.3 and node-llama-cpp 3.22.2 on an Apple M5 Pro running macOS 27.0.1, and
the starter checks passed on Ubuntu and macOS along with the QMD compatibility
job.

All 22 adopters synced to 2.12.0 on their default branches, and `bin/check`
passed in each. podhaven merged the change into its `bin/_knowledge.py`
override and its tests, which failed without it, and passed
`bin/check --full` with 319 tests. Every adopter's refresh after the sync left
no orphaned vectors. Each index was then deleted and rebuilt, as the changelog
allows, and `bin/doctor --json` reported current freshness with no issues.
`bin/sync --status` reported no drift; podhaven still records two overrides.

| Adopter | Before | Orphaned | After cleanup | Rebuilt |
| --- | --- | --- | --- | --- |
| trading | 32.5 MB | 7,595 of 7,896 | 23.7 MB | 4.8 MB |
| screenr | 13.3 MB | 2,041 of 2,354 | 11.4 MB | 5.0 MB |
| news | 12.7 MB | 2,317 of 2,500 | 7.5 MB | 4.4 MB |
| sourdough | 12.2 MB | 2,786 of 2,850 | 6.8 MB | 3.7 MB |
| stories | 9.0 MB | 1,529 of 1,706 | 7.4 MB | 4.3 MB |
| podhaven | 5.7 MB | 556 of 789 | 4.7 MB | 4.7 MB |

The other 16 indexes were 3.5 to 4.3 MB with 43 to 92 percent of their
vectors orphaned. Cleanup brought them to 3.4 to 3.8 MB, and rebuilding
changed each by at most 8 KB. The gap left after cleanup in larger indexes is
sqlite-vec's partly used vector blocks.

Hosted CI passed for the pushed commit in ten repositories: jeeves,
jubishop.github.io, news, pantrydates, printing, radio, scoreboard, sourdough,
steam-starter, and td-dashboard, and news deployed. In the ten private
repositories, jobs again did not start because of the Actions spending limit,
so CI was unavailable, not passed. Each passed its workflow's commands locally
on the pushed revision: trading's test job and its Python 3.12.15 floor job
ran in disposable clones, which must sit where Docker can see them for its
Linux-only tests, and the Node repositories ran `npm ci` in disposable clones.
screenr's CI failed only on the same date-dependent weekly test that
[screenr#316](https://github.com/jubishop/screenr/issues/316) tracks, so its
deploy was skipped.

## Release 3.0 and td's retirement — 2026-10-25

Version 3.0.0 retires td task tracking: sync removes
`docs/foundation/task-tracking.md`, the managed `AGENTS.md` block drops its td
rule, and the managed `.gitignore` block no longer ignores `.todos/`. The
first `bin/check` failed on a design-record link to the removed page; after
the fix, it passed 58 tests. The starter checks passed on Ubuntu and macOS,
and so did the QMD compatibility job's real-QMD run. QMD itself did not
change, so the local strict smoke check was not rerun. Version 3.0.1, a sync-only
release, removes a stray comma that 3.0.0 left in the starter's
project-owned `docs/README.md`.

All 22 adopters synced on their default branches: 21 to 3.0.0 and then
3.0.1, and screenr straight to 3.0.1 once its session had stopped using td.
Each adopter's manual follow-up removed td from its project-owned pages,
td task IDs cited as provenance (health, news, pantrydates, radio, and
vidservey), and the `.gitignore` headers left empty when 2.0 moved `.todos/`
into the managed block. In a few adopters it also changed:

- podhaven: its sidecar and `.td-root` ignores;
- will: its `.todos/**` knowledge exclusion;
- artisanalsoftware.com: its deployment test, which named the removed page and
  `.todos/` as example paths;
- home-infra: its Pi notes, after td-sync and the td dashboard were removed
  from the Pi.

`bin/check --documents-only` passed in every adopter, and
artisanalsoftware.com's deployment test passed its 5 cases. Each adopter's
`.todos/` was deleted after its unfinished tasks were closed as done or moved
into GitHub issues. `bin/sync --status` reported no drift; podhaven still
records two overrides.

For the 3.0.0 commit, hosted CI passed in ten public repositories: jeeves,
jubishop.github.io, news, offline-librarian, pantrydates, printing, radio,
scoreboard, sourdough, and steam-starter. news skipped deployment by its
recorded decision. screenr's 3.0.1 commit failed one application shard when
Docker Hub answered 502 to the caddy image pull, and it passed on a rerun of
that job. Its deploy was skipped by its recorded decision. podhaven has no
push workflow.

In the ten private repositories, jobs did not start because of the Actions
spending limit, so CI was unavailable, not passed. Each passed its workflow's
commands locally on the pushed revision:

- health, home-infra, taxes, vidservey, vps-infra, and will: `bin/check --full`
  in their primary checkouts;
- artisanalsoftware.com, kidsbank, and stories: `npm ci` and `bin/check --full`
  in disposable clones;
- trading: `bin/check --full` with Python 3.15.1, then its floor job's
  `bin/check-application` with Python 3.12.15, in a temporary worktree.

The 3.0.1 commits changed only `.project-starter.json`, so they carry
`[skip ci]`.

## Release 3.2 and the shared memory audit — 2026-10-25

Version 3.2.0 adds optional features and the memory audit
([issue #6](https://github.com/jubishop/project-starter/issues/6)). The new
`bin/sync` tests failed first because sync rejected `--enable`. Against
screenr's runner copied verbatim into the feature, 22 of the 44 audit tests
failed: those covering settings, the default label and repository, the
configurable heading, labels, trailers, every push URL, and the empty-memory
skip. The other 22, ported from screenr's suite, passed against both runners.
After the change, `bin/check` passed 107 tests in 101 to 110 seconds on macOS 27.0.1
with Python 3.15.1; the audit suite takes about 43 of them.

Throwaway adopters made by `bin/sync --init` enabled the feature at adoption
and later, kept it across a plain sync, disabled it, and refused it while a
project copy of `bin/_memory_audit.py` existed, then accepted it once the
copy was gone; each passed its `bin/check`. With podhaven's
`bin/_knowledge.py` override and `.config/knowledge.json`, a faked audit kept
its `includeByDefault: false` collection out of default search, indexed only
the clone, and removed the archived note from an `Active notes` list. No real
audit or LaunchAgent install ran.

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

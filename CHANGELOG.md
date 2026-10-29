# Changelog

Each release lists what `bin/sync` changes in adopters and the manual
follow-up it cannot apply. See [releases](docs/releases.md).

## 3.6.0 — 2026-10-29

### Synced

- The `memory-audit` feature's tool boundary check also probes the audit's
  own allow rules, `jq` and `qmd search`, and its Grep and Glob tools, the
  routes most likely to widen in a later Claude Code release. It now requires
  that `jq` cannot read a file outside the repository, as in
  `jq -R . ../outside.txt` and `jq --rawfile f ../outside.txt -n '$f'`; that
  neither allow rule covers a command chained after it, as in
  `jq -n 1; cat ../outside.txt` and `qmd search … && printenv`; and that Grep
  and Glob stay inside the repository. Claude Code 2.1.312 denies all of
  these, so nothing was exposed; this is regression coverage.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path; the next scheduled audit runs the extended check without a reinstall.

### Verified

`bin/check` passed 121 tests on macOS 27.0.1 with Python 3.15.1. Real Claude
Code 2.1.312 and QMD 2.8.3 ran the check in a throwaway adopter, with no model
request, and it passed in about a second with every new probe denied. The
same `jq -R`, Grep, and Glob calls aimed inside the repository printed the
file, so those probes would catch a widened route. Claude Code 2.1.312 denies
`jq --rawfile`, `--slurpfile`, and `--arg` even inside the repository, so the
`--rawfile` probe guards that refusal as well as the working-directory check.

## 3.5.1 — 2026-10-29

### Synced

- The `memory-audit` feature clones every run to the same path,
  `.cache/memory-audit/repository`, instead of a new folder under
  `.cache/memory-audit/runs/`. Claude Code records the folder it works in as a
  project in `~/.claude.json` when the project tracks
  `.claude/settings.local.json`, and nothing prunes those entries, so each
  audit left one more behind: podhaven had six by 2026-10-28. Its large tool
  output under `~/.claude/projects/` now lands in one folder per project too,
  which Claude Code's `cleanupPeriodDays` sweep prunes. The tool boundary
  check's scratch repository moves to `.cache/memory-audit/boundary/` for the
  same reason. Run folders keep the same logs, context, report, and patch, and
  a run replaces a clone that an interrupted run left.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path; the next scheduled audit uses the new paths without a reinstall. The
entries that earlier runs left in `~/.claude.json` stay, about 285 bytes each,
since removing them means editing a file Claude Code rewrites. Claude Code's
own sweep removes their `~/.claude/projects/` folders once their files age
past `cleanupPeriodDays`.

### Verified

`bin/check` passed 123 tests on macOS 27.0.1 with Python 3.15.1. Real Claude
Code 2.1.312 ran the runner's `run_model` against its local stand-in API, so
with no model request, in an isolated `CLAUDE_CONFIG_DIR`, three times in
repositories that track `.claude/settings.local.json` and print a large `jq`
output. New paths per run left three `~/.claude.json` entries and three
`~/.claude/projects/` folders; one reused path left one of each. Without the
tracked file it wrote no entry but still one folder per path. Claude Code
2.1.312's retention sweep deletes `tool-results` files older than
`cleanupPeriodDays`, then empty session and project folders. QMD is unchanged
since 2.12.0's strict real-QMD smoke; this release does not rerun it.

## 3.5.0 — 2026-10-28

### Synced

- The `memory-audit` feature checks its tool boundary before every model run.
  3.3.1 keeps the key from the model's tools through Claude Code behavior
  that any release can change: scrub mode, the `jq` allow rule, and
  `INDEX_PATH` reaching tools. The runner now runs the installed Claude Code
  with its own model-run and search setup and the audit's flags against a
  local stand-in for the Anthropic API, which scripts the tool calls, so the
  check makes no model request and costs nothing. If `jq` reads
  `ANTHROPIC_API_KEY` or a secret-named canary, if `jq` on the context or
  `qmd search` on the clone's index stops working, or if an environment or
  process listing or a read outside the repository runs, the audit fails
  before the model starts and reports through its notification and
  `Memory audit failing` issue.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path; the next scheduled audit runs the check without a reinstall.

### Verified

`bin/check` passed 121 tests on macOS 27.0.1 with Python 3.15.1. Real Claude
Code 2.1.312 and QMD 2.8.3 ran the check in a throwaway adopter, with no model
request. With 3.3.0's model run and search setup, it failed because `jq`
printed the canary key through `env` and `$ENV`, and printed
`ANTHROPIC_API_KEY`. With 3.3.1's and this release's, it passed in about a
second. 3.3.1's scrubbed model run with 3.3.0's search setup failed because
`qmd search` missed the scratch note.

## 3.4.0 — 2026-10-28

### Synced

- `bin/check` runs ShellCheck on each `bin/` script whose shebang names `sh`,
  `bash`, `dash`, or `ksh`, in that dialect, directly or through `env` and
  with or without flags, such as `#!/usr/bin/env bash` or `#!/bin/bash -e`.
  Before, it linted only scripts starting with `#!/bin/sh`, so bash scripts
  such as deploy tooling went unlinted. `.envrc` is still linted as bash, and
  scripts outside `bin/` still are not. The engineering policy names the
  linted files and notes that a project's `.shellcheckrc` configures
  ShellCheck.

### Manual follow-up

Every adopter runs `bin/check` after syncing and fixes any finding in a newly
linted script before committing the sync. At release time, ShellCheck 0.11.0
passed every adopter's newly linted scripts except these:

- health: SC2029 notes in `bin/deploy.sh` and
  `bin/rollback-health-server.sh`, where `ssh` commands expand variables on
  the client. Escape any expansion meant for the server, and add
  `# shellcheck disable=SC2029` above each intended one, as trading's
  `bin/deploy.sh` does.
- podhaven: SC1091 notes in `bin/check-sentry-feedback` and
  `bin/check-sentry-issues`, whose `# shellcheck source=` directives need
  ShellCheck to follow sourced files. Add a root `.shellcheckrc` containing
  `external-sources=true`.

trading may then drop the `bin/` half of the bash lint test it added in
jubishop/trading#378.

### Verified

`bin/check` on macOS 27.0.1 with Python 3.15.1, and the starter checks on
Ubuntu and macOS. The new `bin/check` run with ShellCheck 0.11.0 in clones of
health, podhaven, and trading failed on the findings above and passed
trading; a `.shellcheckrc` with `external-sources=true` cleared podhaven's.
QMD is unchanged since 2.12.0's strict real-QMD smoke (QMD 2.8.3 with
node-llama-cpp 3.22.2); this release does not rerun it.

## 3.3.1 — 2026-10-28

### Synced

- The `memory-audit` feature keeps the project's API key away from the
  model's tools. In 3.3.0, Claude Code passed `ANTHROPIC_API_KEY` to Bash, and
  the allowed `jq -n 'env.ANTHROPIC_API_KEY'` printed it without approval, so
  a prompt-injected issue could steer the key into a published note or the
  failure issue. Every model attempt now runs with
  `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`, which bills the key but withholds it
  and other secret-named variables from tool processes.
- Scrub mode also withholds `XDG_CACHE_HOME`, so the runner sets `INDEX_PATH`
  to the clone's search index, keeping `qmd search` off the user's own index.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path; the next scheduled audit runs the new runner without a reinstall.

### Verified

`bin/check` on macOS 27.0.1 with Python 3.15.1. Claude Code 2.1.312 ran the
runner's own `run_model` and flags on Haiku through the subscription with two
canary variables. On 3.3.0, `jq -n 'env.AUDIT_CANARY_API_KEY'` and `$ENV`
printed the secret-named canary; after the fix both printed `null`, while
`jq` on the context file, `qmd search` on the clone's index, `git show`, Read,
and Grep still worked. With a bogus `ANTHROPIC_API_KEY`, a SessionStart hook
saw the key in its environment without scrub mode and not with it, and the
API still answered 401 for that key. QMD is unchanged since 2.12.0's strict
real-QMD smoke; this release does not rerun it.

## 3.3.0 — 2026-10-28

### Synced

- The `memory-audit` feature runs `claude-sonnet-5-5` instead of
  `claude-haiku-5-5`, still at high effort.
- An audit bills the project's own Anthropic API key when the checkout's
  ignored `.env` sets `MEMORY_AUDIT_ANTHROPIC_API_KEY`. The runner reads only
  that line and passes the key to Claude as `ANTHROPIC_API_KEY` for the
  API-key attempt alone. Without the key, the audit uses the subscription
  login as before.
- When the API refuses the key for a low credit balance, a reached spend
  limit, or HTTP 401 or 403, the runner reruns that attempt on the
  subscription without a manual step. Other failures fail as before.
  `latest.json` records the `credential` used, which replaces `provider`, and
  the `fallback` with its `trigger`.

### Manual follow-up

Adopters without the `memory-audit` feature need none and take the
[sync-only](docs/releases.md#sync-only-releases) path. Each adopter with it
can add `MEMORY_AUDIT_ANTHROPIC_API_KEY=<key>` to its primary checkout's
`.env` and run `chmod 600 .env`; no reinstall is needed. A project page that
names the old model or calls the audit subscription-only should be updated:
podhaven's `memoryAudit.context`, model-selection memory note, and scheduled
audit section, and screenr's `.env.example` and scheduled audit section.

### Verified

`bin/check` on macOS 27.0.1 with Python 3.15.1, and the starter checks on
Ubuntu and macOS. Claude Code 2.1.312 with a bogus `ANTHROPIC_API_KEY`
reported `authMethod: api_key` from `ANTHROPIC_API_KEY`, and its `-p`
stream-json run exited 1 with a result event marked `is_error`,
`api_error_status: 401`, and "Invalid API key · Fix external API key". The
credit and spend-limit shapes come from Claude Code's error handling and are
covered by tests with recorded events; no paid API call was made. QMD is
unchanged since 2.12.0's strict real-QMD smoke (QMD 2.8.3 with node-llama-cpp
3.22.2); this release does not rerun it.

## 3.2.0 — 2026-10-25

### Synced

- Optional features. `bin/sync --enable <feature>` and `--disable <feature>`,
  with or after `--init`, change the features an adopter's
  `.project-starter.json` lists. Sync manages an enabled feature's files like
  the bundle's and lists its page in `docs/foundation/README.md`. An adopter
  that enables none receives only the version bump, and `bin/sync --status`
  shows each adopter's features. A new file whose path holds a file sync does
  not manage is a conflict.
- The `memory-audit` feature shares screenr's weekly local Claude audit of
  memory notes: `bin/memory-audit`, its runner and prompt, and
  `docs/foundation/memory-audit.md`. An optional `memoryAudit` object in
  `.config/knowledge.json` sets the repository, LaunchAgent label, schedule,
  failure-issue labels, commit trailers, active-index heading, and prompt
  context; `bin/memory-audit settings` prints them. The defaults keep
  `com.<owner>.<repo>.memory-audit` from `origin`, Saturday 06:00, and the
  starter's `Active pages` heading. Unlike screenr's copy, the audit pushes
  to every push URL of `origin`, labels a new failure issue (unlabeled when
  the labels cannot be applied), skips the model when no note is active, and
  fails before the model when `memory/README.md` lacks the heading.
- Every project's audit defaults to the same time, and runs take turns
  through a per-user lock at `~/.cache/project-starter/memory-audit.lock`.
  A run waits for its turn, up to `lockWaitMinutes` (180 by default), before
  fetching evidence, and the wait does not count against the 90-minute model
  limit. A run that waits longer fails and reports like any other failure.

### Manual follow-up

Adopters that do not enable a feature need none and take the
[sync-only](docs/releases.md#sync-only-releases) path; screenr and podhaven
take the full path. Sync refuses `--enable memory-audit` while a project's
own audit files exist, so they remove theirs first, then keep the
`## Scheduled memory audit` heading, which their memory pages link to.

**screenr**

1. Delete `bin/memory-audit`, `bin/_memory_audit.py`,
   `bin/memory-audit-prompt.md`, and `tests/test_memory_audit.py`, and
   commit.
2. Run `bin/sync --enable memory-audit /path/to/screenr`.
3. Add its settings to `.config/knowledge.json`:

   ```json
   "memoryAudit": {
     "schedule": {"weekday": "Saturday", "hour": 8, "minute": 0},
     "issueLabels": ["bug", "area: tooling"],
     "commitTrailers": {
       "Screenr-Deploy": "skip",
       "Screenr-Deploy-Reason": "The weekly memory audit changes only memory notes, which do not run in production."
     },
     "indexHeading": "Active memory index"
   }
   ```

4. Shorten `docs/development-workflow.md#scheduled-memory-audit` to link
   `docs/foundation/memory-audit.md` and keep only Screenr's specifics: the
   Saturday 08:00 start, two hours after podhaven's, the deployment trailers,
   the labels, and the audit decisions.
5. Run `bin/check --full`, commit, and push. In the primary checkout, run
   `bin/memory-audit settings`, confirm the label is
   `com.jubishop.screenr.memory-audit`, and rerun `bin/memory-audit install`.

**podhaven**

1. Delete `bin/memory-audit`, `bin/_memory_audit.py`,
   `bin/memory-audit-prompt.md`, `bin/memory-index`, `bin/_memory_index.py`,
   `bin/tests/test_local_memory_audit.py`, and
   `bin/tests/test_memory_audit.py`, and drop the `bin/memory-index` call
   from the index-coverage test in `bin/tests/test_knowledge.py`.
2. Delete `bin/_checks.py` and its override in `.project-starter.json`, so
   sync restores the managed copy, and commit.
3. Run `bin/sync --enable memory-audit /path/to/podhaven`.
4. In `memory/README.md`, remove the `ACTIVE_MEMORY_START` and
   `ACTIVE_MEMORY_END` markers but keep the list, and replace the
   `bin/memory-index` paragraph with the hand-maintained rule: link each
   active note, and the audit removes an archived note's entry.
5. Add its settings to `.config/knowledge.json`; it keeps the default
   Saturday 06:00, and `context` carries the project paragraph its prompt
   had:

   ```json
   "memoryAudit": {
     "issueLabels": ["memory-audit-failure"],
     "indexHeading": "Active notes",
     "context": "The user selected this local Claude Code job with Haiku through their Claude subscription to replace the paid OpenRouter memory audit and the later Codex job. That choice supersedes older model preferences in the notes. The Sentry Feedback GitHub workflow remains in use."
   }
   ```

6. Shorten `docs/development-workflow.md#scheduled-memory-audit` to link
   `docs/foundation/memory-audit.md`, and make its Project Starter section
   name only the `bin/_knowledge.py` override.
7. Delete `bin/knowledge-config`: only the old audit and its own test in
   `bin/tests/test_knowledge.py` use it, and no workflow or doc does. Move
   that test's `sentry-history` `includeByDefault: false` assertion into the
   lookup test that records the rendered collections, so the override keeps
   coverage, drop the now unused `include_local` parameter from the override's
   `config()`, and remove "for CI configuration" from the override's reason.
8. Run `bin/check --full`, commit, and push. In the primary checkout, run
   `bin/memory-audit settings`, confirm the label is
   `com.jubishop.podhaven.memory-audit`, and rerun `bin/memory-audit install`.

### Verified

`bin/check` on macOS 27.0.1 with Python 3.15.1, and the starter checks on
Ubuntu and macOS. A real audit ran in podhaven. QMD is unchanged since
2.12.0's strict real-QMD smoke (QMD 2.8.3 with node-llama-cpp 3.22.2); this
release does not rerun it.

## 3.1.0 — 2026-10-25

### Synced

- `bin/check --full` reuses a passing `bin/check-application` run for a clean
  checkout whose tree and environment passed in the last 12 hours, and says
  which commit passed. The record lives in the common Git directory, so
  worktrees share it. Uncommitted changes always run the application checks,
  and `bin/check --full --no-reuse` runs them regardless. The engineering
  policy describes the reuse.
- A new worktree, and `bin/prep-worktree`, run the project's executable
  `bin/setup-application`, so a worktree gets its dependencies, such as a
  `.venv`, without an agent rebuilding them. A failure in a new worktree is
  reported without stopping Git; `bin/prep-worktree` fails with it.

### Manual follow-up

A project that overrides `bin/_checks.py` ports the application-check reuse
to its copy. One that overrides `bin/_knowledge.py` runs
`bin/setup-application` for new worktrees and in `bin/prep-worktree`, as the
release's `setup_application` does.

### Verified

`bin/check` on macOS 27.0 with Python 3.15.1, and the starter checks on
Ubuntu and macOS. QMD is unchanged since 2.12.0's strict real-QMD smoke (QMD
2.8.3 with node-llama-cpp 3.22.2); this release does not rerun it.

## 3.0.1 — 2026-10-25

### Synced

- New projects' `docs/README.md` describes the foundation as "shared
  engineering and knowledge search policy", without 3.0.0's stray comma.
  Existing adopters keep their own copy of that project-owned page.

### Manual follow-up

None.

## 3.0.0 — 2026-10-25

### Synced

- td task tracking is retired; projects track work in their issue tracker.
  Sync removes `docs/foundation/task-tracking.md`, the managed `AGENTS.md`
  block drops its td rule, the managed `.gitignore` block no longer ignores
  `.todos/`, and the foundation index no longer lists task tracking.

### Manual follow-up

- Remove td from the project-owned pages that 2.x installed: the td sentence
  in `docs/development-workflow.md`, the task-tracking item and the sentence
  about linking issues from td in `README.md`, the td clause in
  `docs/README.md` and `memory/README.md`, and "task tracking" in the
  `foundation` collection's context in `.config/knowledge.json`. Edit any
  other project page that tells agents to use td or cites td task IDs.
- Move any unfinished task's remaining work into an issue, then delete the
  primary checkout's `.todos/` directory.

### Verified

`bin/check` on macOS 27.0 with Python 3.15.1. QMD is unchanged since 2.12.0's
strict real-QMD smoke (QMD 2.8.3 with node-llama-cpp 3.22.2); this release
does not rerun it.

## 2.13.0 — 2026-10-25

### Synced

- When a flaky test's fix does not fit the current change, agents file a
  GitHub issue for it right away, without waiting to be asked, or reuse the
  one that already tracks it, and name the issue when reporting the work. The
  engineering policy states the rule, and the managed `AGENTS.md` block
  summarizes it.

### Manual follow-up

None.

## 2.12.0 — 2026-10-24

### Synced

- Each knowledge refresh whose inputs changed runs `qmd cleanup` after
  `qmd embed`, so the index no longer keeps embedding chunks for replaced or
  removed pages. Lookups during cleanup wait or refuse, as during the rest of
  a refresh, and a failed cleanup fails the refresh. The knowledge-search page
  describes this and how to reclaim the vector space cleanup cannot free.

### Manual follow-up

A project that overrides `bin/_knowledge.py` adds `cleanup` after `embed` to
its refresh's QMD commands. Optionally, to reclaim vector blocks that cleanup
cannot free, delete `.cache/qmd/index.sqlite` and run `bin/qmd-index`, which
rebuilds it.

### Verified

QMD 2.8.3 with node-llama-cpp 3.22.2 (strict real-QMD smoke on an Apple M5
Pro with macOS 27.0.1), td 0.69.0, and Python 3.15.1.

## 2.11.1 — 2026-10-24

### Synced

- A single-file collection whose file is missing indexes nothing instead of
  failing every refresh and lookup with "Collection readme file is missing".
  Tools that search a sparse copy of the checkout without the README, such
  as podhaven's memory audit, work again, and the knowledge-search page says
  so.

### Manual follow-up

From 2.10.x, apply the 2.11.0 follow-up. A project that overrides
`bin/_knowledge.py` merges both releases' changes into its copy. The fleet's
copies were updated directly on 2026-10-24.

## 2.11.0 — 2026-10-24

### Synced

- A knowledge collection's pattern may name one Markdown file instead of
  `**/*.md`. QMD then indexes only that file in the collection's directory,
  and search freshness tracks it alone. The knowledge-search page documents
  this, and new projects' `.config/knowledge.json` adds a `readme` collection
  for the root `README.md`, so search returns `qmd://readme/README.md`.

### Manual follow-up

`.config/knowledge.json` is project-owned, so sync does not add the
collection. Add it to `collections`:

```json
"readme": {
  "path": ".",
  "pattern": "README.md",
  "context": {"/": "The project's purpose, main entry points, and development setup."}
}
```

A collection rooted at `.` with `**/*.md` should list `README.md` in its
`ignore` to avoid indexing the file twice. Then run `bin/check` and
`bin/qmd-index`, and confirm that `bin/doctor --json` counts one `readme`
document. No adopter synced 2.11.0; the fleet moved to 2.11.1 directly.

### Verified

QMD 2.8.3 with node-llama-cpp 3.22.2 (strict real-QMD smoke on an Apple M5
Pro with macOS 27.0.1), td 0.69.0, and Python 3.15.1.

## 2.10.1 — 2026-10-16

### Synced

- The managed `AGENTS.md` secrets rule drops its `.env` example, leaving
  "Keep secrets out of public repositories only; a private one may commit
  them."

### Manual follow-up

None.

## 2.10.0 — 2026-10-16

### Synced

- The managed `AGENTS.md` block keeps secrets out of public repositories only.
  A private repository may commit them, such as its `.env` by adding `!.env`
  after the `.gitignore` block, which still ignores `.env` by default.

### Manual follow-up

None required. A private project that restated this exception outside the
block can remove its copy.

## 2.9.0 — 2026-10-16

### Synced

- Only the recorded release version. The remote page that new projects copy,
  `docs/git-remotes.md`, now records only the primary `origin` remote with no
  second push destination, and the starter README and docs index match it.

### Manual follow-up

None required. A project-owned `docs/git-remotes.md`, `docs/README.md`, or
`README.md` that still describes a second push destination should be updated;
the fleet's copies were updated directly on 2026-10-16.

## 2.8.1 — 2026-10-15

### Synced

- Only the recorded release version. Project Starter's QMD maintenance guide
  now names the home repository's updater `~/bin/auto-update`, its new name.

### Manual follow-up

None.

## 2.8.0 — 2026-10-15

### Synced

- The engineering policy sorts changes into three kinds. Text, such as
  Markdown and AI skill prose, goes directly to the default branch without
  checks. Development code, such as tests, CI, hooks, tooling, and skill
  scripts, goes directly after its checks pass. Production code goes through a
  pull request after its checks. This corrects 2.6.0, which let tests, CI, and
  tooling skip checks.
- The managed `AGENTS.md` block summarizes the three kinds, and
  "Changes outside the runtime" is now "Kinds of change".

### Manual follow-up

None required. A project page that links to
`engineering-policy.md#changes-outside-the-runtime`, or that exempts tests, CI,
or tooling from checks, should be updated.

## 2.7.0 — 2026-10-15

### Synced

- Agents never ignore a flaky test. They fix it on the spot or make sure a
  GitHub issue tracks it. The engineering policy states the rule, and the
  managed `AGENTS.md` block summarizes it.

### Manual follow-up

None.

## 2.6.0 — 2026-10-15

### Synced

- Changes outside the runtime, which can't affect what runs when the
  application executes, go directly to the default branch without checks,
  tests, CI waits, or a pull request. They include Markdown, docs, memory,
  agent instructions, AI skills, and tests, CI, and tooling the running
  application doesn't use. Markdown edits no longer need
  `bin/check --documents-only`.
- A project's own rules take precedence over the managed block and the
  foundation pages wherever they differ, stricter or looser, so a project can
  set its own edge cases. Previously only stronger project rules won.
- A Project Starter sync goes directly to the default branch as a change
  outside the runtime, no longer as a carve-out that overrides project rules.

### Manual follow-up

None required. A project page that still requires checks or a pull request
for changes outside the runtime keeps doing so, because project rules take
precedence; remove such a rule unless it is a deliberate exception.

## 2.5.0 — 2026-10-15

### Synced

- A Project Starter sync with no manual follow-up needs no checks, CI, or
  deployment. Its commit holds only the synced files and carries `[skip ci]`,
  so GitHub Actions starts no push workflows, and it is pushed directly.

### Manual follow-up

None.

## 2.4.1 — 2026-10-15

### Synced

- The task workflow no longer warns against rotating td sessions to bypass
  review checks. Agents approve their own work with `td approve --self-review`.

### Manual follow-up

None.

## 2.4.0 — 2026-10-15

### Synced

- A Project Starter sync may go directly to the default branch without a pull
  request or review, even where the project otherwise requires one. It covers
  the files `bin/sync` writes, `.project-starter.json`, and manual follow-up
  that touches only workflows or documentation.

### Manual follow-up

If the project's own instructions require pull requests for changes a sync
makes, add the same carve-out there, since project rules may be stricter than
the foundation.

## 2.3.0 — 2026-10-15

### Synced

- The engineering policy's runtime and toolchain section says workflows
  reference GitHub Actions by major tag, such as `actions/checkout@v7`, not
  by commit SHA, and install CI tools at their latest version. A job that
  holds deployment credentials pins each third-party action it runs to a
  commit SHA, with that reason beside the pin.

### Manual follow-up

In each workflow, replace commit-SHA and exact-version action references with
the action's current major tag, and install CI tools at their latest version.
In a job that holds deployment credentials, keep each third-party action
pinned to a commit SHA and add a comment giving that reason. New adoptions'
GitHub workflow uses `actions/checkout@v7`.

## 2.2.0 — 2026-10-14

### Synced

- The engineering policy's new hosted CI section skips hosted CI for
  Markdown-only changes with trigger-level `paths-ignore: ['**.md']`. Those
  changes merge on a passing `bin/check --documents-only`. Projects whose
  Markdown affects behavior re-include those pages through a `paths` filter.
- When hosted CI cannot run only because the Actions quota is exhausted or
  GitHub is rate limiting, a local `bin/check --full` pass on the delivered
  revision satisfies the merge or release gate. CI is reported as
  unavailable, not passed.

### Manual follow-up

Add `paths-ignore: ['**.md']` to the `push` and `pull_request` triggers of
workflows that run checks. If Markdown affects behavior, use a `paths` filter
of `'**'`, `'!**.md'`, then those pages. Do not make a path-filtered workflow
a required check. New adoptions' GitHub workflow includes the filter.

## 2.1.3 — 2026-10-13

### Project-owned template

- New adoptions' `docs/development-workflow.md` describes a project with no
  application yet: it has no `bin/check-application`, declares no application
  runtime, and deploys nothing, and each section says what to record when
  that changes. The README introduction asks a project without an
  application to say so. Only new adoptions receive these pages; sync never
  changes existing project-owned pages.

### Manual follow-up

None. The guide now explains that its links resolve from this repository and
where copied pages live in the target.

## 2.1.2 — 2026-10-09

### Project-owned template

- `docs/git-remotes.md` reads correctly once adoption fills in the actual URLs,
  and recommends SSH for GitHub because HTTPS pushes that change workflow files
  need a token with the `workflow` scope. Only new adoptions receive it; sync
  never changes existing project-owned pages.

## 2.1.1 — 2026-10-09

### Synced

- The engineering policy asks CI setup actions to check for the latest
  release (`check-latest: true`) instead of reusing a cached older one.

### Manual follow-up

Add `check-latest: true` beside `lts/*`, `stable`, or similar version
selectors in CI setup actions. New adoptions' GitHub workflow uses
`ubuntu-latest`.

## 2.1.0 — 2026-10-09

### Synced

- `bin/setup` runs an executable `bin/setup-application` after the foundation
  setup succeeds, so application dependencies install with one command.
- The engineering policy uses the latest stable runtimes and tools: projects
  declare minimum versions, CI installs the latest stable release (`lts/*` for
  Node), and machines and servers update automatically with rollback.
- `bin/doctor` no longer reports a tested QMD version or warns about newer
  releases.

### Manual follow-up

- Replace exact runtime pins: `engines` and similar fields declare minimums,
  version files say `lts/*`, CI installs `lts/*`, and application checks
  accept any version at or above the minimum.
- Move dependency installation from separate setup instructions into
  `bin/setup-application`.

## 2.0.1 — 2026-10-09

### Synced

- Hook setup messages and `bin/doctor` point to
  `docs/foundation/knowledge-search.md#existing-hooks` instead of the section
  that moved out of `docs/development-workflow.md` in 2.0.0.
- The managed `AGENTS.md` block restores the 1.x rule to keep accepted
  decisions separate from proposals, preserve unrelated changes, and keep
  secrets and generated caches out of Git.
- The check schedule states that a sync changing only managed files needs
  `bin/check`; the release's CI already tested that code.

### Manual follow-up

- Projects that override `bin/_knowledge.py` apply the same message change.
- Remove project copies of the restored `AGENTS.md` rule outside the block.
- Optionally remove `.gitignore` lines outside the block that duplicate block
  lines; the only negation they share, `!.env.example`, keeps its order inside
  the block.

## 2.0.0 — 2026-10-09

### Synced

- `bin/check` verifies managed files and blocks against the hashes in
  `.project-starter.json` in every mode. `--full` runs an executable
  `bin/check-application` after the foundation checks, instead of the copied
  foundation behavior tests.
- Shared policy moved into managed, condensed `docs/foundation/` pages:
  engineering policy, knowledge search, and task tracking.
- `AGENTS.md` and `.gitignore` carry managed blocks between
  `project-starter:begin` and `project-starter:end` markers.
- `bin/doctor` flags every QMD release except the exact tested version.
- Each refresh section in `.cache/qmd/index.log` starts with a timestamp and
  the QMD version.
- Task tracking installs upstream td from the `marcus/tap` Homebrew tap.
- `.project-starter.json` records only the version, source, release, managed
  hashes, and overrides.

Sync removes unchanged copies of `tests/test_knowledge.py`, because the
foundation tests now run only in Project Starter's CI, and of
`docs/task-tracking.md`, which moved to `docs/foundation/task-tracking.md`.
Changed copies are conflicts to review.

### Manual follow-up

- Move application checks from `bin/check` wrappers or `bin/_checks.py` into
  an executable `bin/check-application`.
- In `.config/knowledge.json`, add the `foundation` collection for
  `docs/foundation` and ignore `foundation/**` in the `docs` collection.
- Link `foundation/README.md` from `docs/README.md`, and repoint links that
  used `docs/task-tracking.md` or policy anchors in
  `docs/development-workflow.md`.
- Reduce `docs/development-workflow.md` to project-specific commands, and
  remove `AGENTS.md` rules that the managed block now covers.
- Record intentional managed-file changes as overrides with reasons, and
  merge 2.0 into those files by hand. A project that overrides a helper keeps
  its own tests for that variant.
- Preserve project-specific regression tests from the removed
  `tests/test_knowledge.py`, such as application-check wiring, as tests of
  `bin/check-application`.
- Update project tests that build fixtures from `.config/knowledge.json` or
  `.project-starter.json`: they now need `docs/foundation/` and the managed
  files those manifests reference. Repoint in-page anchors to moved sections;
  `bin/check` reports them.

### Verified

QMD 2.8.3 with node-llama-cpp 3.22.1 (strict real-QMD smoke on an Apple M5
Pro with macOS 27.0.1), td 0.66.0, and CI on Ubuntu 24.04 and macOS 15.

## 1.0.0 — 2026-09-04

Initial release. Adopters copied files by hand and recorded the starter
revision in `source_ref`; later partial updates added `knowledge_source_ref`
and `task_tracking_source_ref`. `bin/sync` uses those revisions to migrate.

# Changelog

Each release lists what `bin/sync` changes in adopters and the manual
follow-up it cannot apply. See [releases](docs/releases.md).

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

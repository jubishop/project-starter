# Changelog

Each release lists what `bin/sync` changes in adopters and the manual
follow-up it cannot apply. See [releases](docs/releases.md).

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
- Record intentional managed-file changes as overrides with reasons.

### Verified

QMD 2.8.3 with node-llama-cpp 3.22.1 (strict real-QMD smoke on an Apple M5
Pro with macOS 27.0.1), td 0.66.0, and CI on Ubuntu 24.04 and macOS 15.

## 1.0.0 — 2026-09-04

Initial release. Adopters copied files by hand and recorded the starter
revision in `source_ref`; later partial updates added `knowledge_source_ref`
and `task_tracking_source_ref`. `bin/sync` uses those revisions to migrate.

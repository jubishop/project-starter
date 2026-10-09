---
status: current
---

# Releases and fleet sync

Project Starter ships as semver tags. `bin/sync` installs a tagged release
into adopters, and the [changelog](../CHANGELOG.md) tells them what changed
and what needs manual follow-up. The decisions behind this process are in the
[template design](template-design.md#project-starter-20--2026-10-09).

## What sync manages

| Category | Files | Sync behavior |
| --- | --- | --- |
| Managed | Everything in `starter/` not listed below | Replaced each release; hashes recorded in `.project-starter.json` and verified by every `bin/check` mode. |
| Managed blocks | The marked sections of `AGENTS.md` and `.gitignore` | Only the text between the `project-starter:begin` and `project-starter:end` markers is replaced and hashed. |
| Project-owned | `README.md`, `docs/README.md`, `memory/README.md`, `docs/development-workflow.md`, `docs/git-remotes.md`, `.config/knowledge.json`, `.github/workflows/check.yml` | Copied by `--init` when missing, then never changed. |

A managed file that differs from its recorded hash is a conflict, and sync
writes nothing until it is resolved. Move the change into an extension point,
record an override with its reason in `.project-starter.json`, or discard it
with `--force`. Sync skips overridden files and reports upstream changes to
them. Add a new extension point once a second repository needs the same
override.

Version 1.x adopters recorded starter revisions instead of hashes. Sync treats
a file as unchanged when it matches the content at any recorded revision
(`source_ref`, `knowledge_source_ref`, or `task_tracking_source_ref`),
removes unchanged files the release no longer ships, and inserts the managed
blocks, placing the `AGENTS.md` block after the page title.

## Cut a release

1. Choose the version. A major release changes extension points or requires
   adopter action, a minor release adds features, and a patch fixes defects.
2. Set `version` in `starter/.project-starter.json`, and add a changelog entry
   with the synced changes, the manual follow-up, and the verified QMD, td,
   and platform versions.
3. Run `bin/check`, push `main`, and wait for the
   [starter checks](../.github/workflows/check.yml) to pass on Ubuntu and
   macOS.
4. Tag the commit `vX.Y.Z` and run `git push origin vX.Y.Z`; `origin` pushes
   to both GitHub and SourceHut.

## Sync the fleet

Run `bin/sync --status` to list adopters under `~/projects`. For each one,
starting from a clean, current checkout:

```sh
bin/sync --dry-run /path/to/project
bin/sync /path/to/project
```

Apply the changelog's manual follow-up, run `bin/check --full` there, commit
on its default branch, push to both hosts, and confirm CI for the pushed
commit. Rerun `bin/sync --status` to confirm that no adopter reports drift.
Coordinate a fleet-wide sync with a td task in the home database.

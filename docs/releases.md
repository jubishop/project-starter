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
| Features | Everything in `features/<name>/` except its `feature.json` | Managed like the bundle, but only in adopters whose `.project-starter.json` lists the feature; `--enable` and `--disable` change that list. The foundation index lists each enabled feature's page. |

A managed file that differs from its recorded hash is a conflict, and sync
writes nothing until it is resolved. Move the change into an extension point
(`bin/check-application` or `bin/setup-application`),
record an override with its reason in `.project-starter.json`, or discard it
with `--force`. Sync skips overridden files and reports upstream changes to
them. Add a new extension point once a second repository needs the same
override. A new managed or feature file whose path holds a file sync does not
manage is a conflict too; move or delete that file first.

Version 1.x adopters recorded starter revisions instead of hashes. Sync treats
a file as unchanged when it matches the content at any recorded revision
(`source_ref`, `knowledge_source_ref`, or `task_tracking_source_ref`),
removes unchanged files the release no longer ships, and inserts the managed
blocks, placing the `AGENTS.md` block after the page title.

## Sync-only releases

When a release needs no manual follow-up, or its follow-up applies only to
adopters that override a managed file or enable a feature, the other adopters
receive only what `bin/sync` writes. Follow-up for the adopters that enable a
feature, or that are moving to one, is handled like override-only follow-up. Ship it without checks, CI waits, deployments, or validation
records:

1. Set the version, add the changelog entry, commit, tag `vX.Y.Z`, and run
   `git push origin main vX.Y.Z`.
2. Fetch every adopter listed by `bin/sync --status`, then sync each one.
   Where no follow-up applies, commit only the synced files, with `[skip ci]`
   in the message so GitHub Actions starts no push workflows, and push.
3. Give each adopter with an override or feature that the follow-up applies
   to the [fleet sync](#sync-the-fleet) steps: apply the follow-up, run the
   checks it needs, push without `[skip ci]`, and confirm CI.
   `bin/sync --status` lists each adopter's overrides and features.

Sync only an adopter whose checkout is clean, on its default branch, and even
with its remote. A clean checkout that is only behind its remote, such as one
whose [memory audit](../features/memory-audit/docs/foundation/memory-audit.md)
pushed notes, fast-forwards first. Skip and report any other, and never force, stash, or push
someone else's commits. Report a rejected push, such as from enforced branch
protection, instead of bypassing it. Track each adopter left behind this way
in a GitHub issue in this repository, reusing an open one, so a later agent
finishes its sync without anyone having to remember it; the sync that brings
the adopter current closes the issue. Any other release with manual follow-up, including
an optional step for every adopter, uses the full process below.

## Cut a release

1. Choose the version. A major release changes extension points or requires
   adopter action, a minor release adds features, and a patch fixes defects.
2. Set `version` in `starter/.project-starter.json`, and add a changelog entry
   with the synced changes, the manual follow-up, and the verified QMD and
   platform versions.
3. Run `bin/check`, push `main`, and wait for the
   [starter checks](../.github/workflows/check.yml) to pass on Ubuntu and
   macOS.
4. Tag the commit `vX.Y.Z` and run `git push origin vX.Y.Z`.

## Sync the fleet

Invoke the [sync-fleet skill](../.agents/skills/sync-fleet/SKILL.md) from
this repository to sync every adopter by this section or
[sync-only releases](#sync-only-releases).

Run `bin/sync --status` to list adopters under `~/projects`. For each one,
starting from a clean, current checkout:

```sh
bin/sync --dry-run /path/to/project
bin/sync /path/to/project
```

Apply the changelog's manual follow-up, run the checks it needs there (none
when it changes only text), commit
on its default branch, push, and confirm CI for the pushed
commit. When the Actions quota blocks CI, follow
[hosted CI](../starter/docs/foundation/engineering-policy.md#hosted-ci). Rerun `bin/sync --status` to confirm that no adopter reports drift.

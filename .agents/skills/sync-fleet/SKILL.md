---
name: sync-fleet
description: >-
  Bring every Project Starter adopter up to the latest release: sync it, apply
  the release's manual follow-up, commit, push, and confirm CI where the
  release process requires it. Use when the user asks to sync or roll out
  Project Starter to its adopters.
user_invocable: true
disable-model-invocation: true
argument: Optional adopter names to sync instead of every adopter
---

# Sync the Fleet

Leave every adopter that `bin/sync --status` lists on the latest release, with
no drift, its manual follow-up applied, and the result pushed. With adopter
names, sync only those. [Releases and fleet sync](../../../docs/releases.md)
is the authoritative process, and [update an
adopter](../../../GUIDE.md#update-an-adopter) covers each one. Read both, and
the [changelog](../../../CHANGELOG.md) entry for every release an adopter is
behind, before changing anything.

## Start from current sources

Work from this repository's primary checkout, with `main` and its tags even
with the remote. If the checkout has local work or cannot fast-forward, stop
and report it. If `starter/` or `extras/` on `main` differs from the latest
release tag, show the unreleased changes and ask whether to cut a release with
them first.

## Sync each adopter

Take each adopter down the sync-only or full fleet path, whichever the release
process gives it. An adopter several releases behind needs the follow-up of
every release it skipped. Its own agent instructions take precedence when it
commits, checks, or pushes.

The release process's rules for adopters to skip and actions never to take
are binding. Report a sync conflict with its local change and the guide's
options, and pass `--force` only on the user's choice.

## Finish

Rerun `bin/sync --status` to confirm that no adopter is behind or drifting
beyond those reported. Report each adopter's outcome: synced and pushed (with
CI results where required), already current, or skipped and why. File or
reuse the release process's issue for each adopter left behind, and close the
issue of each adopter this run brought current. When an adopter
reveals a reusable gap, follow [propose starter
improvements](../../../GUIDE.md#propose-starter-improvements).

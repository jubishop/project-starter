# Apply Project Starter

Use this checklist when adopting Project Starter in a repository or updating
an adopter. `bin/sync` in this repository copies files and records their
hashes; these steps cover the judgment it cannot apply. Read the guide on
request; do not install it as a skill or load it automatically.

Links in this guide resolve from this repository. Sync copies each page under
`starter/` to the same path in the target without that prefix, so
`starter/docs/git-remotes.md` becomes `docs/git-remotes.md`, and likewise
for an enabled feature's pages under `features/<name>/`; read the target's
copy when working there. The changelog, `bin/sync`, and `bin/smoke-qmd` exist
only here, and the other `bin/` commands run in the target.

## Adopt a repository

1. **Inspect the target.** Confirm its path, branch, and a clean working tree.
   Read its agent instructions and applicable parent instructions, such as
   `~/AGENTS.md`, plus its README, setup and check commands, CI, hooks
   (including local and global `core.hooksPath`), environment files,
   toolchain declarations, and issue tracker.
2. **Run sync** from a checkout of this repository:

   ```sh
   bin/sync --init --dry-run /path/to/project
   bin/sync --init /path/to/project
   ```

   Sync copies the latest release: managed files, the managed blocks in
   `AGENTS.md` and `.gitignore`, and any project-owned pages that do not exist
   yet. It keeps and reports existing project-owned files, and it never
   commits. Add `--enable <feature>` to install an
   [optional feature](#enable-or-disable-a-feature) too.
3. **Merge project-owned pages.** Fold starter guidance into an existing
   README and knowledge indexes, keep useful existing content, and link
   `foundation/README.md` from `docs/README.md`. The copied
   `docs/development-workflow.md` describes a project with no application
   yet; keep that wording only when it is true, and otherwise record the
   project's actual checks, runtime minimums, and deployment.
4. **Tailor `AGENTS.md`.** Leave the managed block intact. Below it, keep
   project commands, stronger requirements, and intentional exceptions, and
   remove rules that the block or applicable inherited instructions already
   cover. A runtime that needs another filename should reference `AGENTS.md`.
5. **Wire application checks.** Put application typechecking, lint, tests, and
   builds in an executable `bin/check-application`, which only
   `bin/check --full` runs. Point CI at `bin/check --full`, skipping
   Markdown-only changes as
   [hosted CI](starter/docs/foundation/engineering-policy.md#hosted-ci)
   describes. Confirm that the routine modes start no application tools, that
   `--full` runs them after the foundation checks, and that failures
   propagate. Time the routine modes.
   Put dependency installation, such as `npm ci`, in an executable
   `bin/setup-application`, which `bin/setup` runs after the foundation setup
   and each new worktree runs when Git creates it.
6. **Integrate hooks.** Setup activates `bin/hooks` when nothing would be
   displaced. Otherwise follow
   [existing hooks](starter/docs/foundation/knowledge-search.md#existing-hooks)
   and verify each event in a disposable checkout.
7. **Configure knowledge.** Adjust collections and deliberate exclusions in
   `.config/knowledge.json`, keeping personal paths in local Git
   configuration. Keep or add the `readme` collection, which indexes only the
   root `README.md`; a collection rooted at `.` with `**/*.md` should ignore
   `README.md` so it is not indexed twice. Bring existing pages into the
   documented formats, and do not invent memories.
8. **Verify.** Run `bin/setup`, `bin/check --full`, and `bin/doctor`. With QMD,
   search for a distinctive term from the tailored root README, expecting
   `qmd://readme/README.md`, and for one from a real `docs/` or `memory/`
   page, and read each result.
   `bin/smoke-qmd --project /path/to/project` exercises a snapshot with real
   QMD. Report missing optional tools as skipped features, and check CI for
   the pushed commit.
9. **Set up the remote for new hosted projects.** After the first commit and
    checks, follow [Git remote setup](starter/docs/git-remotes.md) to publish
    to the primary host. Adopting an existing repository does not authorize
    adding a host or changing visibility.
10. **Report** changes, checks actually run, skipped features, and overrides.
    Commit and push according to the user's request and the repository's rules.

## Update an adopter

On a clean checkout, run `bin/sync --dry-run /path/to/project`, then
`bin/sync /path/to/project`. A conflict means a managed file has local
changes, or that a new file would replace one sync does not manage. Move the change into an extension point (`bin/check-application`,
`bin/setup-application`, project pages, or the project section of `AGENTS.md`), record an override with
its reason in `.project-starter.json`, or discard it with `--force`. Apply the
release's manual follow-up from the [changelog](CHANGELOG.md), run
`bin/check --full`, and commit. An adopter skips the check and deployment
when the release has no manual follow-up, or when the release's follow-up
applies only to overrides the adopter lacks; see [sync-only releases](docs/releases.md#sync-only-releases). `bin/sync --status` reports each adopter's
version, drift, overrides, and features.

## Enable or disable a feature

Optional features live in `features/<name>/` here, laid out at adopter paths.
Sync installs a feature's files only in adopters that enable it, then manages
them like the rest of the bundle: it records their hashes, `bin/check`
verifies them, and releases update them. It also lists the feature's page in
`docs/foundation/README.md`. Adopters that do not enable a feature never
receive its files.

| Feature | What it adds |
| --- | --- |
| `memory-audit` | A weekly local Claude audit of memory notes that commits validated changes and reports failures in a GitHub issue; macOS and GitHub only. See [its page](features/memory-audit/docs/foundation/memory-audit.md). |

On a clean checkout:

```sh
bin/sync --enable memory-audit /path/to/project
bin/sync --disable memory-audit /path/to/project
```

Both repeat for several features and combine with `--init` and `--dry-run`.
`.project-starter.json` lists the enabled features, and later syncs keep
them. Disabling removes the feature's unchanged files and refuses, as a
conflict, to remove changed ones. Review the feature's page for its setup,
such as `bin/memory-audit install`, and its settings, and stop anything it
scheduled before disabling it.

A feature file whose path already holds a file that sync does not manage, such
as a project's own copy of the audit, is a conflict, and sync writes nothing.
Delete or move that copy and commit, then sync with `--enable`. To migrate a
project-owned memory audit, delete its `bin/memory-audit`,
`bin/_memory_audit.py`, `bin/memory-audit-prompt.md`, and tests, enable the
feature, move its schedule, labels, and other differences into the
`memoryAudit` settings, point the project's docs at
`docs/foundation/memory-audit.md`, and rerun `bin/memory-audit install`.

## Propose starter improvements

When adoption reveals a reusable gap, finish the target work first. Then
describe the observed problem, the proposed change, why it belongs here, and
how to verify it, and ask before editing this repository or opening a pull
request. Approval to edit does not include publishing, and approval to open a
pull request does not include merging it. Turn a repeated override into an
extension point once a second repository needs it.

The guide and starter are [MIT licensed](LICENSE); keep
`LICENSE.project-starter` with copied files.

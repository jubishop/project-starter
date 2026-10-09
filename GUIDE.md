# Apply Project Starter

Use this checklist when adopting Project Starter in a repository or updating
an adopter. `bin/sync` in this repository copies files and records their
hashes; these steps cover the judgment it cannot apply. Read the guide on
request; do not install it as a skill or load it automatically.

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
   commits.
3. **Merge project-owned pages.** Fold starter guidance into an existing
   README and knowledge indexes, keep useful existing content, and link
   `foundation/README.md` from `docs/README.md`. Record the project's actual
   commands in `docs/development-workflow.md`.
4. **Tailor `AGENTS.md`.** Leave the managed block intact. Below it, keep
   project commands, stronger requirements, and intentional exceptions, and
   remove rules that the block or applicable inherited instructions already
   cover. A runtime that needs another filename should reference `AGENTS.md`.
5. **Wire application checks.** Put application typechecking, lint, tests, and
   builds in an executable `bin/check-application`, which only
   `bin/check --full` runs. Point CI at `bin/check --full`. Confirm that the
   routine modes start no application tools, that `--full` runs them after the
   foundation checks, and that failures propagate. Time the routine modes.
6. **Integrate hooks.** Setup activates `bin/hooks` when nothing would be
   displaced. Otherwise follow
   [existing hooks](starter/docs/foundation/knowledge-search.md#existing-hooks)
   and verify each event in a disposable checkout.
7. **Configure knowledge.** Adjust collections and deliberate exclusions in
   `.config/knowledge.json`, keeping personal paths in local Git
   configuration. Bring existing pages into the documented formats, and do
   not invent memories.
8. **Set up tasks.** Install td and run `td init` in the primary checkout, per
   [task tracking](starter/docs/foundation/task-tracking.md).
9. **Verify.** Run `bin/setup`, `bin/check --full`, and `bin/doctor`. With QMD,
   search for a distinctive term from a real page and read the result.
   `bin/smoke-qmd --project /path/to/project` exercises a snapshot with real
   QMD. Report missing optional tools as skipped features, and check CI for
   the pushed commit.
10. **Set up remotes for new hosted projects.** After the first commit and
    checks, follow [Git remote setup](starter/docs/git-remotes.md) to add a
    private SourceHut repository with dual pushes. Adopting an existing
    repository does not authorize adding a host or changing visibility.
11. **Report** changes, checks actually run, skipped features, and overrides.
    Commit and push according to the user's request and the repository's rules.

## Update an adopter

On a clean checkout, run `bin/sync --dry-run /path/to/project`, then
`bin/sync /path/to/project`. A conflict means a managed file has local
changes. Move the change into an extension point (`bin/check-application`,
project pages, or the project section of `AGENTS.md`), record an override with
its reason in `.project-starter.json`, or discard it with `--force`. Apply the
release's manual follow-up from the [changelog](CHANGELOG.md), run
`bin/check --full`, and commit. `bin/sync --status` reports each adopter's
version, drift, and overrides.

## Propose starter improvements

When adoption reveals a reusable gap, finish the target work first. Then
describe the observed problem, the proposed change, why it belongs here, and
how to verify it, and ask before editing this repository or opening a pull
request. Approval to edit does not include publishing, and approval to open a
pull request does not include merging it. Turn a repeated override into an
extension point once a second repository needs it.

The guide and starter are [MIT licensed](LICENSE); keep
`LICENSE.project-starter` with copied files.

# Apply Project Starter

Use this checklist when adopting Project Starter in a repository or updating
an adopter. `bin/sync` in this repository copies files and records their
hashes; these steps cover the judgment it cannot apply. Read the guide on
request; do not install it as a skill or load it automatically.

Links in this guide resolve from this repository. Sync copies each page under
`starter/` to the same path in the target without that prefix, so
`starter/docs/git-remotes.md` becomes `docs/git-remotes.md`; read the
target's copy when working there. The changelog, `bin/sync`, and
`bin/smoke-qmd` exist only here, and the other `bin/` commands run in the
target.

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
   commits. When it warns that a public GitHub repository lacks secret
   scanning or push protection, enable both as
   [secret scanning](docs/releases.md#secret-scanning) describes.
3. **Merge project-owned pages.** Fold starter guidance into an existing
   README and knowledge indexes, keep useful existing content, and link
   `foundation/README.md` from `docs/README.md`. The copied
   `docs/development-workflow.md` describes a project with no application
   yet; keep that wording only when it is true, and otherwise record the
   project's actual checks, runtime minimums, and deployment. When the
   project deploys on push and decides from every commit since its last
   deployment, record its deploy-skip trailers in `.project-starter.json` as
   its [sync commit trailers](docs/releases.md#sync-commit-trailers) and for
   the home guidance review, as the
   [engineering policy](starter/docs/foundation/engineering-policy.md#deployment-decisions)
   says.
4. **Tailor `AGENTS.md`** below the managed block with the `edit-agents-md`
   skill, also removing project rules the block already covers. A runtime
   that needs another filename should reference `AGENTS.md`.
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
   displaced, and keeps a `core.hooksPath` that names another checkout's
   [shared hooks](starter/docs/foundation/knowledge-search.md#shared-hooks)
   in the same clone. Otherwise follow
   [existing hooks](starter/docs/foundation/knowledge-search.md#existing-hooks)
   and verify each event in a disposable checkout. Move a project's own
   `pre-push` checks into an executable `bin/pre-push-application`, which
   the managed [pre-push hook](starter/docs/foundation/engineering-policy.md#pre-push-hook)
   runs after the document checks pass.
7. **Configure knowledge.** Adjust collections and deliberate exclusions in
   `.config/knowledge.json`; every collection stays inside the checkout.
   Keep or add the `readme` collection, which indexes only the
   root `README.md`; a collection rooted at `.` with `**/*.md` should ignore
   `README.md` so it is not indexed twice. Bring existing pages into the
   documented formats, and do not invent memories.
8. **Verify.** Run `bin/setup`, `bin/check --full`, and `bin/doctor`, which
   fail when a [required tool](starter/docs/foundation/knowledge-search.md#required-tools)
   is missing. Search for a distinctive term from the tailored root README,
   expecting `qmd://readme/README.md`, and for one from a real `docs/` or
   `memory/` page, and read each result.
   `bin/smoke-qmd --project /path/to/project` exercises a snapshot with real
   QMD. Check CI for the pushed commit.
9. **Set up the remote for new hosted projects.** After the first commit and
    checks, follow [Git remote setup](starter/docs/git-remotes.md) to publish
    to the primary host. Adopting an existing repository does not authorize
    adding a host or changing visibility. For a public GitHub repository, run
    `bin/sync --dry-run /path/to/project` once the remote exists, and enable
    [secret scanning](docs/releases.md#secret-scanning) if it warns.
10. **Report** changes, checks actually run, and overrides.
    Commit and push according to the user's request and the repository's rules.

## Update an adopter

On a clean checkout, run `bin/sync --dry-run /path/to/project`, then
`bin/sync /path/to/project`. A conflict means a managed file has local
changes, or that a new file would replace one sync does not manage. Move the change into an extension point (`bin/check-application`,
`bin/setup-application`, `bin/pre-push-application`, project pages, or the project section of `AGENTS.md`), record an override with
its reason in `.project-starter.json`, or discard it with `--force`. Apply the
release's manual follow-up from the [changelog](CHANGELOG.md), enable
[secret scanning](docs/releases.md#secret-scanning) if sync warns, run
`bin/check --full`, or only `bin/check --documents-only` when the follow-up
changes only text, and commit. An adopter skips the check and deployment
when no manual follow-up applies to it; see
[sync-only releases](docs/releases.md#sync-only-releases).
Its sync-only commit carries `[skip ci]` and, in the message's final trailer
paragraph, any deploy-skip trailers the adopter records as its
[sync commit trailers](docs/releases.md#sync-commit-trailers) in
`.project-starter.json`, which `bin/sync` prints after the sync.
`bin/sync --status` reports each adopter's
version, drift, overrides,
[imports of managed modules](docs/releases.md#imports-of-managed-modules),
and [tests that run managed scripts](docs/releases.md#tests-that-run-managed-scripts).

## Improve the starter

When adopting or syncing a repository reveals a reusable gap in the starter,
finish the target work first, then act on the gap as `~/AGENTS.md`'s
Improvement rule says. Turn a repeated override into an extension point once
a second repository needs it.

The guide and starter are [MIT licensed](LICENSE); keep
`LICENSE.project-starter` with copied files.

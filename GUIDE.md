# Apply the project foundation

Use this guide when a user points an agent at this repository to set up
project memory, docs, local search, Git hooks, and worktrees. Read it on
request. Do not install a skill or register it for automatic loading.

Copyable files are in [starter](starter/). Read the target project's
instructions first. Inspect files when they can answer a question; ask the
user only about material choices that cannot be inferred from the project.

## 1. Inspect the target

Confirm the target path, Git state, branch, and uncommitted changes. Identify
existing agent instructions, README, memory, docs, setup/check commands,
environment configuration, hooks, and task tracker. Determine the effective
hook directory, including local/global `core.hooksPath` and executable hooks
in Git's default directory.

Use the existing application stack, Git host, and task tracker. They are
independent of this foundation. A local-only repository can choose its own
task tracking tool; keep temporary progress out of durable memory and docs.
Create an external repository or change its visibility only when that action
is part of the user's request.

## 2. Adopt the bundle

Obtain the files from a checked-out release or source revision, including
hidden files. Copy from `starter/`, whose contents belong at the target root.
Do not copy this repository's `.git` or its maintainer-only files.

| Files | How to apply them |
| --- | --- |
| `AGENTS.md` | Merge the short instructions into existing guidance. Keep detailed policies in the memory/docs indexes. |
| `README.md` | Replace the generic introduction; add the task tracker and application commands. Preserve useful existing content. |
| `memory/README.md`, `docs/README.md` | Establish knowledge rules and active indexes. Do not invent initial memories. |
| `docs/development-workflow.md` | Adapt it to the actual commands and integrations delivered. |
| `bin/`, `tests/test_knowledge.py` | Add helpers and foundation tests; integrate existing setup/check commands and hooks. |
| `.config/knowledge.json` | Configure collections, descriptions, and deliberate check exclusions. Keep personal paths in local Git settings. |
| `.gitignore` | Merge exclusions with the project's existing file. |
| Optional `.envrc` | Create only when the project needs environment settings. Preserve useful existing settings; search does not need this file or shell-wide cache exports. |
| `.project-starter.json` | Record the copied release; set `source_ref` to its exact commit when copying an unreleased revision. |
| `LICENSE.project-starter` | Retain the license notice with copied material. |

For an empty target, copy the full bundle. For an existing target, merge
shared files and preserve application behavior. If setup or checks already
exist, retain the foundation entry point under a suitable name and call it
from the existing command. Adapt the workflow document and test fixtures to
those names. Keep disposable tests independent of production services and
private data.

If a runtime requires a different instructions filename, use its supported
mechanism to reference the maintained `AGENTS.md`. Preserve existing runtime
instructions. Do not duplicate this guide into automatically loaded context.

Preserve useful existing knowledge and evidence. Bring ordinary pages into
the documented formats, repair moved links, and maintain active indexes.
PR review records retain their own schema. Exclude generated docs deliberately
instead of changing their generated content by hand.

## 3. Integrate hooks and environment setup

The bundle supplies `post-checkout`, `post-commit`, `post-merge`, and
`post-rewrite`. If no existing hooks would be displaced, setup activates them.
Otherwise integrate through the existing manager using the
[hook instructions](starter/docs/development-workflow.md#existing-hooks),
then set `knowledge.hooks` to `external` in local Git configuration.

Preserve arguments, stdin, exit status, and existing hook behavior. Do not
replace a hook manager just to activate search. Verify both behaviors through
real events in an appropriate disposable checkout.

Review environment changes before allowing `.envrc`. A new worktree's file
is approved automatically only when it exactly matches an already trusted
primary checkout file. Integrate application-specific worktree preparation
with isolation appropriate to the project.

## 4. Configure knowledge and search

- `memory/`: durable guidance, corrections, incidents, and external context
  that cannot be recovered cheaply from current source.
- `docs/`: designs, decisions, research, and reference guides. Use `draft`,
  `current`, `superseded`, or `archived` for document lifecycle.
- The task tracker: actionable work and implementation progress.

Use clear titles, opening summaries, and short QMD collection descriptions.
Separate accepted decisions from proposals. Record sources and useful
verification dates for changing external facts; review them when related
work depends on them.

Home memory is excluded by default. Configure `knowledge.homeMemoryPath`
locally only if the user wants it included. Each checkout has its own index;
model files are shared while preserving existing cache choices.

## 5. Set up and verify the result

Run the integrated setup, checks, and diagnostics. In an unmodified bundle:

```sh
bin/setup
bin/check
bin/doctor
```

Report missing optional QMD or direnv as skipped features. Diagnose an
installed but failing tool. Confirm effective hooks and actual QMD paths;
tracked hook files alone do not prove activation.

The copied tests use disposable repositories and simulated tools. They cover
metadata, indexes, links, existing hooks, missing dependencies, search routing,
concurrency, failures, and worktree isolation. Preserve these checks when
adding application validation.

When QMD is available, refresh and verify a distinctive term from a real
project document, a focused read, and collection exclusions. The source
repository's `bin/smoke-qmd` provides an isolated real-QMD test using available
models. Do not claim real-QMD validation from simulated-tool tests. Record
the platforms and versions actually tested.

Use a disposable worktree to verify target-specific integration. Confirm a
separate database, intended model sharing, and preserved hooks. Check its
changes and running processes before cleanup, then verify `git worktree list`.
Do not use production ports, data, or restart commands for disposable tests.

For GitHub projects, copy or merge the optional
[workflow](extras/github/.github/workflows/check.yml) into
`.github/workflows/check.yml`. Adapt its branch, runner, dependencies, and
check command to the target. Preserve existing application checks and avoid
adding a second workflow that repeats them. Keep read-only permissions and
disable persisted checkout credentials unless the job needs write access.

Link to the delivered workflow from the project's development docs. The
copied foundation tests include `.github/` when present so those links work
inside disposable repositories. If adapted docs link to other project files,
include those required files in the test fixtures as well. Run the full
`bin/check` after adding the workflow; document-only checks do not exercise
the test fixtures. Use actionlint to validate workflow syntax when available.

After an authorized push, verify the workflow result for the exact pushed
commit. Report a pending, skipped, or failed run explicitly. Passing local
checks does not establish that runner setup or CI passed. The starter's own
CI checks both the base bundle and GitHub integration on macOS and Linux;
QMD is simulated there. Other CI systems can invoke the same check command.

Deliver a short report of changes, adaptations, checks actually run, and
skipped optional features. Commit or publish according to the user's request
and the target repository's rules.

## Maintenance

Copied files belong to the project. There is no updater, service, or runtime
dependency on this repository. Compare the recorded starter revision with a
chosen release, merge relevant improvements, update `.project-starter.json`,
and rerun checks.

The guide and starter are [MIT licensed](LICENSE). Retain the included notice;
do not replace the target project's own license.

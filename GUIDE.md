# Apply the project foundation

Use this guide when a user points an agent at this repository to set up
project memory, docs, local search, Git hooks, worktrees, and local task tracking. Read it on
request. Do not install a skill or register it for automatic loading.

Copyable files are in [starter](starter/). Read the target project's
instructions first. Inspect files when they can answer a question; ask the
user only about material choices that cannot be inferred from the project.

## 1. Inspect the target

Confirm the target path, Git state, branch, and uncommitted changes. Identify
existing agent instructions, README, memory, docs, setup/check commands,
environment configuration, supported toolchains, hooks, and task tracker.
Read `~/AGENTS.md` when present, along with other instructions that apply to
the target. Respect their scope: rules limited to the home repository do not
cover nested projects.
Identify the local validation commands and whether full CI is an enforced
merge or release gate. Determine the effective
hook directory, including local/global `core.hooksPath` and executable hooks
in Git's default directory.

Use the existing application stack, Git host, and shared issue tracker. Add
`td` for work with multiple stages, interruptions, blockers, or agent handoffs.
Make tasks optional for straightforward work completed in one session. Agents
must inspect and reuse relevant tasks, record meaningful checkpoints, and keep
the current handoff accurate. Task statuses record actual checks and review;
they do not add a separate review gate. Link related shared issues from td;
preserve their scope and acceptance criteria without importing the entire
backlog. Keep temporary progress out of durable memory and docs.
When the user requests a new hosted project, include a private SourceHut
repository and configure ordinary pushes to reach both the primary host and
SourceHut. Use the same project name and infer the SourceHut account from the
user's existing remotes or account information; ask only if it is unknown.
The SourceHut account name can differ from the primary host's account name.
Honor explicit host, visibility, or local-only choices. Adopting the foundation
in an existing project does not by itself authorize adding another host or
changing repository visibility. Follow the [remote setup](#new-project-remotes)
after validation and before the first delivery is complete.

## 2. Adopt the bundle

Obtain the files from a checked-out release or source revision, including
hidden files. Copy from `starter/`, whose contents belong at the target root.
Do not copy this repository's `.git` or its maintainer-only files.

| Files | How to apply them |
| --- | --- |
| `AGENTS.md` | Merge with existing guidance, then remove or shorten rules already covered by applicable home or parent instructions. Keep detailed policies in the memory/docs indexes. |
| `README.md` | Replace the generic introduction; add the task tracker and application commands. Preserve useful existing content. |
| `memory/README.md`, `docs/README.md` | Establish knowledge rules and active indexes. Do not invent initial memories. |
| `docs/development-workflow.md` | Adapt it to the actual commands and integrations delivered. |
| `docs/task-tracking.md` | Add the td workflow and preserve the boundary with the existing shared issue tracker. |
| `docs/git-remotes.md` | Record the actual primary and SourceHut URLs, private SourceHut setup, and how fresh clones restore dual pushes. Adapt or omit this page when the user selects another hosting arrangement. |
| `bin/`, `tests/test_knowledge.py` | Add helpers and foundation tests; integrate existing setup/check commands and hooks. |
| `.config/knowledge.json` | Configure collections, descriptions, and deliberate check exclusions. Keep personal paths in local Git settings. |
| `.gitignore` | Merge exclusions with the project's existing file. |
| Optional `.envrc` | Create only when the project needs environment settings. Preserve useful existing settings; search does not need this file or shell-wide cache exports. |
| `.project-starter.json` | Record the copied release; set `source_ref` to its exact commit when copying an unreleased revision. |
| `LICENSE.project-starter` | Retain the license notice with copied material. |

Treat `starter/AGENTS.md` as a baseline to adapt. Compare the meaning of its
rules and the target's existing rules with the applicable instructions read
above. Prune redundant guidance from the resulting local `AGENTS.md`, including
pre-existing repetition. When a paragraph adds only one project-specific
requirement, keep that requirement and remove the repeated general guidance.
Retain project commands, paths, policy links, stronger requirements, and
intentional exceptions where they add information.

The policy requirements below may be met by applicable inherited instructions;
they do not each require a local copy. Keep local coverage where inherited
guidance is absent or insufficient. This adaptation changes the target's
instructions, not `~/AGENTS.md`, and does not copy personal home settings into
the project.

For an empty target, copy the full bundle. For an existing target, merge
shared files and preserve application behavior. If setup or checks already
exist, retain the foundation entry point under a suitable name and call it
from the existing command. Adapt the workflow document and test fixtures to
those names. Keep disposable tests independent of production services and
private data.

Keep the copied check modes when integrating application commands:
`bin/check` runs only foundation static checks, `bin/check --documents-only`
checks Markdown, and `bin/check --full` adds foundation behavior tests and
application validation. Do not add application typechecking, lint, tests,
builds, or package-manager startup to either routine mode, even if a command
seems fast in isolation. Run relevant application checks explicitly during
code work. Forward the options through existing wrappers; application commands
must run only when `--full` is present and the foundation checks pass. Update
existing CI commands to use `--full` in the same change.

Adapt the engineering policies to the target's existing stack and commands.
Keep concise requirements in the effective agent instructions, with links to
the detailed policies in the copied `docs/development-workflow.md`:

- Prefer fewer dependencies and justify additions by their concrete benefits:
  [dependency policy](starter/docs/development-workflow.md#third-party-dependencies).
- Require automated tests for regression fixes and functional changes, using
  red-green TDD when practical. Test observable behavior through public
  interfaces, with fakes at external-system boundaries:
  [testing policy](starter/docs/development-workflow.md#test-driven-development).
- Keep test cost proportional while preserving coverage and independence:
  [test cost and coverage](starter/docs/development-workflow.md#test-cost-and-coverage).
- Keep source files cohesive and use approximately 1,000 lines as a review
  threshold: [file organization](starter/docs/development-workflow.md#file-organization).
- Keep Markdown pages focused on one topic or reader task, without numeric
  size limits: [Markdown guidance](starter/docs/development-workflow.md#markdown-pages).
  Retain links to this policy from the memory and docs indexes.
- Scope validation inputs and mutable output to the intended checkout:
  [checkout isolation](starter/docs/development-workflow.md#validation-checkout-isolation).
- Declare compatible supported runtime and toolchain versions:
  [version policy](starter/docs/development-workflow.md#runtime-and-toolchain-versions).
  Keep foundation checks independent of unused application runtimes.
- Choose checks by changed files, reuse passing results until inputs change,
  and require successful full validation before merge or release:
  [validation schedule](starter/docs/development-workflow.md#checks-and-project-extensions).

Preserve stronger project requirements. Use the linked policies for details
and exceptions; avoid reproducing them in the target's `AGENTS.md`.

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
- `td`: resumable progress, blockers, and handoffs for work that needs continuity.
- The existing shared issue tracker: shared scope and acceptance criteria,
  linked from local td tasks when applicable.

Use clear titles, opening summaries, and short QMD collection descriptions.
Separate accepted decisions from proposals. Record sources and useful
verification dates for changing external facts; review them when related
work depends on them.

Home memory is excluded by default. Configure `knowledge.homeMemoryPath`
locally only if the user wants it included. Each checkout has its own index;
model files always use `~/.cache/qmd/models`. Setup creates it and QMD downloads
missing weights on first use. See the [migration rules](starter/docs/development-workflow.md#worktrees)
before removing obsolete cache directories. Do not put indexes in the shared cache.

Keep refresh checks stable across shell commands and Git hooks. QMD
subprocesses must not inherit Git repository selectors. Use the QMD release
version for freshness; its optional Git commit suffix can identify an
unrelated repository. Keep the regression tests for this behavior when
adapting the helpers. See [refresh and recovery](starter/docs/development-workflow.md#refresh-and-recovery).

Preserve lookup freshness enforcement: refresh stale inputs before searching,
bound the automatic wait, and return no results if refresh or lookup fails or
the inputs change during the lookup. Keep progress on stderr. Test these
failure and recovery paths when adapting the command.

Include the [search failure policy](starter/docs/development-workflow.md#search-failures)
in the target's agent instructions: report configured QMD failures immediately,
attempt repair, and pause knowledge-dependent work if repair fails until the
user approves a fallback. Never silently bypass the failure with direct reads
or `rg`. Preserve deliberately chosen operation without optional QMD; a broken
configured tool is not evidence that the project made that choice.

## 5. Set up and verify the result

Install td using its [official instructions](https://github.com/marcus/td#installation)
if needed; macOS uses `brew install marcus/tap/td`. Follow the copied
[task workflow](starter/docs/task-tracking.md). Run `td init` in the primary
checkout, verify `td list`, and confirm `.todos/` is ignored. Initialize existing
adopters as well as new projects. Do not commit local databases or exports.
Linked worktrees share the primary checkout's task state; verify this before
using them. Keep td installation and initialization separate from application
startup, CI, and knowledge setup. Record the td version actually checked.

Add the compact new-context command, `td usage --new-session -q`, to the
effective agent instructions with a link to the task workflow. Include the
selective task criteria, task reuse, current handoffs, and reuse of actual
review. Use `td usage` for command guidance and keep detailed examples in the
workflow page. Do not turn small requests into mandatory task lifecycles.

Run the integrated setup, checks, and diagnostics. In an unmodified bundle:

```sh
bin/setup
bin/check --full
bin/doctor
```

Report missing optional QMD or direnv as skipped features. Diagnose an
installed but failing tool. Confirm effective hooks and actual QMD paths;
tracked hook files alone do not prove activation.

The copied tests use disposable repositories and simulated tools. They cover
metadata, indexes, links, existing hooks, missing dependencies, search routing,
concurrency, failures, and worktree isolation. Preserve these checks when
adding application validation.

Test the adopted entry point with simulated application commands that record
invocations: plain `bin/check` and `--documents-only` must call none, `--full`
must run the required application checks, and a failure must stop the command
with a nonzero exit status. Keep this regression in the target project.
Time the routine modes on the actual target and report the measurements.
Aim for well under one second on a small repository; investigate extra work
instead of describing a multi-second command as fast. Use invocation tests,
not a fixed timing threshold, for CI so machine load does not cause failures.

When adapting application discovery, verify that unrelated checkout files are
excluded while errors in intended project files remain detectable. Check both
fresh and warm validation caches after adding or removing a nested checkout.
Verify runtime compatibility checks at the application's command boundary,
including a clear failure before work starts for unsupported versions. Choose
fixtures and commands appropriate to the target stack.

When QMD is available, refresh and verify a distinctive term from a real
project document, a focused read, and collection exclusions. The source
repository's `bin/smoke-qmd --project /absolute/path/to/adopter` snapshots
that adopter's current tracked and unignored files, then exercises its actual
setup, hooks, search, exclusions, diagnostics, and worktree isolation in a
disposable repository. It does not modify the source checkout. Relative links
inside the source are preserved; external symlinks are rejected. Ignored local Git settings
and external hook managers are not copied; verify those in the actual checkout.
Omit `--project` to test the generic bundle. Both modes reuse existing models
at `~/.cache/qmd/models`; first run setup in an adopter to install missing
embedding weights. The smoke test isolates HOME and does not download models. Do not claim real-QMD validation from simulated-tool tests. Record
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
copied foundation tests include `.github/` when present, `LICENSE.project-starter`,
and a project `LICENSE` when present, so workflow and license links work
inside disposable repositories. If adapted docs link to other project files,
include those required files in the test fixtures as well. Run the full
`bin/check --full` after adding the workflow; document-only checks do not exercise
the test fixtures. Use actionlint to validate workflow syntax when available.

After an authorized push, verify the workflow result for the exact pushed
commit. Report a pending, skipped, or failed run explicitly. Passing local
checks does not establish that runner setup or CI passed. The starter's own
CI checks both the base bundle and GitHub integration on macOS and Linux;
QMD is simulated there. Other CI systems should invoke `bin/check --full`.

### New-project remotes

For a new hosted project, complete the [Git remote setup](starter/docs/git-remotes.md).
Keep the primary host, normally GitHub, as `origin` for fetching and pulling.
Create the SourceHut repository as private on its first push, then give
`origin` two push URLs so `git push` updates both hosts. Keep a separate
`sourcehut` remote for verification and targeted retries.

Run this setup explicitly after the initial commit and required checks.
Do not put external repository creation into `bin/setup`, Git hooks,
application startup, or CI. Routine setup after a clone must not create
repositories or publish commits. Preserve existing remotes and custom push
settings; adapt the commands instead of overwriting or duplicating them.

Verify private visibility, the uploaded branch and tag revisions, and both
destinations in a dry-run push. Record the actual URLs in the copied remote
guide. Git does not copy push URLs or additional remotes into fresh clones,
so verify and document how to restore this local configuration.

Deliver a short report of changes, adaptations, checks actually run, and
skipped optional features. Commit or publish according to the user's request
and the target repository's rules.

## 6. Propose improvements to Project Starter

While applying this guide, look for improvements that would help other
projects use the starter. Examples include unclear instructions, missing
integration steps, and failures the starter's checks did not catch. Base
proposals on what you observed. Distinguish a reusable starter improvement
from an application-specific choice, and do not invent suggestions when
the setup reveals none.

Complete the authorized target setup and its checks. Then present any
proposed starter updates to the user who requested the setup. For each
proposal, explain the observed problem, the concrete change, why it belongs
in Project Starter, and how you would verify it. Include enough detail for
the user to review the change before approving it.

Ask whether the user wants you to open a pull request against
[Project Starter](https://github.com/jubishop/project-starter), or apply the
proposed changes to an existing local checkout. If no local checkout is
known, ask whether one exists and request its path as part of that question.
State that this approval is for changing the shared starter, in addition
to the target project's setup.

Wait for the user's approval before changing the starter or opening a PR.
An existing local checkout is not itself permission to edit it. Reuse an
explicit approval already given for the same proposal and delivery route;
do not ask for it again. If the user declines or does not answer, leave the
proposals with the completed setup report.

After approval, read the starter checkout's instructions, inspect its Git
state, and check whether the proposed fix already exists. Preserve unrelated
work. Implement and validate the agreed changes, then deliver the local
update or PR the user requested. Approval for local edits alone does not
authorize publication; approval to open a PR does not authorize merging it.

Keep this feedback step in the guide read on request. Do not add it to the
copied project's automatically loaded instructions or install a background
updater.

## Maintenance

Copied files belong to the project. There is no updater, service, or runtime
dependency on this repository. Compare the recorded starter revision with a
chosen release, merge relevant improvements, update `.project-starter.json`,
and run `bin/check --full`. When adopting the fast default into an existing
project, update its instructions, application wrapper, and CI command together.

For a task-tracking-only update, preserve the original `source_ref` and record
the exact source commit in `task_tracking_source_ref`, plus the verified
`tested_td` version. This records the partial adoption without claiming that
all foundation files were updated.

The guide and starter are [MIT licensed](LICENSE). Retain the included notice;
do not replace the target project's own license.

## Keep the search runtime current

Treat the tested QMD version as a baseline, not a permanent pin. Follow the
[QMD maintenance guide](docs/qmd-maintenance.md) when adopting newer releases.
Merge the command-configuration isolation change into existing helpers before
upgrading older integrations. Preserve explicit subprocess paths in any local
QMD launcher. Validate each adopter with real indexing and search, and use a
central release check for a runtime shared across projects.

## Deployment policy

When the project deploys or publishes releases, adopt the starter's
[deployment policy](starter/docs/development-workflow.md#deployment-decisions).
Allow nonfunctional changes to be committed and pushed without a release.
Preserve required checks and configure the host's supported deployment skip
mechanism when pushes otherwise deploy automatically.

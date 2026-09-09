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
environment configuration, supported toolchains, hooks, and task tracker.
Identify the local validation commands and whether full CI is an enforced
merge or release gate. Determine the effective
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

Keep the copied check modes when integrating application commands:
`bin/check` runs only foundation static checks, `bin/check --documents-only`
checks Markdown, and `bin/check --full` adds foundation behavior tests and
application validation. Do not add application typechecking, lint, tests,
builds, or package-manager startup to either routine mode, even if a command
seems fast in isolation. Run relevant application checks explicitly during
code work. Forward the options through existing wrappers; application commands
must run only when `--full` is present and the foundation checks pass. Update
existing CI commands to use `--full` in the same change.

Include concise file-organization guidance in the target's instructions.
Keep files cohesive and use approximately 1,000 lines as a review threshold
for hand-written source, tests, and styles, not an automatic failure or hard
cap. Preserve readable formatting and meaningful boundaries. Larger files
are acceptable when extraction would reduce clarity. Keep the details in the
[file organization policy](starter/docs/development-workflow.md#file-organization).

Scope application validation inputs and mutable output to the intended
checkout. Review compiler, formatter, build, and test discovery rather than
assuming Git ignore rules exclude nested worktrees and temporary copies.
Include required generated inputs deliberately and preserve safe sharing of
immutable dependencies. Adapt the
[checkout isolation policy](starter/docs/development-workflow.md#validation-checkout-isolation)
to the project's tools.

Declare supported runtime and toolchain versions using the target stack's
existing mechanisms. Keep development, CI, and deployment compatible, and
make application commands reject unsupported versions before work starts.
Prefer maintained releases and coordinate upgrades after compatibility checks.
Apply the [version policy](starter/docs/development-workflow.md#runtime-and-toolchain-versions)
without selecting an application language or stack for the project. Foundation
and document checks must not acquire dependencies on application runtimes they
do not use.

Include the preference for fewer third-party dependencies in the target's
agent instructions. Prefer standard libraries, platform APIs, or a focused
implementation owned by the project when they meet its needs at a reasonable
maintenance cost. A dependency can be justified by concrete benefits; avoiding
initial implementation work alone is not enough. Apply the
[dependency policy](starter/docs/development-workflow.md#third-party-dependencies)
through ordinary technical judgment, without a separate package approval
step. Preserve stronger existing dependency rules and the current application
stack; adopting the foundation does not call for replacing existing packages.

Always state in the target's agent instructions that regression fixes and
functional changes require automated tests for the changed behavior. Use
red-green test-driven development (TDD) whenever practical: write or update
a focused test, confirm it fails for the expected reason before implementation,
then make the change and confirm it passes. If testing first is not practical,
explain why and how the behavior was verified. Preserve stronger existing
testing requirements and adapt the
[testing workflow](starter/docs/development-workflow.md#test-driven-development)
to the project's test commands.

Also state that tests must exercise externally observable behavior: user-visible
outcomes, public interfaces, and interactions with external systems. Put fakes
at those system boundaries so the project's real logic runs. Do not test
private helpers or internal structure, expose private functionality, or add
production APIs only for tests. Internal refactoring that preserves behavior
should not require test changes.

Keep test setup proportional to the behavior under test. Prepare unrelated
prerequisites through isolated fixtures or existing public interfaces, while
retaining dedicated complete journeys. Put repeated rules in less costly
tests when end-to-end execution adds no distinct evidence, and preserve
coverage for every moved case. Measure simpler improvements before deciding
whether parallel execution justifies its isolation work; never hide races
with retries or weaker assertions. Adapt the
[test cost and coverage policy](starter/docs/development-workflow.md#test-cost-and-coverage).

Adapt agent instructions to choose checks by the changed files. Discussion
and read-only work need no checks. Batch Markdown edits before a document
check, and use focused local checks for ordinary code changes. Run the full
suite locally after setup or test/build infrastructure changes, or when
focused checks leave material uncertainty. Require successful full validation
before merge or release. An enforced full CI gate can supply that result for
ordinary changes; without it, require a full local check before delivery.
Preserve stronger project requirements. Reuse a passing result until relevant
inputs change; a conversational handoff alone does not require another run.

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

Keep refresh checks stable across shell commands and Git hooks. QMD
subprocesses must not inherit Git repository selectors. Use the QMD release
version for freshness; its optional Git commit suffix can identify an
unrelated repository. Keep the regression tests for this behavior when
adapting the helpers. See [refresh and recovery](starter/docs/development-workflow.md#refresh-and-recovery).

## 5. Set up and verify the result

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
`bin/check --full` after adding the workflow; document-only checks do not exercise
the test fixtures. Use actionlint to validate workflow syntax when available.

After an authorized push, verify the workflow result for the exact pushed
commit. Report a pending, skipped, or failed run explicitly. Passing local
checks does not establish that runner setup or CI passed. The starter's own
CI checks both the base bundle and GitHub integration on macOS and Linux;
QMD is simulated there. Other CI systems should invoke `bin/check --full`.

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

The guide and starter are [MIT licensed](LICENSE). Retain the included notice;
do not replace the target project's own license.

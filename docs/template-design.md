---
status: current
---

# Template design

## Purpose

Provide a reusable foundation for new repositories: project memory,
documentation, QMD search, Git hooks, and worktree setup. Keep application
stack choices separate from this foundation.

## Accepted decisions

### Delivery format — 2026-09-04

Ship an agent-neutral guide with copyable starter files. The user will point
an agent at the guide when setting up a new repository.

Do not provide a skill wrapper or register the guide for automatic loading.
The user wants to avoid adding persistent agent context.

### Standalone repository — 2026-09-04

Maintain the guide and starter files together in the `project-starter`
repository. It must stand on its own, without references to another project
as its origin or a requirement for using it.

[Fleet-first audience](#fleet-first-audience--2026-10-09) refines this
decision: the starter serves the user's projects and may hold personal
conventions, but not secrets or private data.

### Public distribution — 2026-09-04

Publish the template as a public GitHub repository. Users can point an agent
at its URL without arranging access to a private repository. This choice
applies to the template itself; projects created from it choose their own
visibility.

### Supported platforms — 2026-09-04

Support macOS and Linux. Native Windows support is outside the initial scope.
Use shell scripts and Python helpers that work on both supported platforms.
This keeps the setup small without requiring separate Windows entry points
or file-locking behavior.

### Optional local tools — 2026-09-04

Include QMD and direnv integration in every starter, but do not require these
programs on every machine. Setup can succeed when either is missing and must
clearly report which features were skipped. The Markdown files and Git
workflow remain usable without these tools.

### Minimal agent instructions — 2026-09-04

Include a short `AGENTS.md` in each generated project. It explains where
knowledge belongs, when to search it, and how to run checks. Detailed
policies live in `memory/README.md` and `docs/README.md` and are read when
relevant. This keeps routinely loaded agent context small.

### Tailor instructions to home guidance — 2026-09-28

The starter primarily serves the user's projects, where `~/AGENTS.md` supplies
shared instructions. During adoption, read that file and other applicable
instructions, then remove or shorten redundant rules in the target's
`AGENTS.md`. Compare meaning and scope; home-repository-only rules do not
cover nested projects. Keep project-specific details, stronger requirements,
and intentional exceptions.

This refines the requirements below to include policies in adopted projects:
applicable inherited instructions can supply that coverage. The copied file
is a baseline, not a requirement to repeat every policy locally. The tradeoff
is that a shortened project file can rely on home guidance remaining available.
Keep the adaptation in the setup guide; do not add a recurring cleanup task
to automatically loaded instructions or change the home file during adoption.

From 2.0.0, the [managed AGENTS.md block](#managed-vendoring-and-sync--2026-10-09)
is not pruned against home guidance. This pruning applies only to
project-owned content outside the block.

Keep engineering requirements concise in the guide and agent instructions.
Maintain their details in the [engineering policy](../starter/docs/foundation/engineering-policy.md)
and link to the relevant policy. The user wants to reduce repeated context
and prevent separate copies of the same rule from drifting.

### Optional GitHub integration — 2026-09-04

Generated projects do not have to use GitHub. Every project has local checks
and uses its chosen issue tracker for tasks. Projects hosted on GitHub also
receive a GitHub Actions workflow that runs the same checks. The foundation
must also work with other Git hosts and local repositories.

### Private SourceHut and dual pushes — 2026-09-29

New hosted projects default to a private SourceHut repository in addition
to their primary Git host. Keep primary-host visibility independent. Configure
`origin` with both push URLs so ordinary pushes reach both hosts, while fetches
and pulls keep using the primary host. Keep the named `sourcehut` remote for
verification and retries. Honor explicit hosting choices.

Make this an explicit creation step in the guide. Applying the foundation to
an existing repository does not itself authorize adding a host. Routine local
setup, hooks, and CI must not create repositories or publish commits. Record
the actual URLs in the copied [remote guide](../starter/docs/git-remotes.md)
so fresh clones can restore the local settings. The tradeoffs are separate
push failures and configuration that does not travel with a clone.

### Local task tracking — 2026-09-28

The user selected td for local task progress and handoffs, and requested its
adoption in the starter and existing projects that follow the starter patterns.
Use td alongside the existing shared issue tracker. Shared scope and acceptance
criteria stay in that tracker; local tasks link to relevant issues. Memory and
docs retain durable guidance and decisions rather than temporary progress.

Keep the new-context instruction short and place setup and workflow details in
[the task guide](../starter/docs/foundation/task-tracking.md). Install td explicitly and
initialize each primary checkout. Keep `.todos/` out of Git; linked worktrees
share its state. CI and application startup do not require td. The tradeoff is
that Git pushes do not preserve local task state, so exports or deliberately
configured td sync are needed for transfer to another machine.

### Selective task tracking — 2026-09-30

Keep td available, and require task records for work with multiple stages,
interruptions, blockers, or agent handoffs. Tasks are optional for
straightforward work completed in one session. Read-only questions, small
edits, and filing a single issue need no artificial task lifecycle.

Agents inspect and reuse relevant tasks, record meaningful checkpoints, and
keep the current handoff accurate as work changes. Existing repository checks
and actual review supply completion evidence; moving a task through review and
approval does not add an independent quality gate. Preserve stricter project
review requirements.

The user requested this refinement after an adopter review found useful
recovery and verification handoffs alongside unnecessary small-task records
and handoff summaries that lagged behind their logs. The intended benefit is
less repeated investigation and fewer lost obligations, with less bookkeeping.

### Adaptation to existing files — 2026-09-04

Support new repositories that already contain files, including framework
scaffolding. The guide directs the agent to add missing files, merge setup
instructions, and integrate with existing hooks while preserving their
behavior. Do not provide a separate installer for this adaptation.

[Managed vendoring and sync](#managed-vendoring-and-sync--2026-10-09)
supersedes the no-installer choice. Agents still merge existing instructions,
hooks, and setup commands where judgment is required.

### Enforced documentation checks — 2026-09-04

Require `bin/check` to validate memory metadata, document status fields,
and local Markdown file links. Missing metadata or broken file links fail
local checks and CI. README indexes and PR review records retain their
separate formats.

## Implementation defaults

Use the following defaults to implement the requested foundation:

- Keep durable guidance and non-derivable context in `memory/`, design and
  research in `docs/`, and tracked tasks in the project's issue tracker.
- Index active memory and docs with QMD. Exclude archived memory and PR
  review records. Include home memory only through local opt-in configuration.
- Refresh QMD in the background after checkout, commit, merge, and rewrite.
  Serialize refreshes within each checkout and expose a foreground recovery
  command that reports failures.
- Give each worktree its own search database inside its checkout. Share model
  files across repositories at `~/.cache/qmd/models`; migrate verified local
  duplicates and preserve conflicting files for inspection. Integrate with
  existing environment setup.
- Treat copied starter files as project-owned files that can evolve with the
  project. Keep the guide and bundle usable without an installed skill.
  From 2.0.0, [managed files](#managed-vendoring-and-sync--2026-10-09) are
  synced from releases instead; other copied files remain project-owned.

## Search reliability decision — 2026-09-13

Require current indexed inputs before returning knowledge lookup results.
Automatically refresh stale state with a bounded wait; discard results on
failure or when inputs change during retrieval. Report configured QMD failures
to the user immediately, attempt repair, and pause knowledge-dependent work
after unsuccessful repair until the user approves a fallback.

The user reported that warning-only behavior lets agents silently substitute
direct reads and leave search broken indefinitely. The tradeoff is a freshness
check on each lookup and a possible wait for pending indexing. Keep ordinary
known-file reads and deliberate operation without optional QMD available.
The detailed contract is in the [search failure policy](../starter/docs/foundation/knowledge-search.md#search-failures).

## Improvements accepted — 2026-09-04

All [design principles](design-principles.md) are accepted, including collection
descriptions and starter revision tracking. Documents use `draft`, `current`,
`superseded`, and `archived`; the task tracker owns implementation progress.

## Validation scope — 2026-09-04

The initial delivery required the copied-bundle tests and a real-QMD smoke
test locally on macOS. Linux remained a supported design target, but no
executed Linux test was claimed or required for that delivery.

### GitHub integration follow-up — 2026-09-05

Improve the guide and template's GitHub workflow integration. The user
approved this after adopting the starter exposed missing workflow files in
disposable test copies. Include the optional `.github/` directory in those
copies and test an adopted bundle whose docs link to its workflow.

The starter now uses macOS and Linux CI for the base and GitHub integration
checks. This extends the initial validation scope above. QMD remains simulated
in CI; real-QMD validation is a separate local command. Maintainer checks
require actionlint, while copied projects keep their existing dependencies.

## Adoption feedback — 2026-09-05

Agents applying the guide should propose improvements to Project Starter
when the setup reveals reusable gaps. The user requested this feedback step
so lessons from adoption can improve the guide and template.

Present concrete proposals to the person who requested the setup and ask
for approval to open a PR or update an existing local starter checkout.
Complete the target setup independently. Reuse approval already given for
the same proposal and route. Local edit permission does not imply publishing
permission, and PR permission does not imply merge permission.

Keep the step in the guide read on request. It adds no automatically loaded
instructions or runtime dependency to projects that copy the starter.

## Check frequency and cost — 2026-09-05

The user reported repeated checks during conversation, with one run taking
about 30 seconds. Use a fast default `bin/check` for static validation and
retain `--documents-only` for Markdown edits. Require explicit `--full` for
the disposable-repository behavior tests and all application checks.
Setup and copied CI instructions use `--full`; the maintainer command in
this source repository continues to run the complete suite.

Agent instructions choose validation by changed files and delivery stage.
Discussion and read-only work need no checks. Batch edits and reuse passing
results until relevant inputs change. Follow the current
[validation schedule](../starter/docs/foundation/engineering-policy.md#checks),
which distinguishes focused local checks from the full validation gate.
Existing projects must update their application wrappers and CI commands with
the mode change.

The first correction still allowed application typechecking and lint in the
default path. Those commands and package-manager startup kept a small adopted
project above two seconds. The default now permits foundation static checks
only. Application checks run explicitly for code edits or through `--full`.
Adoption must verify which commands each mode starts and measure routine
latency; use behavioral assertions in CI instead of a timing threshold.

## Tests for behavior changes — 2026-09-06

Every regression fix and functional change requires automated tests for the
changed behavior. Make this explicit in the guide, maintainer instructions,
and copied project instructions. Use red-green test-driven development (TDD)
whenever practical: prove a focused test fails for the expected reason before
implementation, then passes after the change. Refactor with tests passing.

If testing first is not practical, explain why and report the verification
performed and its limits; retain automated coverage for the changed behavior.
Documentation-only changes need the applicable document checks, not new
behavior tests. Focused red and green runs complement the check schedule above.
The user requested this as a basic setup rule so behavior changes have direct
test evidence, beyond running an existing suite.

Tests must exercise externally observable behavior through user-visible
outcomes, public interfaces, and interactions with external systems. Place
fakes at external-system boundaries so the project's real logic runs. Do not
test private helpers or internal structure, expose private functionality, or
add production APIs only for tests. The user requested this boundary so tests
protect actual behavior while allowing internal refactoring.

## Third-party dependencies — 2026-09-06

Make a preference for fewer third-party dependencies part of the guide,
maintainer instructions, and copied project instructions. Prefer standard
libraries, platform APIs, and focused implementations the project can own
when they meet its needs with a reasonable maintenance burden. Dependencies
remain appropriate when their concrete benefits justify their costs.

The user expects increasingly capable coding models to make it more practical
to build and maintain focused implementations. Avoiding initial development
work alone is not enough reason to add a package or framework. Compare the
smallest complete owned implementation with the dependency, including
validation, edge cases, security, maintenance, upgrades, and additional
packages. A library can still reduce the total work or risk.

Use ordinary technical judgment without a separate package approval step.
Preserve existing stack choices during adoption. Keep the detailed
[dependency policy](../starter/docs/foundation/engineering-policy.md#third-party-dependencies)
in the copied workflow so each project can apply it to its own requirements.

## Portable engineering guidance — 2026-09-08

Include concise, stack-neutral guidance for file organization, test cost and
coverage, checkout isolation, runtime compatibility, and local versus CI
validation. Keep the guide, maintainer instructions, and copied project
instructions consistent, with details in the
[copied workflow](../starter/docs/foundation/engineering-policy.md).

Files should have cohesive responsibilities. Approximately 1,000 lines is a
review threshold, not a hard cap. Test optimizations must preserve behavioral
evidence and independence. Project-source discovery and mutable validation
state must respect checkout boundaries. Supported runtime and toolchain
versions must be explicit and compatible across environments; the foundation
does not prescribe an application language, version, or platform.

Use focused local checks for ordinary code changes and require successful full
validation before merge or release. An enforced full CI gate can supply that
result. Without it, require full local validation before delivery. Setup,
test/build infrastructure changes, and material uncertainty still require full
local validation. This refines the earlier requirement to run the full suite
locally before every code PR or release. The source repository's maintainer
command continues to run its complete checks once per completed batch.

The purpose is to reduce unnecessary work while preserving reliable delivery.
The tradeoff is that failures outside focused local coverage may first appear
in CI; the full gate must pass before delivery is complete. Preserve stronger
existing project requirements during adoption. Keep these policies standalone,
without references to another project or assumptions about its stack.

### Nonfunctional delivery — 2026-09-28

Documentation, task tracking, comments, and other nonfunctional changes do not
require deployment or a package release. Keep required checks and assess all
changes since the last successful release. Projects with automatic deployment
must document a supported way to skip it. Follow explicit deployment requests.


## Project Starter 2.0 — 2026-10-09

The user accepted these decisions after a review of the starter and its 21
adopters. They take effect with the 2.0.0 release; td tracks implementation.

### Fleet-first audience — 2026-10-09

Project Starter primarily serves the user's own projects. The repository
stays public and the README states that it is opinionated; it makes no
promise of generic use. Private SourceHut, td, and home-guidance defaults stay
in the core rather than optional extras. Maintainer guidance excludes secrets
and private data instead of all personal conventions.

The user is the only consumer. Staying public avoids Actions minutes that
private macOS runs would consume.

### Managed vendoring and sync — 2026-10-09

Adopters keep vendored copies of managed files: helpers, hooks, `bin/check`,
license notice, and the [managed docs](#managed-docs-and-guide--2026-10-09).
`bin/sync` in this repository copies a tagged release into adopters, creates
new adoptions with `--init`, and reports fleet versions, overrides, and drift
with `--status`. It never commits or pushes. Project-owned pages (README,
development workflow, Git remotes, memory and docs indexes, CI workflow) are
copied only by `--init`. `AGENTS.md` and `.gitignore` carry managed blocks
between markers; content outside the markers belongs to the project.

Clones and CI stay self-contained. The accepted rationale was drift and
manual effort: 17 adopters had byte-identical `_knowledge.py` and 16 had
identical `_checks.py`, while updates were merged by hand across eight source
revisions and ad hoc manifest fields. The tradeoff is that projects no longer
edit managed files freely.

### Extension points — 2026-10-09

`_checks.py` runs a project-owned executable `bin/check-application` under
`--full`, after foundation checks pass. Routine modes never run it. Foundation
behavior tests use bundled fixture documents instead of copying adopter docs.

Every substantive adopter customization was application checks added to
`_checks.py` or a test fixture patched to satisfy that project's links. The
fixture coupling also caused three earlier starter fixes.

### Adopter verification and overrides — 2026-10-09

The foundation behavior suite runs only in starter CI. Every adopter
`bin/check` mode verifies managed files against hashes recorded in
`.project-starter.json`, which records only the version, source, managed
hashes, and overrides. A file that needs local changes is a declared override
with a reason; sync reports it for manual merge. A need becomes an extension
point when a second repository has it.

Rerunning identical code in each adopter added no evidence once managed files
are verified. The tradeoff is that adopters no longer exercise the suite on
their own runners.

### Managed docs and guide — 2026-10-09

Shared policy moves to managed `docs/foundation/` pages for engineering
policy, knowledge search operations, and task tracking, in a separate QMD
collection. Each rule has one authoritative page; project pages link to it and
add only stronger or project-specific rules. The managed `AGENTS.md` block
stays near 20 lines. `GUIDE.md` becomes a checklist of judgment steps around
`bin/sync --init`; maintenance, runtime, and deployment sections move to docs.
Foundation docs receive a concision pass, with rationale kept in this document.

Rules were repeated in up to six files, and most starter commits were policy
changes merged into adopters by hand.

### Releases and migration — 2026-10-09

Cut semver tags after CI passes on `main`; sync targets the latest tag.
`CHANGELOG.md` separates synced changes from manual follow-up. Major versions
change extension points or required actions. 2.0.0 may span several pull
requests but ships as one tag, so adopters migrate once.

Pilot the migration in health, screenr, and podhaven, then migrate the other
adopters. Every adopter uses the same managed set; printing adopts the full
set rather than a knowledge-only subset.

### Tool versions — 2026-10-09

Use upstream td from its Homebrew tap; 0.66.0 was installed on 2026-10-09
(PDT). Record verified td and QMD versions once per starter release, not
in each adopter. The QMD constant in `_knowledge.py` is the runtime source;
maintainer checks assert that it matches `tools/qmd/package.json`, and
`bin/doctor` compares parsed versions exactly.

[Latest stable toolchains](#latest-stable-toolchains--2026-10-09) supersedes the
tested-version constant and its checks.

### Latest stable toolchains — 2026-10-09

Use the latest stable release of runtimes and tools instead of pinning
versions that someone must remember to bump; for Node, the latest LTS line.
Projects declare minimum versions, CI installs the latest stable release on
every run, and developer machines and servers update weekly with
verification and rollback. QMD and its backend follow the latest releases;
the tested-version constant, its `bin/doctor` notice, the validation
lockfile, and Dependabot updates are removed. A pin is allowed only for a
known incompatibility, with its removal condition recorded beside it.

The user asked for this so versions do not go stale when nobody is watching.
The tradeoff is that a breaking release can reach a machine or server before
anyone reviews it; scheduled CI, the strict QMD smoke check, health checks,
and automatic rollback limit that risk. This supersedes the 2026-09-08 rule
against unbounded version selectors and the per-release tested versions above.

### Setup extension point — 2026-10-09

`bin/setup` runs an executable, project-owned `bin/setup-application` after
the foundation setup succeeds, so application dependencies install with the
same single command. The user noted that a project needing a dependency
install is not special; several Node adopters need one.

### Unchanged choices — 2026-10-09

Keep the [search reliability decision](#search-reliability-decision--2026-09-13)
and state it once in the managed docs; no adopter had a failed refresh state
on 2026-10-09. Keep this repository's maintainer `bin/check` rather than
adopting the managed set, because a broken managed file would also break the
tools needed to repair it. Sync receives its own fixture tests.

## License — 2026-09-04

Use the MIT license for the guide and starter files. Preserve its notice in
copied material without imposing a license on the rest of a new project.

Record accepted decisions in this document. Recommendations and unanswered
questions do not constitute accepted decisions.

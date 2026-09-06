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

### Optional GitHub integration — 2026-09-04

Generated projects do not have to use GitHub. Every project has local checks
and uses its chosen issue tracker for tasks. Projects hosted on GitHub also
receive a GitHub Actions workflow that runs the same checks. The foundation
must also work with other Git hosts and local repositories.

### Adaptation to existing files — 2026-09-04

Support new repositories that already contain files, including framework
scaffolding. The guide directs the agent to add missing files, merge setup
instructions, and integrate with existing hooks while preserving their
behavior. Do not provide a separate installer for this adaptation.

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
- Give each worktree its own search database and share model files. Preserve
  existing local caches and integrate with existing environment setup.
- Treat copied starter files as project-owned files that can evolve with the
  project. Keep the guide and bundle usable without an installed skill.

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

## License — 2026-09-04

Use the MIT license for the guide and starter files. Preserve its notice in
copied material without imposing a license on the rest of a new project.

Record accepted decisions in this document. Recommendations and unanswered
questions do not constitute accepted decisions.

---
status: planning
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

## Design questions

Resolve supported environments, required and optional tooling, knowledge
conventions, setup behavior, and validation before completing the starter
bundle.

Record accepted decisions in this document. Recommendations and unanswered
questions do not constitute accepted decisions.

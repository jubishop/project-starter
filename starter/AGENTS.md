# Project instructions

Keep durable guidance and non-derivable context in [memory](memory/README.md).
Keep designs, decisions, and research in [docs](docs/README.md). Use the
project's chosen task tracker for work items and implementation progress.

Before non-trivial work or writing memory, search the relevant knowledge.
Use `bin/knowledge search "term"` for known terms and
`bin/knowledge query "question" --no-rerank` for broader questions.
Read focused results with `bin/knowledge get <path> -l 80`.
Use direct reads for known files or when search is unavailable or stale.
Markdown source files are authoritative. Update existing pages when possible.

Regression fixes and functional changes require automated tests for the
changed behavior. Use red-green test-driven development (TDD) whenever
practical: prove a focused test fails before implementation and passes after.
If testing first is not practical, explain why and how the behavior was
verified. Follow the [testing workflow](docs/development-workflow.md#test-driven-development).

Test user-visible outcomes, public interfaces, and interactions with external
systems. Put fakes at external-system boundaries so real project logic runs.
Do not test private helpers or internal structure, expose private functionality,
or add production APIs only for tests. Tests should allow internal refactoring
that preserves behavior.

Run `bin/setup` after cloning. Choose checks for the changed files: use
`bin/check --documents-only` for Markdown edits and `bin/check` for foundation
checks only. Keep application tools out of both modes; run relevant application
checks explicitly for code edits.
Run `bin/check --full` after setup or foundation changes, and before a code PR
or release. Do not run checks for discussion or read-only work. Batch edits
before checking; reuse passing results while relevant inputs are unchanged.
See [the workflow](docs/development-workflow.md#checks-and-project-extensions).
Use `bin/doctor` to inspect local setup and `bin/qmd-index` to refresh search
after uncommitted knowledge edits when current search results are needed.
Hooks refresh search after Git events.

Read the relevant memory or docs index for its format and maintenance rules.
Keep accepted decisions separate from proposals. Preserve existing project
instructions, setup commands, hooks, and unrelated changes when adapting this
foundation. Keep secrets and generated caches out of Git.

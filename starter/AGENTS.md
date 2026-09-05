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

Run `bin/setup` after cloning and `bin/check` before delivering changes.
Use `bin/doctor` to inspect local setup and `bin/qmd-index` to refresh search
after uncommitted knowledge edits. Hooks refresh search after Git events.

Read the relevant memory or docs index for its format and maintenance rules.
Keep accepted decisions separate from proposals. Preserve existing project
instructions, setup commands, hooks, and unrelated changes when adapting this
foundation. Keep secrets and generated caches out of Git.

---
status: current
---

# Design principles

These accepted principles define the foundation described in the
[template design](template-design.md). Keep the guide and starter files
small enough for an agent to understand and adapt without a separate framework.

## Scope search settings to the search process

Provide one repository-local command for QMD that works from the checkout
and its subdirectories without personal shell wrappers or direnv. Resolve
the configuration and database paths from the checkout itself.

Set cache environment variables only for the QMD process. In particular,
`XDG_CACHE_HOME` controls the cache location for applications generally;
exporting it through `.envrc` also changes unrelated tools. Keep direnv
available for project environment setup without making it necessary for
correct search routing.

Reference: [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir/latest/).

## Make setup repeatable and preserve existing integrations

Inspect existing setup commands, active Git hooks, and environment files
before integrating the bundle. Repeated setup should preserve local choices
and existing behavior. When a hook manager is present, integrate with it
instead of taking ownership of its configuration.

Resolve worktree locations through Git's reported worktree information,
without assuming that the parent of the common Git directory is the primary
checkout. Test paths with spaces and repositories with separate Git metadata.

Reference: [Git worktree documentation](https://git-scm.com/docs/git-worktree).

## Avoid unnecessary refresh work

Combine bursts of hook requests into the minimum refreshes needed to index
the final state. Preserve a pending refresh when indexed files change during
an active run. Skip work only when the indexed inputs and configuration are
known to be unchanged, accounting for deletions and optional home memory.

Keep a foreground refresh command for uncommitted edits and recovery.
Search documentation must explain that Git hooks do not observe each file
save. Use QMD's incremental indexing rather than implementing a second indexer.

## Add a read-only diagnostic command

A command such as `bin/doctor` should report the active hook integration,
available tools and supported versions, selected collections, current
checkout's database, shared model path, and the last refresh outcome.

Distinguish an optional tool that is absent from a tool that is installed
but failing. Report whether index freshness is known, stale, or unknown.
Give a specific recovery command when a check finds a problem. Diagnostic
inspection should not approve environment files, download models, or rebuild
the index as a side effect.

## Separate document lifecycle from implementation progress

Use `draft`, `current`, `superseded`, and `archived` for document status.
These apply to reference guides, research, and designs as well as product
documents. Track planned, ongoing, and completed implementation in the
project's task system. A current design describes the current plan; it does
not establish that the plan has been implemented or explicitly approved.

Keep accepted decisions, their reasons, and open questions distinct inside
documents. For external facts that can change, include a source and a
verification date when useful. Use related work as the occasion to review
such facts rather than imposing recurring bookkeeping on every page.

## Make checks enforce the documented rules

Validate the stated frontmatter schema, including filename/name agreement
and project-memory lifecycle rules. Verify that active pages appear in their
index and that archived pages are removed from active indexes. Check local
file links and ordinary heading anchors where their syntax is supported.

Provide clear diagnostics for unsupported markup. Preserve separate handling
for PR review records, generated documentation, and deliberately excluded
content. Do not infer document correctness or user approval from metadata.

## Improve retrieval without adding loaded instructions

Give QMD collections short descriptions of their purpose, using its context
metadata. Give documents clear titles and opening summaries. These help an
agent assess a search result without requiring the whole knowledge base in
its initial context. They do not replace reading the authoritative document.

Reference: [QMD context documentation](https://github.com/tobi/qmd#context-management).

## Validate the copied result and record its version

Test the starter as copied into disposable repositories. Run the base bundle
and the optional GitHub integration on macOS and Linux in CI. Include existing
hooks, missing optional tools, subdirectory searches,
repeated setup, concurrent refresh requests, and worktree isolation.

Keep routine tests independent of model downloads. Add an explicit smoke
check with a supported real QMD version to verify actual configuration,
collection exclusions, and retrieval. Record tested versions and a starter
revision so maintainers can compare later changes manually. Copied projects
remain independent, without an automatic update service.

---
status: current
---

# Keep QMD current

Always run the latest QMD release and the latest node-llama-cpp backend.
Nothing pins a version: the owner's Mac tests the newest releases every week
and installs them only after the strict smoke check passes.

## Compatibility boundary

The foundation owns collection definitions and the canonical generated JSON
configuration. Each indexing or lookup process receives its own temporary
configuration copy through `QMD_CONFIG_DIR`. QMD may serialize that copy as
YAML or add model defaults. Its changes are discarded when the command ends.
The SQLite index remains checkout-local and models remain shared.

This avoids depending on QMD's serialization format or reproducing its model
defaults in every project. Configuration changes, failed commands, source
changes during retrieval, and stale indexes still prevent unverified results.
Custom launchers must preserve an explicit `QMD_CONFIG_DIR`, `INDEX_PATH`, and
`XDG_CACHE_HOME` supplied by the caller.

## Latest runtime

The Mac's updater installs the latest release of both packages, with an
override that makes QMD use the newest backend rather than the older one it
depends on. QMD 2.8.3 depends on backend 3.20.0, whose llama.cpp build cannot
compile the Metal 4 tensor-API probe on M5 Macs: it logs
`ggml_metal_library_init_from_source: error compiling source`, disables M5
tensor acceleration, and embeds about 30 percent slower while still using the
GPU. Backend 3.21.0 and later fix the probe, as its
[release notes](https://github.com/withcatai/node-llama-cpp/releases/tag/v3.21.0)
state.

## Changes to the knowledge tools

Real QMD runs only on the owner's Mac, the one machine that runs the knowledge
tools; GitHub Actions runs only the tests with fake QMD processes. When
[`bin/check`](../bin/check) runs outside GitHub Actions and this checkout's
changes, committed or not, touch the knowledge tools, it also runs
`bin/smoke-qmd --strict-diagnostics` against the Mac's QMD. The knowledge
tools are `_knowledge.py`, the commands and hooks that load it,
`.config/knowledge.json`, and `bin/smoke-qmd` itself. A hosted workflow that
ran the smoke check on a Linux CPU runner was retired; see
[template design](template-design.md#adopters-on-one-mac--2026-11-15).

## Automatic updates on the Mac

The home repository's `~/bin/auto-update` runs weekly from a
LaunchAgent. For QMD it installs the latest QMD and backend into a fresh
package root, runs `bin/smoke-qmd --qmd <candidate> --strict-diagnostics`
from this repository, and replaces the shared runtime only when that passes.
The previous runtime is kept for rollback, and failures send a notification.
Indexes refresh on their next lookup, because index freshness includes the
QMD release version.

## Verify a runtime by hand

1. Install the candidate into a separate package root.
2. Run `bin/smoke-qmd --qmd /candidate/node_modules/.bin/qmd
   --download-models --strict-diagnostics`. Run it again with
   `--project /path/to/adopter` for affected integrations.
3. The smoke check covers fresh indexes, exclusions, keyword and vector
   retrieval, query expansion, reranking, repeat setup, linked worktrees, and
   orphaned-vector cleanup after an edit.
   It records diagnostics and rejects warnings in strict mode, including
   warnings in indexing logs after a successful command.
   On Apple M5 Macs, `ggml_metal_library_init_from_source: error compiling
   source` means the backend disabled Metal tensor acceleration. Treat it as a
   failed candidate rather than noise. Failure reports retain worker logs,
   including setup timeouts. Run it with `CI` unset, since QMD disables
   inference whenever that variable is nonempty.
4. Do not use direct `qmd update` against managed indexes or share databases
   between worktrees. Index logs keep entries from replaced runtimes until
   they rotate at about 1 MB; each refresh section starts with a timestamp and
   QMD version, so judge a runtime only by sections written after its first
   refresh.
5. If a release breaks compatibility, fix the integration and add a
   regression test. If it cannot be fixed yet, pin the last working release in
   the Mac updater, and record the issue and the condition for removing the
   pin beside it.

Model downloads are opt-in for smoke tests, which otherwise reuse the models
in `~/.cache/qmd/models`. The normal foundation suite uses fake QMD processes
and stays offline.

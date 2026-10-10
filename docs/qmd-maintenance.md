---
status: current
---

# Keep QMD current

Always run the latest QMD release and the latest node-llama-cpp backend.
Nothing pins a version: CI tests the newest releases every week, and the
owner's Mac installs them automatically after the same strict check passes.

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

[The validation manifest](../tools/qmd/package.json) asks for `latest` of
both packages and has no lockfile. Its override makes QMD use the newest
backend rather than the older one it depends on. QMD 2.8.3 depends on backend
3.20.0, whose llama.cpp build cannot compile the Metal 4 tensor-API probe on
M5 Macs: it logs `ggml_metal_library_init_from_source: error compiling
source`, disables M5 tensor acceleration, and embeds about 30 percent slower
while still using the GPU. Backend 3.21.0 and later fix the probe, as its
[release notes](https://github.com/withcatai/node-llama-cpp/releases/tag/v3.21.0)
state. Remove the override once QMD's own backend dependency is at least
3.21.0.

The [compatibility workflow](../.github/workflows/qmd-compatibility.yml)
installs the latest releases on the latest Node LTS and runs the strict
smoke check with real models on a Linux CPU runner. It runs on relevant
changes and every Monday, so a breaking release appears as a failed Actions
run. Hosted runners cannot exercise Metal, which is why the Mac verifies
each update itself.

## Automatic updates on the Mac

The home repository's `~/bin/toolchain-update` runs weekly from a
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
   retrieval, query expansion, reranking, repeat setup, and linked worktrees.
   It records diagnostics and rejects warnings in strict mode, including
   warnings in indexing logs after a successful command. `--cpu-only` forces
   CPU operation for hosted runners and allows only QMD's exact no-GPU notice;
   all other warning and error diagnostics still fail strict validation.
   On Apple M5 Macs, `ggml_metal_library_init_from_source: error compiling
   source` means the backend disabled Metal tensor acceleration. Treat it as a
   failed candidate rather than noise. Failure reports retain worker logs,
   including setup timeouts. CI downloads models in a separate bounded step
   and allows 600 seconds per smoke command. The real-model step unsets `CI`
   because QMD disables inference whenever that variable is nonempty.
4. Do not use direct `qmd update` against managed indexes or share databases
   between worktrees. Index logs keep entries from replaced runtimes until
   they rotate at about 1 MB; each refresh section starts with a timestamp and
   QMD version, so judge a runtime only by sections written after its first
   refresh.
5. If a release breaks compatibility, fix the integration and add a
   regression test. If it cannot be fixed yet, pin the last working release in
   the validation manifest and the Mac updater, and record the issue and the
   condition for removing the pin beside it.

Model downloads are opt-in for local smoke tests. CI enables them explicitly.
The normal foundation suite uses fake QMD processes and stays offline.

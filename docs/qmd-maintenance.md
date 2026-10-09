---
status: current
---

# Keep QMD current

Prefer current stable QMD and backend releases. Test a candidate before
replacing a shared installation. A tested version records evidence; it is
not an indefinite version ceiling.

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

## Tested runtime and release detection

[The validation manifest](../tools/qmd/package.json) and its lockfile select
QMD 2.8.3 and node-llama-cpp 3.22.1. QMD 2.8.3 otherwise selects backend
3.20.0, whose llama.cpp build cannot compile the Metal 4 tensor-API probe on
M5 Macs. That backend logs `ggml_metal_library_init_from_source: error
compiling source`, disables M5 tensor acceleration, and embeds about 30
percent slower while still using the GPU. Backend 3.21.0 and later fix the
probe, as its [release notes](https://github.com/withcatai/node-llama-cpp/releases/tag/v3.21.0)
state. Remove the override once QMD's own backend dependency is at least
3.21.0. This pairing passed strict smoke validation on an Apple M5 Pro with
macOS 27.0.1 on October 9, 2026 (PDT).

Dependabot checks both direct dependencies weekly and groups their updates.
The [compatibility workflow](../.github/workflows/qmd-compatibility.yml) runs
on relevant changes and every Monday. It tests the selected runtime and the
latest published versions with actual models on Linux CPU runners. This checks
CLI, configuration, database, and model compatibility. Run the same smoke check
on the developer Mac before upgrading to verify its Metal backend. Failures remain visible
as failed Actions runs; dependency updates require passing validation.
No workflow automatically changes a developer's global installation.

For a Bun or npm installation, run:

```sh
bin/qmd-updates --installation /path/to/package-manager/root
```

The root must contain `node_modules`. The command checks the installed QMD
and its resolved backend, including a nested backend. It queries the npm
registry with timeouts, writes a dated JSON report, and exits 0 when current,
2 when a newer release exists, or 1 when the check fails. `--state-file`
selects the report path. `--notify` sends a macOS notification once for each
new release set or changed failure. A login scheduler can run this weekly.
It checks releases without installing them or accessing knowledge content.

## Upgrade and verify

1. Install the candidate into a separate package-manager root. Keep its
   package manifest and lockfile so the tested dependency graph is reproducible.
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
   failed candidate rather than noise; hosted CPU runners cannot detect it.
   Failure reports retain worker logs, including setup timeouts. CI downloads
   models in a separate bounded step and allows 600 seconds per smoke command.
   The real-model step unsets `CI` because QMD disables inference whenever that
   variable is nonempty. Ordinary foundation tests retain the CI environment.
4. Back up the current runtime, update affected helpers, then replace the
   shared runtime. Run each integration's coordinated refresh and real lookup.
   Keep the old runtime until these checks pass. Do not use direct `qmd update`
   against managed indexes or share databases between worktrees. Index logs
   keep entries from replaced runtimes until they rotate at about 1 MB. Since
   2.0.0, each refresh section starts with a timestamp and QMD version; judge
   a runtime only by sections written after its first refresh.
5. Update the tested version and evidence. If compatibility breaks, fix the
   integration and add a regression test. Keep any temporary pin visible in
   the update checks and state the condition for removing it.

Model downloads are opt-in for local smoke tests. CI enables them explicitly.
The normal foundation suite uses fake QMD processes and stays offline.

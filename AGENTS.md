# Maintaining Project Starter

Read [the guide](GUIDE.md) and the relevant [design documents](docs/README.md).
`starter/` holds the bundle that `bin/sync` installs, and `extras/` holds
files it copies on adoption. Keep secrets and private data out of this public
repository. Do not install or register a skill.

Follow the [task workflow](starter/docs/foundation/task-tracking.md) for td
and the [engineering policy](starter/docs/foundation/engineering-policy.md)
for dependencies, red-green tests through public interfaces, test cost, file
and page organization, checkout isolation, and toolchain versions.

Run `bin/check` once for a completed batch of changes; it tests copies of the
bundle. Reuse a passing result while relevant inputs are unchanged.
Discussion and read-only work need no checks. Use `bin/smoke-qmd` for
explicit real-QMD validation. Cut releases and sync adopters as described in
[releases](docs/releases.md), and record manual follow-up in the
[changelog](CHANGELOG.md). Keep the guide, bundle, and changelog consistent.

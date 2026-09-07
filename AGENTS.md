# Maintaining Project Starter

Read [the guide](GUIDE.md) and the relevant [design documents](docs/README.md).
The copyable foundation lives in `starter/`; optional host integration lives
in `extras/`. Keep the guide standalone and free of personal paths or origin
project references. Do not install or register a skill.

Prefer fewer third-party dependencies. Use standard libraries, platform APIs,
or a focused implementation owned by the project when they meet its needs at
a reasonable maintenance cost. Add a dependency when its concrete benefits
justify it; initial implementation convenience alone is not enough. Apply
the [dependency policy](starter/docs/development-workflow.md#third-party-dependencies)
through ordinary technical judgment, without a separate approval step.

Regression fixes and functional changes require automated tests for the
changed behavior. Use red-green test-driven development (TDD) whenever
practical: prove a focused test fails before implementation and passes after.
If testing first is not practical, explain why and how the behavior was
verified. Follow the [testing workflow](starter/docs/development-workflow.md#test-driven-development).

Test user-visible outcomes, public interfaces, and interactions with external
systems. Put fakes at external-system boundaries so real project logic runs.
Do not test private helpers or internal structure, expose private functionality,
or add production APIs only for tests. Tests should allow internal refactoring
that preserves behavior.

Run `bin/check` once for a completed batch of changes. Its tests exercise
copies of the bundle. Reuse a passing result while relevant inputs are
unchanged; discussion and read-only work do not require checks.
Use `bin/smoke-qmd --models /absolute/path/to/existing/models` for explicit
real-QMD validation. Keep copied project behavior and the guide consistent.

# Maintaining Project Starter

Read [the guide](GUIDE.md) and the relevant [design documents](docs/README.md).
The copyable foundation lives in `starter/`; optional host integration lives
in `extras/`. Keep the guide standalone and free of personal paths or origin
project references. Do not install or register a skill.

Follow the local [task workflow](starter/docs/task-tracking.md) for td setup and commands.

Follow the engineering policies linked below:

- Prefer fewer dependencies; justify additions by their concrete benefits
  under the [dependency policy](starter/docs/development-workflow.md#third-party-dependencies).
- Cover regression fixes and functional changes with automated tests. Use
  [red-green TDD](starter/docs/development-workflow.md#test-driven-development)
  when practical; explain exceptions. Test observable behavior through public
  interfaces, with fakes at external-system boundaries.
- Keep [test cost proportional](starter/docs/development-workflow.md#test-cost-and-coverage)
  while preserving coverage, independence, and useful complete journeys.
- Keep [files cohesive](starter/docs/development-workflow.md#file-organization);
  approximately 1,000 lines is a review threshold for source, tests, and styles.
- Keep [Markdown pages focused](starter/docs/development-workflow.md#markdown-pages)
  on one topic or reader task, without numeric size limits.
- Isolate [validation inputs and output](starter/docs/development-workflow.md#validation-checkout-isolation)
  to the intended checkout.
- Keep supported [runtime and toolchain versions](starter/docs/development-workflow.md#runtime-and-toolchain-versions)
  compatible across environments without imposing an application stack.

Run `bin/check` once for a completed batch of changes. Its tests exercise
copies of the bundle. Reuse a passing result while relevant inputs are
unchanged; discussion and read-only work do not require checks.
Use `bin/smoke-qmd` for explicit real-QMD validation. Keep copied project
behavior and the guide consistent.

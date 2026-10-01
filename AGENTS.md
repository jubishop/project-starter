# Maintaining Project Starter

Read [the guide](GUIDE.md) and the relevant [design documents](docs/README.md).
The copyable foundation lives in `starter/`; optional host integration lives
in `extras/`. Keep the guide standalone and free of personal paths or origin
project references. Do not install or register a skill.

Use `td` for work with multiple stages, interruptions, blockers, or agent
handoffs. Tasks are optional for straightforward work completed in one session;
read-only questions and small edits need no artificial task records. In each
new agent context, run `td usage --new-session -q` once. Before substantive
work, inspect and reuse relevant tasks. Record meaningful checkpoints and keep
the current handoff accurate. Reuse required checks and actual review; task
statuses do not add a separate review gate. Follow the
[task workflow](starter/docs/task-tracking.md) for setup and commands. Keep
GitHub Issues for shared scope and acceptance criteria; link related issues
from td.

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

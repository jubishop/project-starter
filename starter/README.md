# Project

Replace this introduction with the project's purpose and main entry points.

## Development

Run `bin/setup` after cloning. It requires Git and Python 3.9 or later.
QMD and direnv are optional; setup reports skipped features.

Use `bin/check --documents-only` for Markdown edits and `bin/check` for
foundation checks only. Use focused local checks for ordinary code changes.
Run `bin/check --full` locally after setup, test/build infrastructure changes,
or when focused checks leave material uncertainty. Require successful full
validation before merge or release; an enforced full CI gate can provide it
for ordinary changes. Without that gate, run the full check locally before
delivery. See the [validation policy](docs/development-workflow.md#checks-and-project-extensions).
The fast and full checks require ShellCheck.
Use `bin/doctor` for diagnostics. See the
[development workflow](docs/development-workflow.md) for search, worktrees,
hook integration, and recovery.

## Knowledge

- [Memory](memory/README.md): durable guidance and non-code context.
- [Docs](docs/README.md): designs, decisions, research, and reference guides.

Choose a task tracker and add its entry point here. Add application setup as
the project develops. Integrate application validation only with `--full`,
and document explicit application checks for code edits.

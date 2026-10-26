# Project

Replace this introduction with the project's purpose and main entry points.
Until the project has an application, say so instead of listing entry points.

## Development

Run `bin/setup` after cloning; it needs Git and Python 3.9 or later. QMD and
direnv are optional, and setup reports skipped features. See the
[development workflow](docs/development-workflow.md) for this project's
commands and the [check schedule](docs/foundation/engineering-policy.md#checks)
for when to run `bin/check --documents-only`, `bin/check`, and
`bin/check --full`. The checks need ShellCheck; `bin/doctor` diagnoses setup.

Hosted projects record their primary remote in
[Git remotes](docs/git-remotes.md); `bin/setup` never publishes repositories.

## Knowledge

- [Memory](memory/README.md): durable guidance and non-derivable context.
- [Docs](docs/README.md): designs, decisions, research, and reference guides.

Track work in the project's issue tracker. This project uses [Project Starter](https://github.com/jubishop/project-starter);
`.project-starter.json` records its release.

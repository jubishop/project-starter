# Project Starter

A standalone guide and starter-file bundle for repository memory, docs,
QMD search, Git hooks, and worktrees. Point a coding agent at
[GUIDE.md](GUIDE.md) when setting up a new repository.

> Read https://github.com/jubishop/project-starter/blob/main/GUIDE.md and apply
> its starter bundle to my project. Inspect existing files and hooks first,
> preserve their behavior, and verify the resulting setup.

No skill installation or automatic context loading is required. Copied files
belong to the new project and can evolve independently.

- [Guide](GUIDE.md): how to apply and verify the foundation.
- [Starter files](starter/): the copyable bundle, including its own checks.
- [Optional GitHub workflow](extras/github/.github/workflows/check.yml): run
  the same checks in GitHub Actions.
- [Design and validation](docs/README.md): decisions, guarantees, and evidence.

The scripts target macOS and Linux. Validation for this release runs locally
on macOS; Linux execution is not claimed. Git and Python 3.9+ are required.
ShellCheck is required for checks. QMD and direnv are optional.

Maintainers run `bin/check`. For a real-QMD smoke test using existing local
models, run `bin/smoke-qmd --models /absolute/path/to/models`.

Released under the [MIT license](LICENSE). Keep `LICENSE.project-starter`
with copied material; choose the new project's own license independently.

# Project Starter

A standalone guide and starter-file bundle for repository memory, docs,
QMD search, Git hooks, and worktrees. Point a coding agent at
[GUIDE.md](GUIDE.md) when setting up a new repository.

> Read https://github.com/jubishop/project-starter/blob/main/GUIDE.md and apply
> its starter bundle to my project. Inspect existing files and hooks first,
> preserve their behavior, and verify the resulting setup.

No skill installation or automatic context loading is required. Copied files
belong to the new project and can evolve independently.
Agents applying the guide [propose reusable improvements](GUIDE.md#6-propose-improvements-to-project-starter)
and ask the user before updating the starter or opening a pull request.

- [Guide](GUIDE.md): how to apply and verify the foundation.
- [Starter files](starter/): the copyable bundle, including its own checks.
- [Optional GitHub workflow](extras/github/.github/workflows/check.yml): run
  the full checks in GitHub Actions.
- [Design and validation](docs/README.md): decisions, guarantees, and evidence.

The scripts target macOS and Linux. The
[starter CI](.github/workflows/check.yml) runs checks on both platforms,
including an adopted copy with the optional GitHub workflow. See
[validation](docs/validation.md) for executed results. Git and Python 3.9+ are required.
ShellCheck is required for checks. QMD and direnv are optional.

Copied projects use `bin/check` for fast checks, `--documents-only` for
Markdown edits, and `--full` for foundation tests and CI. Discussion needs
no checks. Batch edits and reuse passing results until relevant inputs change.

In this source repository, maintainers run `bin/check`, which always runs
the full suite and also requires
[actionlint](https://github.com/rhysd/actionlint/blob/main/docs/install.md) to
check the maintained and copyable workflows. This extra dependency is only
for maintaining the starter. For a real-QMD smoke test using existing local
models, run `bin/smoke-qmd --models /absolute/path/to/models`.

Released under the [MIT license](LICENSE). Keep `LICENSE.project-starter`
with copied material; choose the new project's own license independently.

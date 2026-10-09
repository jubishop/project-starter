# Project Starter

An opinionated foundation for one owner's repositories: Markdown memory and
docs with QMD search, Git hooks, worktree support, td task tracking, shared
engineering policy, and private SourceHut mirroring. The repository is public,
but it is not a general-purpose template; its defaults reflect those projects.

- [Guide](GUIDE.md): adopt or update a repository.
- [Starter bundle](starter/): the files `bin/sync` installs.
- [Changelog](CHANGELOG.md): releases and their manual follow-up.
- [Design and validation](docs/README.md): decisions, releases, and evidence.

## Use

```sh
bin/sync --init /path/to/project   # adopt the latest release
bin/sync /path/to/project          # update an adopter
bin/sync --status                  # versions, drift, and overrides under ~/projects
```

Sync copies managed files, records their hashes in `.project-starter.json`,
and never commits. An adopter's `bin/check` verifies those hashes, and
`bin/check --full` adds the project's `bin/check-application`.

The scripts target macOS and Linux and need Git and Python 3.9 or later;
checks need ShellCheck. QMD, direnv, and td are optional at runtime.

## Maintain

`bin/check` runs the maintainer suite: document checks, ShellCheck,
[actionlint](https://github.com/rhysd/actionlint/blob/main/docs/install.md),
and behavior tests against copies of the bundle.
[CI](.github/workflows/check.yml) runs it on Ubuntu and macOS. `bin/smoke-qmd`
runs a real-QMD smoke test locally. See [releases](docs/releases.md) for
cutting a version and syncing adopters.

Released under the [MIT license](LICENSE).

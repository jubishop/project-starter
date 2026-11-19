# Project Starter

An opinionated foundation for one owner's repositories: Markdown memory and
docs with QMD search, Git hooks, worktree support, and shared
engineering policy. The repository is public, but it is not a general-purpose
template; its defaults reflect those projects.

- [Guide](GUIDE.md): adopt or update a repository.
- [Starter bundle](starter/): the files `bin/sync` installs.
- [Changelog](CHANGELOG.md): releases and their manual follow-up.
- [Design and validation](docs/README.md): decisions, releases, and evidence.

## Use

```sh
bin/sync --init /path/to/project   # adopt the latest release
bin/sync /path/to/project          # update an adopter
bin/sync --status                  # versions, drift, overrides, managed imports, and script tests under ~/projects
```

Sync copies managed files, records their hashes in `.project-starter.json`,
and never commits. An adopter's `bin/check` verifies those hashes, and
`bin/check --full` adds the project's `bin/check-application`.

The scripts target macOS, where every adopter lives; only `bin/check` and
what it imports also support Linux, for adopters' CI. They need Git and
Python 3, and checks need ShellCheck. On the Mac, the knowledge tools also
require QMD, and direnv in a checkout with an `.envrc`; the home repository's
setup installs them all.

## Maintain

`bin/check` runs the maintainer suite: document checks, ShellCheck,
[actionlint](https://github.com/rhysd/actionlint/blob/main/docs/install.md),
and behavior tests against copies of the bundle.
[CI](.github/workflows/check.yml) runs it on Ubuntu and macOS. Outside CI,
it also runs `bin/smoke-qmd`, a smoke test with the Mac's real QMD, when a
change touches the knowledge tools. See [releases](docs/releases.md) for
cutting a version and syncing adopters.

Released under the [MIT license](LICENSE).

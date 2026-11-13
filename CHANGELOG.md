# Changelog

Each release lists what `bin/sync` changes in adopters and the manual
follow-up it cannot apply. See [releases](docs/releases.md).

## 3.12.0 — 2026-11-13

### Synced

- The `memory-audit` feature reads its Anthropic API key as
  `ANTHROPIC_MEMORY_AUDIT_API_KEY`, from the checkout's `.env` and, without a
  line there, from `~/.env`, where one key serves every project's audit on
  the Mac. The checkout's line wins even when empty, which keeps that project
  on the subscription. The old name, `MEMORY_AUDIT_ANTHROPIC_API_KEY`, is no
  longer read, and nothing falls back to it.
- `latest.json` and `run-meta.json` record the `keyFile`, `.env` or `~/.env`,
  that set an API-key run's key, and the key's errors name that file.
- The audit works on a default branch other than `main`. Each run reads the
  branch `origin`'s `HEAD` names, such as `master`, audits it, rebases its
  commit onto it, and opens its pull request into it.
- The feature's page recommends giving each project on a Mac that audits many
  its own schedule, at idle hours, so that no run waits past
  `lockWaitMinutes`.

### Manual follow-up

Adopters without the `memory-audit` feature need none and take the
[sync-only](docs/releases.md#sync-only-releases) path. An adopter with the
feature whose `.env` sets `MEMORY_AUDIT_ANTHROPIC_API_KEY` renames the line to
`ANTHROPIC_MEMORY_AUDIT_API_KEY` to keep its own key, or deletes it to use the
shared key in `~/.env`; no reinstall is needed. Podhaven's and screenr's
`.env` files no longer set it. Update their pages that name the old variable
or say the audit bills the project's own key:

- podhaven: `memoryAudit.context` in `.config/knowledge.json`, the scheduled
  memory audit section of `docs/development-workflow.md`, and
  `memory/memory-audit-model-selection.md` with its entry in
  `memory/README.md`.
- screenr: the scheduled memory audit section of
  `docs/development-workflow.md`, including its billing bullet, and the
  memory audit lines of `.env.example`. Nothing in this sync runs in
  production, so its commit ends with screenr's `Screenr-Deploy: skip`
  trailers; its CI otherwise deploys every push.

### Verified

`bin/check` passed 139 tests on macOS 27.0.1 with Python 3.15.2 and Git
2.56.1. The new key and default-branch tests failed before the change: the
old name still billed the key, `~/.env` was never read, and an origin without
`main` failed with "couldn't find remote ref main". On GitHub,
`git ls-remote --symref origin HEAD` named `master` for jubishop.github.io
and `main` for podhaven. No real audit ran before the release.

## 3.11.0 — 2026-11-13

### Synced

- The `memory-audit` feature proposes its changes for the user to merge
  instead of pushing them to `main`. An audit with changes pushes its commit
  to a new `memory-audit/<run folder>` branch, opens an unassigned issue
  listing each change with the model's evidence and holding the audit report,
  and opens a pull request from the branch that closes the issue. The user
  merges it, or an agent that works unassigned issues reviews it; the audit
  never merges, assigns, or closes its own work. If the issue or pull request
  cannot be opened, the runner deletes the branch, closes any issue it opened
  as not planned, and fails the run.
- While a pull request from a `memory-audit/` branch is open, each run skips
  before it gathers evidence, even with `--force`, and `latest.json` records
  the pull request. The next audit after it merges or closes covers whatever
  changed meanwhile, and a run that publishes deletes the branches earlier
  audits left.
- `latest.json` records a publishing run's `branch`, `issue`, and
  `pullRequest` beside its `publishedCommit`. The prompt tells the model that
  its report goes into the issue, and that an audit pull request closed
  without merging is a rejected change, to propose again only on newer
  evidence. The issue says the same, so an agent that finds it open after
  its pull request closed unmerged closes it as not planned instead of
  applying the changes.
- The issue mentions no one: the runner puts a zero-width space after each
  bare `@` in the model's evidence and report, outside code and links, so a
  Swift attribute such as `@MainActor` notifies no GitHub user.

### Manual follow-up

Adopters without the `memory-audit` feature need none and take the
[sync-only](docs/releases.md#sync-only-releases) path. Podhaven and screenr,
which enable it, need no reinstall; their next audit publishes the new way.
Update their pages that say the audit commits to `main`:

- podhaven: the scheduled memory audit section of
  `docs/development-workflow.md`.
- screenr: the scheduled memory audit section of
  `docs/development-workflow.md`, including its deployment bullet, since CI
  now runs on the audit's pull request and its merge, and the memory audit
  paragraph in `memory/README.md`. The `Screenr-Deploy` trailers stay on the
  audit's commit, which a squash or rebase merge keeps; a merge commit does
  not carry them.

### Verified

`bin/check` passed 137 tests on macOS 27.0.1 with Python 3.15.2 and Git
2.56.0. Against real Git remotes and a fake `gh`, an audit with changes
leaves `main` alone, pushes its branch to every push URL, and opens an issue
with no assignee or labels and a pull request whose body closes it. The
issue's evidence and report quiet bare mentions such as `@MainActor` but
leave code, email addresses, and links as written. A forced
run then skips while that pull request is open, another branch's open pull
request does not count, and the run after the merge audits again and deletes
the merged branch. A refused pull request closes the issue as not planned,
deletes the branch, and opens the failure issue. The new publishing tests
failed before the change, which pushed to `main` and opened nothing. The
`gh` 2.103.3 flags the runner uses match its help. No real audit ran
before the release.

## 3.10.0 — 2026-11-13

### Synced

- The engineering policy's
  [hosted CI](starter/docs/foundation/engineering-policy.md#hosted-ci)
  fallback, a local `bin/check --full` pass on the delivered revision, covers
  every job GitHub refuses to start, whatever the cause, such as a failed
  payment, not only an exhausted Actions quota or rate limiting. A refused
  job has a failure annotation beginning "The job was not started because"
  and no steps or runner.
- It also covers a job left queued, with no runner, for 10 or more minutes
  while every self-hosted runner matching its labels was `offline`, or
  `online` and not busy. GitHub never moves such a job to a hosted runner
  and ends it only after 24 hours, so an adopter whose runner went down had
  to wait until it was back. A busy runner restarts the count, a job that
  started on a runner is a failure even if the runner then went offline, and
  a job GitHub ended after 24 hours counts only when listings had already
  shown its runners down for 10 minutes. The section gives the `gh api`
  commands that show the job queued and each runner's state, read across
  the 10 minutes. The evidence rules, exclusions, and anchor are unchanged.

### Manual follow-up

Health, kidsbank, trading, vidservey, and will keep the earlier home rule in
`docs/development-workflow.md`, which allows the fallback only when "GitHub
CI is blocked solely by confirmed Actions quota exhaustion or GitHub rate
limiting" and, as the project's own rule, overrides the policy there. In
each, widen that cause to the policy's: GitHub refused to start the job, for
any reason, or the self-hosted runners it needs stayed down, linking
`foundation/engineering-policy.md#hosted-ci` for how to tell. Keep the rest
of the paragraph, such as trading's `floor` job. In vidservey and will, also
drop the next paragraph's requirement to confirm quota exhaustion from the
account's billing, with its statement that a failed-payment notice doesn't
prove it. The owner accepted both exceptions on 2026-10-14 while
reconciling each project's CI guidance with the home account's rule, which
now covers any refused job. Keep the paragraph's acceptance date and its
limits on what the exception authorizes. Run `bin/check --documents-only`,
commit with the synced files, push without `[skip ci]`, and confirm CI.

Home-infra's own rule, from jubishop/home-infra#99, already covers both cases
with its runner's details and needs no change, and pantrydates keeps its
owner's choice of no local fallback. Every other adopter takes only the
synced files.

### Verified

`bin/check` passed 132 tests on macOS 27.0.1 with Python 3.15.2 and Git
2.56.0. On 2026-11-13 the section's runner listing against home-infra
printed `nvr-home-infra-1`, `online`, `false`, and its labels
`self-hosted,Linux,X64,nvr`, and its job query printed a completed job's
status, runner, and `self-hosted,nvr` labels. No adopter overrides the
engineering policy, and a search of every adopter's own pages found the
narrower rule only in the five named above.

## 3.9.4 — 2026-11-10

### Synced

- `bin/doctor` and `bin/setup` accept a `core.hooksPath` that names another
  checkout's `bin/hooks` in the same clone, such as the primary checkout's by
  absolute path, while its hook files match the checkout's own. Before, a
  linked worktree's `bin/doctor` reported "Bundled hooks are not active" and
  its `bin/setup` stopped with advice to set `knowledge.hooks external`,
  while `bin/setup` in the checkout that the path named reset the clone-wide
  setting to the relative `bin/hooks`. Setup now leaves a path that already
  names the bundled hooks unchanged. When a shared hook differs or is
  missing, both name the event and link the new
  [shared hooks](starter/docs/foundation/knowledge-search.md#shared-hooks)
  section, which says to bring the checkout that is behind up to date
  rather than repoint the path.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path. Screenr, whose clone names its primary checkout's `bin/hooks`, needs
no step beyond the sync.

### Verified

`bin/check` passed 132 tests on macOS 27.0.1 with Python 3.15.2 and Git
2.56.0. In a fixture whose `core.hooksPath` names the main checkout's
`bin/hooks` by absolute path, `bin/doctor` passes and `bin/setup` leaves the
path unchanged in that checkout and a linked worktree. The new test failed
before the fix: the worktree's doctor reported "Bundled hooks are not
active", and setup in the main checkout reset the path to `bin/hooks`. A
changed shared `pre-push` fails both in the worktree, naming the event, and a
copy of the bundled hooks outside the clone still counts as existing hooks.
In a linked worktree of Screenr, whose clone names its primary checkout's
`bin/hooks`, this bundle synced with `--ref WORKTREE` made `bin/doctor` exit
0, and `bin/setup` left `core.hooksPath` unchanged.

## 3.9.3 — 2026-11-09

### Synced

- In a GitHub Actions partial clone, the whitespace check and
  `bin/check --fetch-base` find the paths the sparse checkout leaves out from
  its own patterns, cone or not, through `git sparse-checkout check-rules`.
  3.9.2 found them by a skip-worktree bit or a missing blob. Git stores blobs
  by content, so a `.env` whose committed content matched a checked-out
  file, such as an emptied `.env` beside an empty file, counted as checked
  out once an earlier step wrote it: `--fetch-base` fetched its base
  version, and the check reported the written file's whitespace. A deleted
  `.env` leaves neither signal, so `--fetch-base` fetched its base version
  too.
- In such a clone, the whitespace check and `--fetch-base` also skip the
  base version of a file the run deletes, which adds no lines, unless the run
  adds a file too, for Git's rename detection to compare. So a file that a
  run moves and edits still passes on whitespace it already had.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path. Trading's sparse jobs, the only ones in the fleet, need no change.

### Verified

`bin/check` passed 131 tests on macOS 27.0.1 with Python 3.15.2 and Git
2.56.0. In the partial-clone test, `.env`'s base version stays on the server
in pull requests that empty `.env` to match a checked-out file and that
delete it, with a step writing `.env` before the check, and the run's own
errors still fail. A deleted file's base stays there too when the run adds
no file, and a file the run moves and edits passes on whitespace it already
had. A cone-mode sparse checkout set by `git sparse-checkout set`, checked
by hand, left out a step-written path the same way.

## 3.9.2 — 2026-11-09

### Synced

- In a GitHub Actions partial clone, the whitespace check and
  `bin/check --fetch-base` keep leaving out a path the sparse checkout
  excludes after an earlier step writes a file there, such as a `.env` for
  tests. 3.9.1 found such paths by their skip-worktree bit, which Git clears
  once a file exists at the path, so `--fetch-base` fetched `.env`'s base
  version, the check then reported the written file's whitespace, and a push
  that created its branch failed with Git's missing-object error. A changed
  path whose index blob the checkout never fetched now counts as excluded
  too.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path. No adopter's CI writes a sparse-excluded path before `bin/check`, so
trading's sparse `test` job behaves as before.

### Verified

`bin/check` passed 131 tests on macOS 27.0.1 with Python 3.15.2 and Git
2.56.0. The partial-clone test writes a `.env` with whitespace errors in the
CI checkout before the check, in pull requests that do and don't change
`.env`, one after `git status` saves the index, and in a push that created
its branch. The check and `--fetch-base` leave it out, fetch neither of
`.env`'s blobs, and still fail on the run's own errors.

## 3.9.1 — 2026-11-09

### Synced

- In a GitHub Actions job whose checkout is a partial clone, which any
  `sparse-checkout` makes, the whitespace check no longer fails with Git's
  credential error. Such a clone leaves the base's version of the files a run
  changes on GitHub, and 3.9.0's check reads them, so Git tried to fetch them
  without the token that `persist-credentials: false` removes. There the
  check now fetches nothing, leaves out paths the sparse checkout excludes,
  and fails with its own fix when a file it reads is missing. The new
  `bin/check --fetch-base`, run with the job's token in a step before
  `bin/check`, fetches just those files, handing the token to that one fetch
  without writing it to the checkout's config. The engineering policy's
  [hosted CI](starter/docs/foundation/engineering-policy.md#hosted-ci)
  section shows the step. Full clones, local runs, and other hosts behave as
  before.

### Manual follow-up

Trading's `test` job in `.github/workflows/ci.yml`, the only adopter job that
runs `bin/check` in a sparse checkout, needs two changes in the same pull
request as the sync, since trading's rules send workflow changes through one.
Its `actions/checkout` step gets `fetch-depth: 0`, 3.9.0's follow-up, which
trading hasn't taken yet. Before `Check repository and application`, under
the same `if:` condition, a new step runs `bin/check --fetch-base` with
`GH_TOKEN: ${{ github.token }}`, and the workflow test that emulates the
checkout runs it too and still finds `.env`'s blob unfetched. Confirm that CI
passes on the pull request and on the `main` push after merge. Every other
adopter takes only the synced files, committed with `[skip ci]` as in a
[sync-only release](docs/releases.md#sync-only-releases).

### Verified

`bin/check` passed 130 tests on macOS 27.0.1 with Python 3.15.2 and Git
2.56.0. A new test serves a bare repository over HTTP only to requests with a
token, as GitHub serves a private repository, and checks it out as trading
does: a `blob:none` fetch with full history and a sparse checkout without
`.env`. It covers the check's fix without `--fetch-base`, pull request and
push runs after it, and `.env`'s blobs staying on the server. Against GitHub
itself, in such a checkout of trading's pull request 527 with no Git
configuration, `bin/check --fetch-base` fetched the base version of 4 changed
files with a token, the check then passed, and `.env` stayed unfetched.

## 3.9.0 — 2026-11-09

### Synced

- In a GitHub Actions pull request or push run, `bin/check` and
  `bin/check --full` fail on whitespace errors in the commits the run adds.
  CI's checkout has no `origin/HEAD`, so since 3.8.2 the check there read
  only uncommitted changes, which CI never has. A pull request's commits now
  count from where it left its base branch, and a push's from the commit it
  replaced, both read from GitHub's event. Content already on the default
  branch still passes, and a push that creates its branch, or that rewrote
  history past the commit it replaced, still checks only uncommitted changes.
  A checkout too shallow to reach the base fails with the fix instead of
  passing without reading the commits. The engineering policy's
  [hosted CI](starter/docs/foundation/engineering-policy.md#hosted-ci)
  section asks for full history in each job that runs `bin/check`.

### Manual follow-up

Every adopter whose CI runs `bin/check` or `bin/check --full` for pull
requests or pushes adds `fetch-depth: 0` to that job's `actions/checkout`
step, beside `persist-credentials: false`, in the same commit as the sync;
without it, the job's next pull request or push run fails. At release, these
are the `check` job in `.github/workflows/check.yml` of artisanalsoftware.com,
health, home-infra, jeeves, jubishop.github.io, kidsbank, news,
offline-librarian, pantrydates, printing, radio, scoreboard, sourdough,
stories, taxes, vidservey, vps-infra, and will; screenr's `static` job in
`check.yml`; steam-starter's `linux` job in `build.yml`; and trading's `test`
job in `ci.yml`. Commit without `[skip ci]`, push, and confirm that CI passes
on the pushed commit. Podhaven runs no `bin/check` in CI and takes only the
synced files. New adoptions' workflow already fetches full history.

### Verified

`bin/check` passed 128 tests on macOS 27.0.1 with Python 3.15.2 and Git
2.56.0. A test that emulates `actions/checkout` against a local remote, with
GitHub's event variables, covers a pull request's merge commit, a push, and
a shallow checkout. Full history costs little: on 2026-11-09, a full bare
clone of artisanalsoftware.com, at 81 MB the largest adopter, took the same 4.0
seconds as a depth-1 clone, and screenr's took 2.3 seconds against 1.9.

## 3.8.2 — 2026-11-09

### Synced

- `bin/check` and `bin/check --full` fail on whitespace errors a branch has
  already committed. They ran `git diff --check` only on staged and
  unstaged changes, so after a commit the whitespace check passed whatever
  it held. The check now compares the working tree with where the branch
  left `origin`'s default branch, or with the empty tree before anything is
  fetched or pushed. Content already on the default branch, such as a
  fixture, still passes, and a fix counts once it's in the working tree. A
  clone without `origin/HEAD`, such as CI's shallow checkout, still checks
  only uncommitted changes. The
  [engineering policy](starter/docs/foundation/engineering-policy.md#checks)
  describes the check and how `.gitattributes` exempts a file.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path. Twelve adopters have whitespace errors on their default branch, mostly
in data files such as RSS fixtures, CAD exports, and Xcode project files.
The check leaves them alone, and it gave the same result as before in every
adopter's primary checkout and in all 29 of their linked worktrees.

### Verified

`bin/check` passed 127 tests on macOS 27.0.1 with Python 3.15.2 and Git
2.56.0. In every adopter on 2026-11-09, the whitespace check took 0.08 to
0.21 seconds, found the base at `HEAD` in each primary checkout, and gave
the same result as the old check in each linked worktree, including
branches up to 10 commits ahead. In a simulated CI checkout, shallow and
detached, a default branch with trailing whitespace still passed.

## 3.8.1 — 2026-11-06

### Synced

- The managed `pre-push` hook no longer refuses a push whose local refspec
  contains spaces, such as `git push origin ':/Add a probe file:main'`. Git
  passes the local ref to the hook as typed, and the hook split each input
  line on whitespace, so it failed closed on every such push, even one that
  changed no Markdown. It now reads the other three fields from the right,
  since only the local ref can hold spaces, and checks the push like one
  naming a branch. Input it still can't read, such as a line without two
  object names, refuses the push as before.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path.

### Verified

`bin/check` passed 126 tests on macOS 27.0.1 with Python 3.15.2 and Git
2.56.0. In a throwaway clone of will synced with this release and pushing to
a local bare remote, a non-Markdown commit went through when pushed as
`:/Add a probe file:refs/heads/by-message`, and a page with a broken link
pushed through a `:/<message>` refspec was refused with
`docs/hook-probe.md: missing link destination missing-page.md`, as it was
when pushed by branch name.

## 3.8.0 — 2026-11-06

### Synced

- A managed `pre-push` hook runs `bin/check --documents-only` whenever a
  push changes Markdown, and Git refuses the push when it fails. Since
  3.7.2, text has waited for that check, but only the policy asked for it,
  so a skipped check could still let a broken link or missing index entry
  reach the default branch and fail the next unrelated change's
  `bin/check`, as it did twice in screenr. The hook checks each pushed
  revision in a disposable clone, so it catches a page left out of the
  commit, and an uncommitted draft doesn't block a clean push. Pushes that
  change no Markdown skip it, and a new branch is checked when its unpushed
  commits change Markdown. `bin/setup` and `bin/doctor` treat it like the
  other bundled hooks.
- An executable, project-owned `bin/pre-push-application` holds a project's
  own pre-push checks. The managed hook runs it after the document checks
  pass, with Git's arguments, standard input, and environment, and its
  failure refuses the push.
- The engineering policy's new
  [pre-push hook](starter/docs/foundation/engineering-policy.md#pre-push-hook)
  section allows `git push --no-verify` only for a broken hook. Another hook
  manager now forwards `pre-push` too, with its stdin, as
  [existing hooks](starter/docs/foundation/knowledge-search.md#existing-hooks)
  describes. The memory audit's page notes that its push skips the hook
  because the audit already runs the same checks.

### Manual follow-up

Health and screenr keep their own `bin/hooks/pre-push`, which runs Xcode
checks before a push, so sync reports a conflict there and writes nothing.
In each, move that hook to `bin/pre-push-application` and update the tests,
docs, and memory that name its old path. Commit the move, then sync, commit
the synced files, and push both commits.

- **health:** the hook works unchanged at its new path. Update
  `tests/test_pre_push.py` and the hook's link in
  `docs/development-workflow.md`.
- **screenr:** the hook imports `bin/_ios_check_records.py` through
  `HOOK.parents[1]`, which becomes `HOOK.parent`. Its `dispatch()` handed a
  push from a worktree to that worktree's own copy, because
  `core.hooksPath` names the primary checkout's `bin/hooks`; the managed
  hook now does that, since it runs the pushing checkout's
  `bin/pre-push-application`. Drop or adapt `dispatch()` and the `GATE`
  paths, and update `tests/test_pre_push.py`,
  `docs/development-workflow.md`, and `memory/parallel-agent-gotchas.md`.
  Run `bin/check --full`. A worktree whose branch predates the move runs
  no pre-push checks until it merges the default branch.

Every other adopter takes only the synced files. An adopter whose hooks come
from another manager (`knowledge.hooks external`) would forward `pre-push`;
none does at release.

### Verified

`bin/check` passed 126 tests on macOS 27.0.1 with Python 3.15.2 and Git
2.56.0. In throwaway clones synced with this release and pushing to a local
bare remote, will refused a push that added a page with a broken link, with
`docs/hook-probe.md: missing link destination missing-page.md`, and let the
sync and a clean Markdown edit through in about 0.24 seconds each. In
health, with its hook moved unchanged to `bin/pre-push-application`, the
managed hook passed it Git's input, and it refused a push whose macOS-only
inputs differed from the checkout. Across all 22 adopters on 2026-11-06,
the disposable clone took 0.04 to 0.27 seconds and the document checks 0.06
to 0.65 seconds. The starter checks passed on Ubuntu and macOS, and on
GitHub's `ubuntu-latest` runner the strict real-QMD smoke check passed with
QMD 2.8.3 and node-llama-cpp 3.22.3.

## 3.7.2 — 2026-11-05

### Synced

- Text, such as Markdown and AI skill prose, still goes directly to the
  default branch with no tests, pull request, or hosted CI run, but only once
  `bin/check --documents-only` passes. Since 2.6.0 the policy had said text
  needs no checks, and hosted CI skips Markdown-only changes, so nothing
  checked them. The document checks read every tracked Markdown file, so a
  page with a broken link or a missing index entry reached the default branch
  and failed the next unrelated change's `bin/check`, as it did twice in
  screenr. The engineering policy's kinds of change, check schedule, and
  hosted CI section, and the managed `AGENTS.md` block, now require the
  check. Hosted CI still skips Markdown-only changes.

### Manual follow-up

Project rules take precedence, so a project page that still says text needs
no checks keeps the old rule. In each adopter below, reword it to require
`bin/check --documents-only`, run that check, and commit the edit with the
sync:

- news: `AGENTS.md`, "Text-only changes need no checks."
- podhaven: `AGENTS.md`, "Documentation needs no checks", and in
  `docs/development-workflow.md` the check decision's note and the
  "Documentation-only delivery" row.
- screenr: `docs/testing.md`, "Markdown edits need no checks."
- stories: `AGENTS.md`, "text-only changes need no checks"; the Markdown-only
  bullet in `docs/development-workflow.md`; and `memory/change-delivery.md`.
- trading: the "Pull requests" paragraph in `AGENTS.md`, and the sentence in
  `docs/development-workflow.md` that sends other Markdown to `main` without
  checks. Its rules send any change to `AGENTS.md` outside the managed block
  through a pull request, so deliver both pages that way after the sync.

Sourdough's rule that no check runs before a push is the owner's deliberate
choice of 2026-10-15; leave it. Other adopters take only the synced files.

### Verified

`bin/check` passed 124 tests on macOS 27.0.1 with Python 3.15.2. In
adopters, `bin/check --documents-only` took 0.05 seconds in will and 0.7
seconds in screenr. In a throwaway clone of will, it passed, then failed on
`missing link destination missing-page.md` after a Markdown-only change added
a page with a broken link. The starter checks passed on Ubuntu and macOS, and
on GitHub's `ubuntu-latest` runner the strict real-QMD smoke check passed
with QMD 2.8.3 and node-llama-cpp 3.22.3.

## 3.7.1 — 2026-11-01

### Synced

- The engineering policy no longer suggests `node-version: lts/*` with
  `check-latest: true` for CI. `actions/setup-node` resolves `lts/*` from the
  `actions/node-versions` manifest, which can mark a new LTS major days after
  nodejs.org does, and `check-latest` reads the same manifest. On 2026-11-01,
  four days after nodejs.org marked v26.13.0 LTS, screenr's CI still
  installed Node 24.22.2 while its machines and server ran 26.13.0. CI now
  resolves the newest LTS from nodejs.org's release index and passes that
  exact version to `setup-node`, and the policy shows the two steps.

### Manual follow-up

In each adopter whose CI gives `actions/setup-node` `lts/*`, as
`node-version` or through `node-version-file`, add the policy's
[resolver step](starter/docs/foundation/engineering-policy.md#runtime-and-toolchain-versions)
before `setup-node`, then replace that input and `check-latest` with
`node-version: ${{ steps.node.outputs.version }}`. Keep the step's other
inputs, such as `cache`, and give the resolver any `if:` condition the
`setup-node` step has. Version files keep `lts/*` for developer machines. At
release, these are artisanalsoftware.com, kidsbank, podhaven
(`sentry-intake.yml`), sourdough, steam-starter (both jobs in `build.yml`,
including its `windows-latest` build), stories, and vidservey; screenr already
resolves the version from nodejs.org. Run the checks the workflow change needs,
push, and confirm that CI installs the newest LTS. Other adopters take only the
synced files.

### Verified

`bin/check` passed 124 tests on macOS 27.0.1 with Python 3.15.2, and
actionlint accepts the starter's QMD compatibility workflow, which now uses
the same two steps. Under `bash -e`, the resolver step read 26.13.0 from
nodejs.org's live index, chose 26.13.0 over 9.0.0 in an unsorted index, and
failed for a missing index and for one with no LTS release. On GitHub's
`ubuntu-latest` runner, the workflow's two steps installed Node 26.13.0, and
its strict real-QMD smoke check passed with QMD 2.8.3.

## 3.7.0 — 2026-10-29

### Synced

- The `memory-audit` feature's tool boundary check also requires that `jq`
  cannot import a JSON file outside the repository as a module, as in
  `jq -n 'import "outside" as $x {search: ".."}; $x'`. jq takes a module's
  path from inside the program, not from a file argument, and reads it from
  any directory, dotfiles included, so under the audit's `Bash(jq *)` allow
  rule only Claude Code's refusal of the import keeps the model from reading
  any JSON file on the machine. Claude Code 2.1.312 denies every form of the
  import, so nothing was exposed; this is regression coverage.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path; the next scheduled audit runs the extended check without a reinstall.

### Verified

`bin/check` passed 123 tests on macOS 27.0.1 with Python 3.15.1. Real
Claude Code 2.1.312 and QMD 2.8.3 ran the check with no model request in a
throwaway adopter, and it passed in about a second with the import probe
denied for want of approval. A fake Claude Code that allows the import fails
the check, because jq 1.8.2 prints the outside file's token.

## 3.6.0 — 2026-10-29

### Synced

- The `memory-audit` feature's tool boundary check also probes the audit's
  own allow rules, `jq` and `qmd search`, and its Grep and Glob tools, the
  routes most likely to widen in a later Claude Code release. It now requires
  that `jq` cannot read a file outside the repository, as in
  `jq -R . ../outside.txt` and `jq --rawfile f ../outside.txt -n '$f'`; that
  neither allow rule covers a command chained after it, as in
  `jq -n 1; cat ../outside.txt` and `qmd search … && printenv`; and that Grep
  and Glob stay inside the repository. Claude Code 2.1.312 denies all of
  these, so nothing was exposed; this is regression coverage.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path; the next scheduled audit runs the extended check without a reinstall.

### Verified

`bin/check` passed 123 tests on macOS 27.0.1 with Python 3.15.1, on top of
3.5.1. Real Claude Code 2.1.312 and QMD 2.8.3 ran the check with no model
request, and it passed in about a second with every new probe denied, both
in a throwaway adopter and again in 3.5.1's reused scratch folder. The
same `jq -R`, Grep, and Glob calls aimed inside the repository printed the
file, so those probes would catch a widened route. Claude Code 2.1.312 denies
`jq --rawfile`, `--slurpfile`, and `--arg` even inside the repository, so the
`--rawfile` probe guards that refusal as well as the working-directory check.

## 3.5.1 — 2026-10-29

### Synced

- The `memory-audit` feature clones every run to the same path,
  `.cache/memory-audit/repository`, instead of a new folder under
  `.cache/memory-audit/runs/`. Claude Code records the folder it works in as a
  project in `~/.claude.json` when the project tracks
  `.claude/settings.local.json`, and nothing prunes those entries, so each
  audit left one more behind: podhaven had six by 2026-10-28. Its large tool
  output under `~/.claude/projects/` now lands in one folder per project too,
  which Claude Code's `cleanupPeriodDays` sweep prunes. The tool boundary
  check's scratch repository moves to `.cache/memory-audit/boundary/` for the
  same reason. Run folders keep the same logs, context, report, and patch, and
  a run replaces a clone that an interrupted run left.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path; the next scheduled audit uses the new paths without a reinstall. The
entries that earlier runs left in `~/.claude.json` stay, about 285 bytes each,
since removing them means editing a file Claude Code rewrites. Claude Code's
own sweep removes their `~/.claude/projects/` folders once their files age
past `cleanupPeriodDays`.

### Verified

`bin/check` passed 123 tests on macOS 27.0.1 with Python 3.15.1. Real Claude
Code 2.1.312 ran the runner's `run_model` against its local stand-in API, so
with no model request, in an isolated `CLAUDE_CONFIG_DIR`, three times in
repositories that track `.claude/settings.local.json` and print a large `jq`
output. New paths per run left three `~/.claude.json` entries and three
`~/.claude/projects/` folders; one reused path left one of each. Without the
tracked file it wrote no entry but still one folder per path. Claude Code
2.1.312's retention sweep deletes `tool-results` files older than
`cleanupPeriodDays`, then empty session and project folders. QMD is unchanged
since 2.12.0's strict real-QMD smoke; this release does not rerun it.

## 3.5.0 — 2026-10-28

### Synced

- The `memory-audit` feature checks its tool boundary before every model run.
  3.3.1 keeps the key from the model's tools through Claude Code behavior
  that any release can change: scrub mode, the `jq` allow rule, and
  `INDEX_PATH` reaching tools. The runner now runs the installed Claude Code
  with its own model-run and search setup and the audit's flags against a
  local stand-in for the Anthropic API, which scripts the tool calls, so the
  check makes no model request and costs nothing. If `jq` reads
  `ANTHROPIC_API_KEY` or a secret-named canary, if `jq` on the context or
  `qmd search` on the clone's index stops working, or if an environment or
  process listing or a read outside the repository runs, the audit fails
  before the model starts and reports through its notification and
  `Memory audit failing` issue.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path; the next scheduled audit runs the check without a reinstall.

### Verified

`bin/check` passed 121 tests on macOS 27.0.1 with Python 3.15.1. Real Claude
Code 2.1.312 and QMD 2.8.3 ran the check in a throwaway adopter, with no model
request. With 3.3.0's model run and search setup, it failed because `jq`
printed the canary key through `env` and `$ENV`, and printed
`ANTHROPIC_API_KEY`. With 3.3.1's and this release's, it passed in about a
second. 3.3.1's scrubbed model run with 3.3.0's search setup failed because
`qmd search` missed the scratch note.

## 3.4.0 — 2026-10-28

### Synced

- `bin/check` runs ShellCheck on each `bin/` script whose shebang names `sh`,
  `bash`, `dash`, or `ksh`, in that dialect, directly or through `env` and
  with or without flags, such as `#!/usr/bin/env bash` or `#!/bin/bash -e`.
  Before, it linted only scripts starting with `#!/bin/sh`, so bash scripts
  such as deploy tooling went unlinted. `.envrc` is still linted as bash, and
  scripts outside `bin/` still are not. The engineering policy names the
  linted files and notes that a project's `.shellcheckrc` configures
  ShellCheck.

### Manual follow-up

Every adopter runs `bin/check` after syncing and fixes any finding in a newly
linted script before committing the sync. At release time, ShellCheck 0.11.0
passed every adopter's newly linted scripts except these:

- health: SC2029 notes in `bin/deploy.sh` and
  `bin/rollback-health-server.sh`, where `ssh` commands expand variables on
  the client. Escape any expansion meant for the server, and add
  `# shellcheck disable=SC2029` above each intended one, as trading's
  `bin/deploy.sh` does.
- podhaven: SC1091 notes in `bin/check-sentry-feedback` and
  `bin/check-sentry-issues`, whose `# shellcheck source=` directives need
  ShellCheck to follow sourced files. Add a root `.shellcheckrc` containing
  `external-sources=true`.

trading may then drop the `bin/` half of the bash lint test it added in
jubishop/trading#378.

### Verified

`bin/check` on macOS 27.0.1 with Python 3.15.1, and the starter checks on
Ubuntu and macOS. The new `bin/check` run with ShellCheck 0.11.0 in clones of
health, podhaven, and trading failed on the findings above and passed
trading; a `.shellcheckrc` with `external-sources=true` cleared podhaven's.
QMD is unchanged since 2.12.0's strict real-QMD smoke (QMD 2.8.3 with
node-llama-cpp 3.22.2); this release does not rerun it.

## 3.3.1 — 2026-10-28

### Synced

- The `memory-audit` feature keeps the project's API key away from the
  model's tools. In 3.3.0, Claude Code passed `ANTHROPIC_API_KEY` to Bash, and
  the allowed `jq -n 'env.ANTHROPIC_API_KEY'` printed it without approval, so
  a prompt-injected issue could steer the key into a published note or the
  failure issue. Every model attempt now runs with
  `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`, which bills the key but withholds it
  and other secret-named variables from tool processes.
- Scrub mode also withholds `XDG_CACHE_HOME`, so the runner sets `INDEX_PATH`
  to the clone's search index, keeping `qmd search` off the user's own index.

### Manual follow-up

None. Adopters take the [sync-only](docs/releases.md#sync-only-releases)
path; the next scheduled audit runs the new runner without a reinstall.

### Verified

`bin/check` on macOS 27.0.1 with Python 3.15.1. Claude Code 2.1.312 ran the
runner's own `run_model` and flags on Haiku through the subscription with two
canary variables. On 3.3.0, `jq -n 'env.AUDIT_CANARY_API_KEY'` and `$ENV`
printed the secret-named canary; after the fix both printed `null`, while
`jq` on the context file, `qmd search` on the clone's index, `git show`, Read,
and Grep still worked. With a bogus `ANTHROPIC_API_KEY`, a SessionStart hook
saw the key in its environment without scrub mode and not with it, and the
API still answered 401 for that key. QMD is unchanged since 2.12.0's strict
real-QMD smoke; this release does not rerun it.

## 3.3.0 — 2026-10-28

### Synced

- The `memory-audit` feature runs `claude-sonnet-5-5` instead of
  `claude-haiku-5-5`, still at high effort.
- An audit bills the project's own Anthropic API key when the checkout's
  ignored `.env` sets `MEMORY_AUDIT_ANTHROPIC_API_KEY`. The runner reads only
  that line and passes the key to Claude as `ANTHROPIC_API_KEY` for the
  API-key attempt alone. Without the key, the audit uses the subscription
  login as before.
- When the API refuses the key for a low credit balance, a reached spend
  limit, or HTTP 401 or 403, the runner reruns that attempt on the
  subscription without a manual step. Other failures fail as before.
  `latest.json` records the `credential` used, which replaces `provider`, and
  the `fallback` with its `trigger`.

### Manual follow-up

Adopters without the `memory-audit` feature need none and take the
[sync-only](docs/releases.md#sync-only-releases) path. Each adopter with it
can add `MEMORY_AUDIT_ANTHROPIC_API_KEY=<key>` to its primary checkout's
`.env` and run `chmod 600 .env`; no reinstall is needed. A project page that
names the old model or calls the audit subscription-only should be updated:
podhaven's `memoryAudit.context`, model-selection memory note, and scheduled
audit section, and screenr's `.env.example` and scheduled audit section.

### Verified

`bin/check` on macOS 27.0.1 with Python 3.15.1, and the starter checks on
Ubuntu and macOS. Claude Code 2.1.312 with a bogus `ANTHROPIC_API_KEY`
reported `authMethod: api_key` from `ANTHROPIC_API_KEY`, and its `-p`
stream-json run exited 1 with a result event marked `is_error`,
`api_error_status: 401`, and "Invalid API key · Fix external API key". The
credit and spend-limit shapes come from Claude Code's error handling and are
covered by tests with recorded events; no paid API call was made. QMD is
unchanged since 2.12.0's strict real-QMD smoke (QMD 2.8.3 with node-llama-cpp
3.22.2); this release does not rerun it.

## 3.2.0 — 2026-10-25

### Synced

- Optional features. `bin/sync --enable <feature>` and `--disable <feature>`,
  with or after `--init`, change the features an adopter's
  `.project-starter.json` lists. Sync manages an enabled feature's files like
  the bundle's and lists its page in `docs/foundation/README.md`. An adopter
  that enables none receives only the version bump, and `bin/sync --status`
  shows each adopter's features. A new file whose path holds a file sync does
  not manage is a conflict.
- The `memory-audit` feature shares screenr's weekly local Claude audit of
  memory notes: `bin/memory-audit`, its runner and prompt, and
  `docs/foundation/memory-audit.md`. An optional `memoryAudit` object in
  `.config/knowledge.json` sets the repository, LaunchAgent label, schedule,
  failure-issue labels, commit trailers, active-index heading, and prompt
  context; `bin/memory-audit settings` prints them. The defaults keep
  `com.<owner>.<repo>.memory-audit` from `origin`, Saturday 06:00, and the
  starter's `Active pages` heading. Unlike screenr's copy, the audit pushes
  to every push URL of `origin`, labels a new failure issue (unlabeled when
  the labels cannot be applied), skips the model when no note is active, and
  fails before the model when `memory/README.md` lacks the heading.
- Every project's audit defaults to the same time, and runs take turns
  through a per-user lock at `~/.cache/project-starter/memory-audit.lock`.
  A run waits for its turn, up to `lockWaitMinutes` (180 by default), before
  fetching evidence, and the wait does not count against the 90-minute model
  limit. A run that waits longer fails and reports like any other failure.

### Manual follow-up

Adopters that do not enable a feature need none and take the
[sync-only](docs/releases.md#sync-only-releases) path; screenr and podhaven
take the full path. Sync refuses `--enable memory-audit` while a project's
own audit files exist, so they remove theirs first, then keep the
`## Scheduled memory audit` heading, which their memory pages link to.

**screenr**

1. Delete `bin/memory-audit`, `bin/_memory_audit.py`,
   `bin/memory-audit-prompt.md`, and `tests/test_memory_audit.py`, and
   commit.
2. Run `bin/sync --enable memory-audit /path/to/screenr`.
3. Add its settings to `.config/knowledge.json`:

   ```json
   "memoryAudit": {
     "schedule": {"weekday": "Saturday", "hour": 8, "minute": 0},
     "issueLabels": ["bug", "area: tooling"],
     "commitTrailers": {
       "Screenr-Deploy": "skip",
       "Screenr-Deploy-Reason": "The weekly memory audit changes only memory notes, which do not run in production."
     },
     "indexHeading": "Active memory index"
   }
   ```

4. Shorten `docs/development-workflow.md#scheduled-memory-audit` to link
   `docs/foundation/memory-audit.md` and keep only Screenr's specifics: the
   Saturday 08:00 start, two hours after podhaven's, the deployment trailers,
   the labels, and the audit decisions.
5. Run `bin/check --full`, commit, and push. In the primary checkout, run
   `bin/memory-audit settings`, confirm the label is
   `com.jubishop.screenr.memory-audit`, and rerun `bin/memory-audit install`.

**podhaven**

1. Delete `bin/memory-audit`, `bin/_memory_audit.py`,
   `bin/memory-audit-prompt.md`, `bin/memory-index`, `bin/_memory_index.py`,
   `bin/tests/test_local_memory_audit.py`, and
   `bin/tests/test_memory_audit.py`, and drop the `bin/memory-index` call
   from the index-coverage test in `bin/tests/test_knowledge.py`.
2. Delete `bin/_checks.py` and its override in `.project-starter.json`, so
   sync restores the managed copy, and commit.
3. Run `bin/sync --enable memory-audit /path/to/podhaven`.
4. In `memory/README.md`, remove the `ACTIVE_MEMORY_START` and
   `ACTIVE_MEMORY_END` markers but keep the list, and replace the
   `bin/memory-index` paragraph with the hand-maintained rule: link each
   active note, and the audit removes an archived note's entry.
5. Add its settings to `.config/knowledge.json`; it keeps the default
   Saturday 06:00, and `context` carries the project paragraph its prompt
   had:

   ```json
   "memoryAudit": {
     "issueLabels": ["memory-audit-failure"],
     "indexHeading": "Active notes",
     "context": "The user selected this local Claude Code job with Haiku through their Claude subscription to replace the paid OpenRouter memory audit and the later Codex job. That choice supersedes older model preferences in the notes. The Sentry Feedback GitHub workflow remains in use."
   }
   ```

6. Shorten `docs/development-workflow.md#scheduled-memory-audit` to link
   `docs/foundation/memory-audit.md`, and make its Project Starter section
   name only the `bin/_knowledge.py` override.
7. Delete `bin/knowledge-config`: only the old audit and its own test in
   `bin/tests/test_knowledge.py` use it, and no workflow or doc does. Move
   that test's `sentry-history` `includeByDefault: false` assertion into the
   lookup test that records the rendered collections, so the override keeps
   coverage, drop the now unused `include_local` parameter from the override's
   `config()`, and remove "for CI configuration" from the override's reason.
8. Run `bin/check --full`, commit, and push. In the primary checkout, run
   `bin/memory-audit settings`, confirm the label is
   `com.jubishop.podhaven.memory-audit`, and rerun `bin/memory-audit install`.

### Verified

`bin/check` on macOS 27.0.1 with Python 3.15.1, and the starter checks on
Ubuntu and macOS. A real audit ran in podhaven. QMD is unchanged since
2.12.0's strict real-QMD smoke (QMD 2.8.3 with node-llama-cpp 3.22.2); this
release does not rerun it.

## 3.1.0 — 2026-10-25

### Synced

- `bin/check --full` reuses a passing `bin/check-application` run for a clean
  checkout whose tree and environment passed in the last 12 hours, and says
  which commit passed. The record lives in the common Git directory, so
  worktrees share it. Uncommitted changes always run the application checks,
  and `bin/check --full --no-reuse` runs them regardless. The engineering
  policy describes the reuse.
- A new worktree, and `bin/prep-worktree`, run the project's executable
  `bin/setup-application`, so a worktree gets its dependencies, such as a
  `.venv`, without an agent rebuilding them. A failure in a new worktree is
  reported without stopping Git; `bin/prep-worktree` fails with it.

### Manual follow-up

A project that overrides `bin/_checks.py` ports the application-check reuse
to its copy. One that overrides `bin/_knowledge.py` runs
`bin/setup-application` for new worktrees and in `bin/prep-worktree`, as the
release's `setup_application` does.

### Verified

`bin/check` on macOS 27.0 with Python 3.15.1, and the starter checks on
Ubuntu and macOS. QMD is unchanged since 2.12.0's strict real-QMD smoke (QMD
2.8.3 with node-llama-cpp 3.22.2); this release does not rerun it.

## 3.0.1 — 2026-10-25

### Synced

- New projects' `docs/README.md` describes the foundation as "shared
  engineering and knowledge search policy", without 3.0.0's stray comma.
  Existing adopters keep their own copy of that project-owned page.

### Manual follow-up

None.

## 3.0.0 — 2026-10-25

### Synced

- td task tracking is retired; projects track work in their issue tracker.
  Sync removes `docs/foundation/task-tracking.md`, the managed `AGENTS.md`
  block drops its td rule, the managed `.gitignore` block no longer ignores
  `.todos/`, and the foundation index no longer lists task tracking.

### Manual follow-up

- Remove td from the project-owned pages that 2.x installed: the td sentence
  in `docs/development-workflow.md`, the task-tracking item and the sentence
  about linking issues from td in `README.md`, the td clause in
  `docs/README.md` and `memory/README.md`, and "task tracking" in the
  `foundation` collection's context in `.config/knowledge.json`. Edit any
  other project page that tells agents to use td or cites td task IDs.
- Move any unfinished task's remaining work into an issue, then delete the
  primary checkout's `.todos/` directory.

### Verified

`bin/check` on macOS 27.0 with Python 3.15.1. QMD is unchanged since 2.12.0's
strict real-QMD smoke (QMD 2.8.3 with node-llama-cpp 3.22.2); this release
does not rerun it.

## 2.13.0 — 2026-10-25

### Synced

- When a flaky test's fix does not fit the current change, agents file a
  GitHub issue for it right away, without waiting to be asked, or reuse the
  one that already tracks it, and name the issue when reporting the work. The
  engineering policy states the rule, and the managed `AGENTS.md` block
  summarizes it.

### Manual follow-up

None.

## 2.12.0 — 2026-10-24

### Synced

- Each knowledge refresh whose inputs changed runs `qmd cleanup` after
  `qmd embed`, so the index no longer keeps embedding chunks for replaced or
  removed pages. Lookups during cleanup wait or refuse, as during the rest of
  a refresh, and a failed cleanup fails the refresh. The knowledge-search page
  describes this and how to reclaim the vector space cleanup cannot free.

### Manual follow-up

A project that overrides `bin/_knowledge.py` adds `cleanup` after `embed` to
its refresh's QMD commands. Optionally, to reclaim vector blocks that cleanup
cannot free, delete `.cache/qmd/index.sqlite` and run `bin/qmd-index`, which
rebuilds it.

### Verified

QMD 2.8.3 with node-llama-cpp 3.22.2 (strict real-QMD smoke on an Apple M5
Pro with macOS 27.0.1), td 0.69.0, and Python 3.15.1.

## 2.11.1 — 2026-10-24

### Synced

- A single-file collection whose file is missing indexes nothing instead of
  failing every refresh and lookup with "Collection readme file is missing".
  Tools that search a sparse copy of the checkout without the README, such
  as podhaven's memory audit, work again, and the knowledge-search page says
  so.

### Manual follow-up

From 2.10.x, apply the 2.11.0 follow-up. A project that overrides
`bin/_knowledge.py` merges both releases' changes into its copy. The fleet's
copies were updated directly on 2026-10-24.

## 2.11.0 — 2026-10-24

### Synced

- A knowledge collection's pattern may name one Markdown file instead of
  `**/*.md`. QMD then indexes only that file in the collection's directory,
  and search freshness tracks it alone. The knowledge-search page documents
  this, and new projects' `.config/knowledge.json` adds a `readme` collection
  for the root `README.md`, so search returns `qmd://readme/README.md`.

### Manual follow-up

`.config/knowledge.json` is project-owned, so sync does not add the
collection. Add it to `collections`:

```json
"readme": {
  "path": ".",
  "pattern": "README.md",
  "context": {"/": "The project's purpose, main entry points, and development setup."}
}
```

A collection rooted at `.` with `**/*.md` should list `README.md` in its
`ignore` to avoid indexing the file twice. Then run `bin/check` and
`bin/qmd-index`, and confirm that `bin/doctor --json` counts one `readme`
document. No adopter synced 2.11.0; the fleet moved to 2.11.1 directly.

### Verified

QMD 2.8.3 with node-llama-cpp 3.22.2 (strict real-QMD smoke on an Apple M5
Pro with macOS 27.0.1), td 0.69.0, and Python 3.15.1.

## 2.10.1 — 2026-10-16

### Synced

- The managed `AGENTS.md` secrets rule drops its `.env` example, leaving
  "Keep secrets out of public repositories only; a private one may commit
  them."

### Manual follow-up

None.

## 2.10.0 — 2026-10-16

### Synced

- The managed `AGENTS.md` block keeps secrets out of public repositories only.
  A private repository may commit them, such as its `.env` by adding `!.env`
  after the `.gitignore` block, which still ignores `.env` by default.

### Manual follow-up

None required. A private project that restated this exception outside the
block can remove its copy.

## 2.9.0 — 2026-10-16

### Synced

- Only the recorded release version. The remote page that new projects copy,
  `docs/git-remotes.md`, now records only the primary `origin` remote with no
  second push destination, and the starter README and docs index match it.

### Manual follow-up

None required. A project-owned `docs/git-remotes.md`, `docs/README.md`, or
`README.md` that still describes a second push destination should be updated;
the fleet's copies were updated directly on 2026-10-16.

## 2.8.1 — 2026-10-15

### Synced

- Only the recorded release version. Project Starter's QMD maintenance guide
  now names the home repository's updater `~/bin/auto-update`, its new name.

### Manual follow-up

None.

## 2.8.0 — 2026-10-15

### Synced

- The engineering policy sorts changes into three kinds. Text, such as
  Markdown and AI skill prose, goes directly to the default branch without
  checks. Development code, such as tests, CI, hooks, tooling, and skill
  scripts, goes directly after its checks pass. Production code goes through a
  pull request after its checks. This corrects 2.6.0, which let tests, CI, and
  tooling skip checks.
- The managed `AGENTS.md` block summarizes the three kinds, and
  "Changes outside the runtime" is now "Kinds of change".

### Manual follow-up

None required. A project page that links to
`engineering-policy.md#changes-outside-the-runtime`, or that exempts tests, CI,
or tooling from checks, should be updated.

## 2.7.0 — 2026-10-15

### Synced

- Agents never ignore a flaky test. They fix it on the spot or make sure a
  GitHub issue tracks it. The engineering policy states the rule, and the
  managed `AGENTS.md` block summarizes it.

### Manual follow-up

None.

## 2.6.0 — 2026-10-15

### Synced

- Changes outside the runtime, which can't affect what runs when the
  application executes, go directly to the default branch without checks,
  tests, CI waits, or a pull request. They include Markdown, docs, memory,
  agent instructions, AI skills, and tests, CI, and tooling the running
  application doesn't use. Markdown edits no longer need
  `bin/check --documents-only`.
- A project's own rules take precedence over the managed block and the
  foundation pages wherever they differ, stricter or looser, so a project can
  set its own edge cases. Previously only stronger project rules won.
- A Project Starter sync goes directly to the default branch as a change
  outside the runtime, no longer as a carve-out that overrides project rules.

### Manual follow-up

None required. A project page that still requires checks or a pull request
for changes outside the runtime keeps doing so, because project rules take
precedence; remove such a rule unless it is a deliberate exception.

## 2.5.0 — 2026-10-15

### Synced

- A Project Starter sync with no manual follow-up needs no checks, CI, or
  deployment. Its commit holds only the synced files and carries `[skip ci]`,
  so GitHub Actions starts no push workflows, and it is pushed directly.

### Manual follow-up

None.

## 2.4.1 — 2026-10-15

### Synced

- The task workflow no longer warns against rotating td sessions to bypass
  review checks. Agents approve their own work with `td approve --self-review`.

### Manual follow-up

None.

## 2.4.0 — 2026-10-15

### Synced

- A Project Starter sync may go directly to the default branch without a pull
  request or review, even where the project otherwise requires one. It covers
  the files `bin/sync` writes, `.project-starter.json`, and manual follow-up
  that touches only workflows or documentation.

### Manual follow-up

If the project's own instructions require pull requests for changes a sync
makes, add the same carve-out there, since project rules may be stricter than
the foundation.

## 2.3.0 — 2026-10-15

### Synced

- The engineering policy's runtime and toolchain section says workflows
  reference GitHub Actions by major tag, such as `actions/checkout@v7`, not
  by commit SHA, and install CI tools at their latest version. A job that
  holds deployment credentials pins each third-party action it runs to a
  commit SHA, with that reason beside the pin.

### Manual follow-up

In each workflow, replace commit-SHA and exact-version action references with
the action's current major tag, and install CI tools at their latest version.
In a job that holds deployment credentials, keep each third-party action
pinned to a commit SHA and add a comment giving that reason. New adoptions'
GitHub workflow uses `actions/checkout@v7`.

## 2.2.0 — 2026-10-14

### Synced

- The engineering policy's new hosted CI section skips hosted CI for
  Markdown-only changes with trigger-level `paths-ignore: ['**.md']`. Those
  changes merge on a passing `bin/check --documents-only`. Projects whose
  Markdown affects behavior re-include those pages through a `paths` filter.
- When hosted CI cannot run only because the Actions quota is exhausted or
  GitHub is rate limiting, a local `bin/check --full` pass on the delivered
  revision satisfies the merge or release gate. CI is reported as
  unavailable, not passed.

### Manual follow-up

Add `paths-ignore: ['**.md']` to the `push` and `pull_request` triggers of
workflows that run checks. If Markdown affects behavior, use a `paths` filter
of `'**'`, `'!**.md'`, then those pages. Do not make a path-filtered workflow
a required check. New adoptions' GitHub workflow includes the filter.

## 2.1.3 — 2026-10-13

### Project-owned template

- New adoptions' `docs/development-workflow.md` describes a project with no
  application yet: it has no `bin/check-application`, declares no application
  runtime, and deploys nothing, and each section says what to record when
  that changes. The README introduction asks a project without an
  application to say so. Only new adoptions receive these pages; sync never
  changes existing project-owned pages.

### Manual follow-up

None. The guide now explains that its links resolve from this repository and
where copied pages live in the target.

## 2.1.2 — 2026-10-09

### Project-owned template

- `docs/git-remotes.md` reads correctly once adoption fills in the actual URLs,
  and recommends SSH for GitHub because HTTPS pushes that change workflow files
  need a token with the `workflow` scope. Only new adoptions receive it; sync
  never changes existing project-owned pages.

## 2.1.1 — 2026-10-09

### Synced

- The engineering policy asks CI setup actions to check for the latest
  release (`check-latest: true`) instead of reusing a cached older one.

### Manual follow-up

Add `check-latest: true` beside `lts/*`, `stable`, or similar version
selectors in CI setup actions. New adoptions' GitHub workflow uses
`ubuntu-latest`.

## 2.1.0 — 2026-10-09

### Synced

- `bin/setup` runs an executable `bin/setup-application` after the foundation
  setup succeeds, so application dependencies install with one command.
- The engineering policy uses the latest stable runtimes and tools: projects
  declare minimum versions, CI installs the latest stable release (`lts/*` for
  Node), and machines and servers update automatically with rollback.
- `bin/doctor` no longer reports a tested QMD version or warns about newer
  releases.

### Manual follow-up

- Replace exact runtime pins: `engines` and similar fields declare minimums,
  version files say `lts/*`, CI installs `lts/*`, and application checks
  accept any version at or above the minimum.
- Move dependency installation from separate setup instructions into
  `bin/setup-application`.

## 2.0.1 — 2026-10-09

### Synced

- Hook setup messages and `bin/doctor` point to
  `docs/foundation/knowledge-search.md#existing-hooks` instead of the section
  that moved out of `docs/development-workflow.md` in 2.0.0.
- The managed `AGENTS.md` block restores the 1.x rule to keep accepted
  decisions separate from proposals, preserve unrelated changes, and keep
  secrets and generated caches out of Git.
- The check schedule states that a sync changing only managed files needs
  `bin/check`; the release's CI already tested that code.

### Manual follow-up

- Projects that override `bin/_knowledge.py` apply the same message change.
- Remove project copies of the restored `AGENTS.md` rule outside the block.
- Optionally remove `.gitignore` lines outside the block that duplicate block
  lines; the only negation they share, `!.env.example`, keeps its order inside
  the block.

## 2.0.0 — 2026-10-09

### Synced

- `bin/check` verifies managed files and blocks against the hashes in
  `.project-starter.json` in every mode. `--full` runs an executable
  `bin/check-application` after the foundation checks, instead of the copied
  foundation behavior tests.
- Shared policy moved into managed, condensed `docs/foundation/` pages:
  engineering policy, knowledge search, and task tracking.
- `AGENTS.md` and `.gitignore` carry managed blocks between
  `project-starter:begin` and `project-starter:end` markers.
- `bin/doctor` flags every QMD release except the exact tested version.
- Each refresh section in `.cache/qmd/index.log` starts with a timestamp and
  the QMD version.
- Task tracking installs upstream td from the `marcus/tap` Homebrew tap.
- `.project-starter.json` records only the version, source, release, managed
  hashes, and overrides.

Sync removes unchanged copies of `tests/test_knowledge.py`, because the
foundation tests now run only in Project Starter's CI, and of
`docs/task-tracking.md`, which moved to `docs/foundation/task-tracking.md`.
Changed copies are conflicts to review.

### Manual follow-up

- Move application checks from `bin/check` wrappers or `bin/_checks.py` into
  an executable `bin/check-application`.
- In `.config/knowledge.json`, add the `foundation` collection for
  `docs/foundation` and ignore `foundation/**` in the `docs` collection.
- Link `foundation/README.md` from `docs/README.md`, and repoint links that
  used `docs/task-tracking.md` or policy anchors in
  `docs/development-workflow.md`.
- Reduce `docs/development-workflow.md` to project-specific commands, and
  remove `AGENTS.md` rules that the managed block now covers.
- Record intentional managed-file changes as overrides with reasons, and
  merge 2.0 into those files by hand. A project that overrides a helper keeps
  its own tests for that variant.
- Preserve project-specific regression tests from the removed
  `tests/test_knowledge.py`, such as application-check wiring, as tests of
  `bin/check-application`.
- Update project tests that build fixtures from `.config/knowledge.json` or
  `.project-starter.json`: they now need `docs/foundation/` and the managed
  files those manifests reference. Repoint in-page anchors to moved sections;
  `bin/check` reports them.

### Verified

QMD 2.8.3 with node-llama-cpp 3.22.1 (strict real-QMD smoke on an Apple M5
Pro with macOS 27.0.1), td 0.66.0, and CI on Ubuntu 24.04 and macOS 15.

## 1.0.0 — 2026-09-04

Initial release. Adopters copied files by hand and recorded the starter
revision in `source_ref`; later partial updates added `knowledge_source_ref`
and `task_tracking_source_ref`. `bin/sync` uses those revisions to migrate.

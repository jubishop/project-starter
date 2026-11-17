"""Exercise bin/sync and adopter hash checks in disposable repositories."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(repo):
    return {p: p.read_bytes() for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}


class SyncTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="project starter sync ")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, PYTHONDONTWRITEBYTECODE="1",
                        GIT_AUTHOR_NAME="Sync test", GIT_AUTHOR_EMAIL="test@example.invalid",
                        GIT_COMMITTER_NAME="Sync test", GIT_COMMITTER_EMAIL="test@example.invalid")
        # A fake GitHub CLI keeps every test off the network: it answers `gh api repos/<owner>/<name>` from
        # self.repositories and fails any other call, as gh does for a repository it cannot read.
        fake = self.base / "fake bin"
        fake.mkdir()
        self.repositories = self.base / "repositories.json"
        self.repositories.write_text("{}")
        self.gh_calls = self.base / "gh-calls.jsonl"
        gh = fake / "gh"
        gh.write_text(f"#!{sys.executable}\n"
                      "import json,sys\n"
                      f"with open({str(self.gh_calls)!r}, 'a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')\n"
                      f"repositories = json.load(open({str(self.repositories)!r}))\n"
                      "path = sys.argv[2] if sys.argv[1:2] == ['api'] and len(sys.argv) == 3 else None\n"
                      "if path not in repositories:\n"
                      " sys.exit('gh: Not Found (HTTP 404)')\n"
                      "print(json.dumps(repositories[path]))\n")
        gh.chmod(0o755)
        self.env["PATH"] = str(fake) + os.pathsep + self.env["PATH"]

    def run_command(self, *args, cwd, check=True, input=None):
        result = subprocess.run(args, cwd=cwd, env=self.env, text=True, capture_output=True, timeout=60, input=input)
        if check:
            self.assertEqual(result.returncode, 0, (args, result.stdout, result.stderr))
        return result

    def target(self, name="adopter"):
        repo = self.base / name
        repo.mkdir()
        self.run_command("git", "init", "-b", "main", cwd=repo)
        self.run_command("git", "commit", "--allow-empty", "-m", "Start", cwd=repo)
        return repo

    def commit(self, repo, message="Change"):
        self.run_command("git", "add", "-A", cwd=repo)
        self.run_command("git", "commit", "-m", message, cwd=repo)

    def commits(self, repo):
        return int(self.run_command("git", "rev-list", "--count", "HEAD", cwd=repo).stdout)

    def sync(self, *args, source=ROOT, check=True):
        return self.run_command(str(source / "bin/sync"), *args, cwd=self.base, check=check)

    def source(self):
        """Copy this checkout into a disposable source repository that can be tagged."""
        source = self.base / "starter source"
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", ".cache", "__pycache__"))
        self.run_command("git", "init", "-b", "main", cwd=source)
        self.commit(source, "Release")
        self.run_command("git", "tag", "v2.0.0", cwd=source)
        return source

    def release(self, source, tag, edits):
        for relative, text in edits.items():
            path = source / "starter" / relative
            path.write_text(path.read_text() + text)
        self.commit(source, tag)
        self.run_command("git", "tag", tag, cwd=source)

    def check_documents(self, repo, check=True):
        return self.run_command("bin/check", "--documents-only", cwd=repo, check=check)

    def manifest(self, repo):
        return json.loads((repo / ".project-starter.json").read_text())

    def test_init_copies_bundle_records_hashes_and_never_commits(self):
        repo = self.target()
        self.sync("--init", "--ref", "WORKTREE", str(repo))
        self.assertEqual(self.commits(repo), 1)
        bundle = [p.relative_to(ROOT / "starter") for p in (ROOT / "starter").rglob("*")
                  if p.is_file() and "__pycache__" not in p.parts]
        for relative in bundle:
            self.assertTrue((repo / relative).is_file(), relative)
            self.assertEqual(os.access(repo / relative, os.X_OK), os.access(ROOT / "starter" / relative, os.X_OK), relative)
        manifest = json.loads((repo / ".project-starter.json").read_text())
        template = json.loads((ROOT / "starter/.project-starter.json").read_text())
        self.assertEqual(manifest["version"], template["version"])
        self.assertEqual(manifest["managed"]["bin/_checks.py"], digest(repo / "bin/_checks.py"))
        self.assertNotIn("README.md", manifest["managed"])
        self.assertEqual(set(manifest["blocks"]), {"AGENTS.md", ".gitignore"})
        self.assertEqual(manifest["overrides"], {})
        self.assertIn("run: bin/check --full\n", (repo / ".github/workflows/check.yml").read_text())
        self.check_documents(repo)
        result = self.sync("--init", "--ref", "WORKTREE", str(repo), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already", result.stderr)

    def test_check_enforces_managed_hashes_blocks_and_overrides(self):
        repo = self.target()
        self.sync("--init", "--ref", "WORKTREE", str(repo))
        agents = repo / "AGENTS.md"
        agents.write_text(agents.read_text() + "\nProject rule outside the managed block.\n")
        self.check_documents(repo)
        helper = repo / "bin/_knowledge.py"
        helper.write_text(helper.read_text() + "# local change\n")
        result = self.check_documents(repo, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("bin/_knowledge.py", result.stderr)
        manifest_path = repo / ".project-starter.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["overrides"] = {"bin/_knowledge.py": ""}
        manifest_path.write_text(json.dumps(manifest))
        self.assertIn("reason", self.check_documents(repo, check=False).stderr)
        manifest["overrides"] = {"bin/_knowledge.py": "Local diagnostics"}
        manifest_path.write_text(json.dumps(manifest))
        self.check_documents(repo)
        text = agents.read_text()
        start = text.index("project-starter:begin")
        agents.write_text(text[:start] + text[start:].replace("\n", "\nEdited inside the block.\n", 1))
        self.assertIn("AGENTS.md", self.check_documents(repo, check=False).stderr)
        agents.write_text(text)
        (repo / "bin/doctor").unlink()
        self.assertIn("bin/doctor", self.check_documents(repo, check=False).stderr)

    def test_sync_updates_releases_and_refuses_conflicts_without_writing(self):
        source = self.source()
        repo = self.target()
        self.sync("--init", "--ref", "v2.0.0", str(repo), source=source)
        readme = repo / "README.md"
        readme.write_text("# Adopter\n\nProject-owned introduction.\n")
        agents = repo / "AGENTS.md"
        agents.write_text(agents.read_text() + "\nProject rule.\n")
        self.commit(repo, "Adopt")
        template = source / "starter/AGENTS.md"
        text = template.read_text()
        marker = text.index("\n", text.index("project-starter:begin"))
        template.write_text(text[:marker] + "\nNew managed rule." + text[marker:])
        self.release(source, "v2.0.1", {"bin/setup": "# release note\n", "bin/doctor": "# upstream change\n",
                                        "README.md": "\nUpstream template change.\n"})
        old_setup = (repo / "bin/setup").read_bytes()
        doctor = repo / "bin/doctor"
        doctor.write_text(doctor.read_text() + "# adopter change\n")
        self.commit(repo, "Local doctor")
        before = {p: p.read_bytes() for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}

        planned = self.sync("--dry-run", str(repo), source=source, check=False)
        self.assertIn("bin/doctor", planned.stdout + planned.stderr)
        conflict = self.sync(str(repo), source=source, check=False)
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("conflict", conflict.stderr.lower())
        self.assertIn("bin/doctor", conflict.stderr)
        self.assertEqual(before, {p: p.read_bytes() for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts})

        manifest_path = repo / ".project-starter.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["overrides"]["bin/doctor"] = "Adopter diagnostics"
        manifest_path.write_text(json.dumps(manifest))
        dirty = self.sync(str(repo), source=source, check=False)
        self.assertNotEqual(dirty.returncode, 0)
        self.assertIn("uncommitted", dirty.stderr)
        self.commit(repo, "Declare override")
        result = self.sync(str(repo), source=source)
        self.assertIn("bin/doctor is overridden (Adopter diagnostics); upstream changed since v2.0.0", result.stdout)
        self.assertIn("diff v2.0.0 v2.0.1 -- starter/bin/doctor", result.stdout)
        self.assertNotEqual((repo / "bin/setup").read_bytes(), old_setup)
        self.assertTrue((repo / "bin/doctor").read_text().endswith("# adopter change\n"))
        self.assertEqual(readme.read_text(), "# Adopter\n\nProject-owned introduction.\n")
        self.assertIn("New managed rule.", agents.read_text())
        self.assertTrue(agents.read_text().endswith("\nProject rule.\n"))
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest["ref"], "v2.0.1")
        self.assertEqual(manifest["overrides"], {"bin/doctor": "Adopter diagnostics"})
        self.check_documents(repo)

        self.commit(repo, "Sync")
        del manifest["overrides"]["bin/doctor"]
        manifest_path.write_text(json.dumps(manifest))
        self.commit(repo, "Drop override")
        self.assertNotEqual(self.sync(str(repo), source=source, check=False).returncode, 0)
        self.sync("--force", str(repo), source=source)
        self.assertEqual((repo / "bin/doctor").read_bytes(), (source / "starter/bin/doctor").read_bytes())
        self.assertEqual(self.commits(repo), 6)

    def test_releases_that_add_or_drop_a_starter_file_never_overwrite_project_work(self):
        source = self.source()
        repo = self.target()
        self.sync("--init", str(repo), source=source)
        own = repo / "bin/example"
        own.write_text("# The project's own example\n")
        self.commit(repo, "Adopt beside the project's own example")
        tool = source / "starter/bin/example"
        tool.write_text("#!/bin/sh\necho example\n")
        tool.chmod(0o755)
        self.commit(source, "Add the example")
        self.run_command("git", "tag", "v2.1.0", cwd=source)

        # A new starter file whose path holds a file sync does not manage conflicts until the project moves it.
        before = snapshot(repo)
        conflict = self.sync(str(repo), source=source, check=False)
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("bin/example: exists but is not managed", conflict.stderr)
        self.assertEqual(snapshot(repo), before)
        own.unlink()
        self.commit(repo, "Remove the project's own example")
        self.sync(str(repo), source=source)
        self.assertEqual(own.read_bytes(), tool.read_bytes())
        self.assertEqual(self.manifest(repo)["managed"]["bin/example"], digest(own))
        self.commit(repo, "Sync")

        # A release that drops a starter file refuses to remove a changed copy, then removes the unchanged one.
        tool.unlink()
        self.commit(source, "Drop the example")
        self.run_command("git", "tag", "v2.2.0", cwd=source)
        original = own.read_bytes()
        own.write_text(own.read_text() + "# local change\n")
        self.commit(repo, "Local change")
        before = snapshot(repo)
        refused = self.sync(str(repo), source=source, check=False)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("bin/example: no longer part of the starter but has local changes", refused.stderr)
        self.assertEqual(snapshot(repo), before)
        own.write_bytes(original)
        self.commit(repo, "Restore")
        result = self.sync(str(repo), source=source)
        self.assertIn("removed: bin/example", result.stdout)
        self.assertFalse(own.exists())
        self.assertNotIn("bin/example", self.manifest(repo)["managed"])

    def test_sync_keeps_validates_and_prints_sync_commit_trailers(self):
        repo = self.target()
        self.sync("--init", "--ref", "WORKTREE", str(repo))
        self.commit(repo, "Adopt")
        plain = self.sync("--ref", "WORKTREE", str(repo))
        self.assertNotIn("trailer", plain.stdout)
        self.assertNotIn("syncCommitTrailers", self.manifest(repo))

        trailers = {"Screenr-Deploy": "skip",
                    "Screenr-Deploy-Reason": "Project Starter sync with no manual follow-up; nothing it changes runs in production."}
        manifest = self.manifest(repo)
        manifest["syncCommitTrailers"] = trailers
        (repo / ".project-starter.json").write_text(json.dumps(manifest))
        self.commit(repo, "Record sync commit trailers")
        for args in (("--dry-run",), ()):
            with self.subTest(args=args):
                result = self.sync("--ref", "WORKTREE", *args, str(repo))
                self.assertEqual(self.manifest(repo)["syncCommitTrailers"], trailers)
                # The closing advice ends with the trailer lines, unindented so Git reads them as written.
                lines = result.stdout.splitlines()
                self.assertIn("docs/releases.md#sync-commit-trailers", lines[-3])
                self.assertEqual(lines[-2:], [name + ": " + value for name, value in trailers.items()])
                message = "Sync Project Starter\n\nThe manifest records the release.\n\n" + "\n".join(lines[-2:]) + "\n"
                parsed = self.run_command("git", "interpret-trailers", "--parse", cwd=repo, input=message).stdout
                self.assertEqual(parsed, "\n".join(lines[-2:]) + "\n")

        for invalid in (["Screenr-Deploy: skip"], {"Bad name": "skip"}, {"Deploy": "two\nlines"}, {"Deploy": ""},
                        {"Deploy": " padded"}, {"Deploy": 1}):
            with self.subTest(invalid=invalid):
                manifest["syncCommitTrailers"] = invalid
                (repo / ".project-starter.json").write_text(json.dumps(manifest))
                self.commit(repo, "Invalid trailers")
                before = snapshot(repo)
                for args in (("--dry-run",), ()):
                    result = self.sync("--ref", "WORKTREE", *args, str(repo), check=False)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(".project-starter.json: syncCommitTrailers must map trailer names", result.stderr)
                    self.assertEqual(snapshot(repo), before)

    def test_closing_advice_gives_adoption_checks_after_init_and_the_sync_only_path_after_an_update(self):
        def references(output):
            """Return each page#anchor the advice names, after checking that its heading exists here."""
            found = re.findall(r"([\w./-]+\.md)#([\w-]+)", output)
            for page, anchor in found:
                headings = re.findall(r"^#+ (.+)$", (ROOT / page).read_text(), re.M)
                self.assertIn(anchor, {re.sub(r"[^\w -]", "", h.lower()).replace(" ", "-") for h in headings}, page)
            return {page + "#" + anchor for page, anchor in found}

        repo = self.target()
        adopted = self.sync("--init", "--ref", "WORKTREE", str(repo)).stdout
        self.assertEqual(references(adopted), {"GUIDE.md#adopt-a-repository"})
        for command in ("bin/setup", "bin/check --full", "bin/doctor"):
            self.assertIn(command, adopted)
        self.assertNotIn("[skip ci]", adopted)

        self.commit(repo, "Adopt")
        updated = self.sync("--ref", "WORKTREE", str(repo)).stdout
        self.assertEqual(references(updated), {"docs/releases.md#sync-only-releases"})
        for text in ("manual follow-up", "[skip ci]", "bin/check --full", "bin/check --documents-only"):
            self.assertIn(text, updated)
        self.assertNotIn("bin/doctor", updated)

    def test_sync_warns_when_a_public_github_adopter_lacks_secret_scanning(self):
        def repository(visibility, scanning, protection):
            return {"visibility": visibility, "security_and_analysis": {
                "secret_scanning": {"status": scanning}, "secret_scanning_push_protection": {"status": protection}}}
        self.repositories.write_text(json.dumps({
            "repos/example-owner/exposed": repository("public", "disabled", "disabled"),
            "repos/example-owner/partial": repository("public", "enabled", "disabled"),
            "repos/example-owner/protected": repository("public", "enabled", "enabled"),
            "repos/example-owner/private": repository("private", "disabled", "disabled"),
            # GitHub omits the settings for a viewer without admin access.
            "repos/example-owner/unreadable": {"visibility": "public"},
        }))
        remotes = {
            "exposed": "git@github.com:example-owner/exposed.git",
            "partial": "https://github.com/example-owner/partial",
            "protected": "ssh://git@github.com/example-owner/protected.git",
            "private": "git@github.com:example-owner/private.git",
            "unreadable": "git@github.com:example-owner/unreadable.git",
            "missing": "git@github.com:example-owner/missing.git",
            "elsewhere": "git@gitlab.com:example-owner/elsewhere.git",
            "local": None,
        }
        outputs = {}
        for name, remote in remotes.items():
            repo = self.target(name)
            if remote:
                self.run_command("git", "remote", "add", "origin", remote, cwd=repo)
            outputs[name] = self.sync("--init", "--dry-run", "--ref", "WORKTREE", str(repo)).stdout
        enable = ("gh api -X PATCH repos/example-owner/exposed"
                  " -f 'security_and_analysis[secret_scanning][status]=enabled'"
                  " -f 'security_and_analysis[secret_scanning_push_protection][status]=enabled'")
        self.assertIn("warning: example-owner/exposed is a public GitHub repository with secret scanning and push"
                      " protection disabled; enable them with: " + enable + "\n", outputs["exposed"])
        self.assertIn("warning: example-owner/partial is a public GitHub repository with push protection disabled;",
                      outputs["partial"])
        self.assertIn("note: could not check secret scanning on example-owner/unreadable: ", outputs["unreadable"])
        self.assertIn("note: could not check secret scanning on example-owner/missing: gh: Not Found (HTTP 404)\n",
                      outputs["missing"])
        for name in ("protected", "private", "elsewhere", "local"):
            self.assertNotIn("secret scanning", outputs[name], name)
        calls = [json.loads(line) for line in self.gh_calls.read_text().splitlines()]
        self.assertEqual(sorted(calls), sorted(["api", "repos/example-owner/" + name] for name in
                                               ("exposed", "partial", "protected", "private", "unreadable", "missing")))
        # A sync that writes warns too, and the warning never fails it.
        result = self.sync("--init", "--ref", "WORKTREE", str(self.base / "exposed"))
        self.assertIn("enable them with: " + enable + "\n", result.stdout)
        self.assertTrue((self.base / "exposed/.project-starter.json").is_file())

    def test_status_reports_versions_overrides_and_drift(self):
        fleet = self.base / "projects"
        fleet.mkdir()
        for name in ("current", "drifted", "overridden"):
            repo = fleet / name
            repo.mkdir()
            self.run_command("git", "init", "-b", "main", cwd=repo)
            self.run_command("git", "commit", "--allow-empty", "-m", "Start", cwd=repo)
            self.sync("--init", "--ref", "WORKTREE", str(repo))
        doctor = fleet / "drifted/bin/doctor"
        doctor.write_text(doctor.read_text() + "# drift\n")
        manifest_path = fleet / "overridden/.project-starter.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["overrides"] = {"bin/doctor": "Local diagnostics"}
        manifest_path.write_text(json.dumps(manifest))
        (fleet / "unrelated").mkdir()
        status = self.sync("--status", "--root", str(fleet), "--ref", "WORKTREE")
        lines = {line.split()[0]: line for line in status.stdout.splitlines() if line.strip()}
        self.assertNotIn("unrelated", lines)
        self.assertIn("drift 1", lines["drifted"])
        self.assertIn("drift 0", lines["current"])
        self.assertIn("overrides 1", lines["overridden"])


if __name__ == "__main__":
    unittest.main()

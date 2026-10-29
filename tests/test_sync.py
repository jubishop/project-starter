"""Exercise bin/sync and adopter hash checks in disposable repositories."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FEATURE = ROOT / "features/memory-audit"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feature_files():
    """The adopter paths the memory audit feature installs."""
    return sorted(p.relative_to(FEATURE).as_posix() for p in FEATURE.rglob("*")
                  if p.is_file() and p.name != "feature.json" and "__pycache__" not in p.parts)


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

    def run_command(self, *args, cwd, check=True):
        result = subprocess.run(args, cwd=cwd, env=self.env, text=True, capture_output=True, timeout=60)
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

    def assert_feature_installed(self, repo):
        manifest = self.manifest(repo)
        self.assertEqual(manifest["features"], ["memory-audit"])
        for relative in feature_files():
            self.assertEqual((repo / relative).read_bytes(), (FEATURE / relative).read_bytes(), relative)
            self.assertEqual(os.access(repo / relative, os.X_OK), os.access(FEATURE / relative, os.X_OK), relative)
            self.assertEqual(manifest["managed"][relative], digest(repo / relative), relative)
        self.assertFalse((repo / "feature.json").exists())
        # The foundation index lists the feature's page, so index coverage passes.
        index = repo / "docs/foundation/README.md"
        self.assertIn("](memory-audit.md)", index.read_text())
        self.assertEqual(manifest["managed"]["docs/foundation/README.md"], digest(index))
        self.check_documents(repo)

    def assert_feature_absent(self, repo):
        manifest = self.manifest(repo)
        self.assertNotIn("features", manifest)
        for relative in feature_files():
            self.assertFalse((repo / relative).exists(), relative)
            self.assertNotIn(relative, manifest["managed"])
        self.assertEqual((repo / "docs/foundation/README.md").read_bytes(),
                         (ROOT / "starter/docs/foundation/README.md").read_bytes())

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
        self.release(source, "v2.0.1", {"bin/setup": "# release note\n", "README.md": "\nUpstream template change.\n"})
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
        self.assertIn("bin/doctor", result.stdout)
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

    def test_legacy_adopter_migrates_from_recorded_source_refs(self):
        source = self.base / "starter source"
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", ".cache", "__pycache__"))
        legacy_files = {"bin/doctor": "# legacy doctor\n", "tests/test_knowledge.py": "# legacy tests\n",
                        "docs/obsolete-guide.md": "---\nstatus: current\n---\n\n# Obsolete guide\n",
                        ".envrc": "export LEGACY_ENVIRONMENT=1\n"}
        current = {relative: (source / "starter" / relative).read_bytes()
                   for relative in legacy_files if (source / "starter" / relative).is_file()}
        for relative, text in legacy_files.items():
            path = source / "starter" / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self.run_command("git", "init", "-b", "main", cwd=source)
        self.commit(source, "Legacy")
        legacy_ref = self.run_command("git", "rev-parse", "HEAD", cwd=source).stdout.strip()
        repo = self.base / "legacy adopter"
        shutil.copytree(source / "starter", repo)
        (repo / "AGENTS.md").write_text("# Project instructions\n\nLegacy project rule.\n")
        (repo / ".gitignore").write_text("node_modules/\n")
        (repo / ".project-starter.json").write_text(json.dumps(
            {"version": "1.0.0", "source": "https://example.invalid/starter", "source_ref": legacy_ref,
             "tested_qmd": "2.8.3"}))
        checks = repo / "bin/_checks.py"
        checks.write_text(checks.read_text() + "# adapted application checks\n")
        self.run_command("git", "init", "-b", "main", cwd=repo)
        self.commit(repo, "Legacy adoption")
        for relative in legacy_files:
            path = source / "starter" / relative
            if relative in current:
                path.write_bytes(current[relative])
            else:
                path.unlink()
        self.commit(source, "Current")
        self.run_command("git", "tag", "v2.0.0", cwd=source)

        conflict = self.sync(str(repo), source=source, check=False)
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("bin/_checks.py", conflict.stderr)
        self.assertNotIn("bin/doctor", conflict.stderr)
        result = self.sync("--force", str(repo), source=source)
        self.assertEqual((repo / "bin/doctor").read_bytes(), (source / "starter/bin/doctor").read_bytes())
        self.assertEqual(checks.read_bytes(), (source / "starter/bin/_checks.py").read_bytes())
        self.assertFalse((repo / "tests/test_knowledge.py").exists())
        self.assertFalse((repo / "docs/obsolete-guide.md").exists())
        # 1.x shipped .envrc; it is project configuration, never removed by sync.
        self.assertEqual((repo / ".envrc").read_text(), "export LEGACY_ENVIRONMENT=1\n")
        agents = (repo / "AGENTS.md").read_text()
        self.assertIn("Legacy project rule.", agents)
        self.assertLess(agents.index("project-starter:begin"), agents.index("Legacy project rule."))
        self.assertIn("AGENTS.md", result.stdout)
        gitignore = (repo / ".gitignore").read_text()
        self.assertTrue(gitignore.startswith("node_modules/\n"))
        self.assertIn("project-starter:begin", gitignore)
        manifest = json.loads((repo / ".project-starter.json").read_text())
        self.assertEqual(set(manifest), {"version", "source", "ref", "managed", "blocks", "overrides"})
        self.assertEqual(manifest["ref"], "v2.0.0")

    def test_init_can_enable_a_feature(self):
        repo = self.target()
        self.sync("--init", "--ref", "WORKTREE", "--enable", "memory-audit", str(repo))
        self.assertEqual(self.commits(repo), 1)
        self.assert_feature_installed(repo)

    def test_an_adopter_enables_keeps_and_disables_a_feature(self):
        repo = self.target()
        self.sync("--init", "--ref", "WORKTREE", str(repo))
        self.assert_feature_absent(repo)
        self.commit(repo, "Adopt")
        self.sync("--ref", "WORKTREE", "--enable", "memory-audit", str(repo))
        self.assert_feature_installed(repo)
        self.commit(repo, "Enable")
        before = snapshot(repo)
        self.sync("--ref", "WORKTREE", str(repo))
        self.assertEqual(snapshot(repo), before)

        audit = repo / "bin/_memory_audit.py"
        original = audit.read_bytes()
        audit.write_text(audit.read_text() + "# local change\n")
        self.assertIn("bin/_memory_audit.py", self.check_documents(repo, check=False).stderr)
        self.commit(repo, "Local change")
        refused = self.sync("--ref", "WORKTREE", "--disable", "memory-audit", str(repo), check=False)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("bin/_memory_audit.py", refused.stderr)
        self.assertTrue(audit.read_text().endswith("# local change\n"))
        audit.write_bytes(original)
        self.commit(repo, "Restore")
        self.sync("--ref", "WORKTREE", "--disable", "memory-audit", str(repo))
        self.assert_feature_absent(repo)
        self.check_documents(repo)

    def test_a_project_copy_of_a_feature_file_conflicts_until_removed(self):
        repo = self.target()
        self.sync("--init", "--ref", "WORKTREE", str(repo))
        own = repo / "bin/_memory_audit.py"
        own.write_text("# The project's own audit\n")
        self.commit(repo, "Own audit")
        before = snapshot(repo)
        conflict = self.sync("--ref", "WORKTREE", "--enable", "memory-audit", str(repo), check=False)
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("bin/_memory_audit.py", conflict.stderr)
        self.assertIn("not managed", conflict.stderr)
        self.assertEqual(snapshot(repo), before)
        own.unlink()
        self.commit(repo, "Remove own audit")
        self.sync("--ref", "WORKTREE", "--enable", "memory-audit", str(repo))
        self.assert_feature_installed(repo)

    def test_unknown_or_contradictory_features_are_refused(self):
        repo = self.target()
        for args, message in ((("--enable", "memory-audti"), "memory-audit"),
                              (("--disable", "memory-audti"), "memory-audit"),
                              (("--enable", "memory-audit", "--disable", "memory-audit"), "both")):
            with self.subTest(args=args):
                result = self.sync("--init", "--ref", "WORKTREE", *args, str(repo), check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertFalse((repo / ".project-starter.json").exists())
        self.assertNotEqual(self.sync("--status", "--enable", "memory-audit", check=False).returncode, 0)

    def test_feature_changes_reach_only_the_adopters_that_enable_it(self):
        source = self.base / "starter source"
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", ".cache", "__pycache__", "features"))
        self.run_command("git", "init", "-b", "main", cwd=source)
        self.commit(source, "Release without features")
        self.run_command("git", "tag", "v2.0.0", cwd=source)
        plain, featured = self.target("plain"), self.target("featured")
        for repo in (plain, featured):
            self.sync("--init", str(repo), source=source)
            self.commit(repo, "Adopt")
        early = self.sync("--enable", "memory-audit", str(featured), source=source, check=False)
        self.assertNotEqual(early.returncode, 0)
        self.assertIn("memory-audit", early.stderr)

        shutil.copytree(FEATURE, source / "features/memory-audit", ignore=shutil.ignore_patterns("__pycache__"))
        with (source / "features/memory-audit/bin/_memory_audit.py").open("a") as stream:
            stream.write("# release note\n")
        template = source / "starter/.project-starter.json"
        template.write_text(template.read_text().replace(json.loads(template.read_text())["version"], "2.1.0"))
        self.commit(source, "Release the feature")
        self.run_command("git", "tag", "v2.1.0", cwd=source)

        before = self.manifest(plain)
        self.sync(str(plain), source=source)
        changed = self.run_command("git", "status", "--porcelain", cwd=plain).stdout.splitlines()
        self.assertEqual(changed, [" M .project-starter.json"])
        after = self.manifest(plain)
        self.assertEqual(set(after), {"version", "source", "ref", "managed", "blocks", "overrides"})
        self.assertEqual((after["version"], after["ref"]), ("2.1.0", "v2.1.0"))
        self.assertEqual(after["managed"], before["managed"])
        self.sync("--enable", "memory-audit", str(featured), source=source)
        self.assertTrue((featured / "bin/_memory_audit.py").read_text().endswith("# release note\n"))
        self.assertEqual(self.manifest(featured)["features"], ["memory-audit"])
        self.check_documents(featured)

        # An overridden feature file keeps its local change and reports the upstream one.
        with (featured / "bin/_memory_audit.py").open("a") as stream:
            stream.write("# local change\n")
        manifest = self.manifest(featured)
        manifest["overrides"]["bin/_memory_audit.py"] = "Local audit experiment"
        (featured / ".project-starter.json").write_text(json.dumps(manifest))
        self.commit(featured, "Override the audit")
        with (source / "features/memory-audit/bin/_memory_audit.py").open("a") as stream:
            stream.write("# second release note\n")
        self.commit(source, "Change the feature again")
        self.run_command("git", "tag", "v2.2.0", cwd=source)
        result = self.sync(str(featured), source=source)
        self.assertIn("upstream changed since v2.1.0", result.stdout)
        self.assertIn("-- features/memory-audit/bin/_memory_audit.py", result.stdout)
        self.assertTrue((featured / "bin/_memory_audit.py").read_text().endswith("# local change\n"))

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

    def test_status_reports_versions_overrides_drift_and_legacy(self):
        fleet = self.base / "projects"
        fleet.mkdir()
        for name in ("current", "drifted", "overridden", "featured"):
            repo = fleet / name
            repo.mkdir()
            self.run_command("git", "init", "-b", "main", cwd=repo)
            self.run_command("git", "commit", "--allow-empty", "-m", "Start", cwd=repo)
            features = ("--enable", "memory-audit") if name == "featured" else ()
            self.sync("--init", "--ref", "WORKTREE", *features, str(repo))
        doctor = fleet / "drifted/bin/doctor"
        doctor.write_text(doctor.read_text() + "# drift\n")
        audit = fleet / "featured/bin/memory-audit"
        audit.write_text(audit.read_text() + "# drift\n")
        manifest_path = fleet / "overridden/.project-starter.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["overrides"] = {"bin/doctor": "Local diagnostics"}
        manifest_path.write_text(json.dumps(manifest))
        (fleet / "legacy").mkdir()
        (fleet / "legacy/.project-starter.json").write_text(json.dumps({"version": "1.0.0"}))
        (fleet / "unrelated").mkdir()
        lines = {line.split()[0]: line for line in self.sync("--status", "--root", str(fleet), "--ref", "WORKTREE").stdout.splitlines()
                 if line.strip()}
        self.assertNotIn("unrelated", lines)
        self.assertIn("legacy", lines["legacy"].split(maxsplit=1)[1])
        self.assertIn("drift 1", lines["drifted"])
        self.assertIn("drift 0", lines["current"])
        self.assertIn("overrides 1", lines["overridden"])
        self.assertIn("drift 1", lines["featured"])
        self.assertIn("features memory-audit", lines["featured"])
        self.assertNotIn("features", lines["current"])


if __name__ == "__main__":
    unittest.main()

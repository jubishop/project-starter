"""Exercise bin/sync and adopter hash checks in disposable repositories."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SyncTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="project starter sync ")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, PYTHONDONTWRITEBYTECODE="1",
                        GIT_AUTHOR_NAME="Sync test", GIT_AUTHOR_EMAIL="test@example.invalid",
                        GIT_COMMITTER_NAME="Sync test", GIT_COMMITTER_EMAIL="test@example.invalid")

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
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", ".cache", ".todos", "__pycache__"))
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
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", ".cache", ".todos", "__pycache__"))
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

    def test_status_reports_versions_overrides_drift_and_legacy(self):
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


if __name__ == "__main__":
    unittest.main()

"""Exercise adopter selection and failure safety through the smoke CLI, and when bin/check runs it."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SmokeTests(unittest.TestCase):
    def test_maintainer_check_runs_it_off_github_actions_when_the_knowledge_tools_change(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo = base / "maintainer checkout"
            (repo / "bin").mkdir(parents=True)
            for name in ("bin/check", "bin/smoke-qmd"):
                shutil.copy2(ROOT / name, repo / name)
            shutil.copytree(ROOT / "starter", repo / "starter", ignore=shutil.ignore_patterns("__pycache__", ".cache"))
            (repo / "docs").mkdir()
            (repo / "docs/README.md").write_text("# Design\n")
            (repo / "tests").mkdir()
            (repo / "tests/test_fixture.py").write_text("import unittest\n\n\nclass Fixture(unittest.TestCase):\n"
                                                       "    def test_passes(self):\n        pass\n")
            tools = base / "tools"
            tools.mkdir()
            for tool in ("shellcheck", "actionlint"):
                (tools / tool).write_text("#!/bin/sh\nexit 0\n")
                (tools / tool).chmod(0o755)
            # The home has no QMD models, so a smoke check that runs fails at once, naming them.
            env = {key: value for key, value in os.environ.items() if not key.startswith(("GIT_", "GITHUB_"))}
            env |= {"HOME": str(base / "home"), "PATH": str(tools) + os.pathsep + env["PATH"],
                    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}

            def git(*args):
                subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", *args],
                               cwd=repo, env=env, check=True, capture_output=True)

            def check(**extra):
                return subprocess.run([str(repo / "bin/check")], cwd=repo, env=env | extra, text=True,
                                      capture_output=True, timeout=60)

            git("init", "-b", "main")
            git("add", ".")
            git("commit", "-m", "Published")
            git("update-ref", "refs/remotes/origin/HEAD", "HEAD")
            with (repo / "starter/docs/README.md").open("a") as stream:
                stream.write("\nAn unrelated change.\n")
            git("commit", "-am", "Change a page")
            unrelated = check()
            self.assertEqual(unrelated.returncode, 0, unrelated.stdout + unrelated.stderr)
            hook = repo / "starter/bin/hooks/pre-commit"
            hook.write_text("#!/bin/sh\n")
            uncommitted = check()
            self.assertNotEqual(uncommitted.returncode, 0)
            self.assertIn("~/.cache/qmd/models must contain", uncommitted.stderr)
            hook.unlink()
            with (repo / "starter/bin/_knowledge.py").open("a") as stream:
                stream.write("# A change to the knowledge tools.\n")
            git("commit", "-am", "Change the knowledge tools")
            committed = check()
            self.assertNotEqual(committed.returncode, 0)
            self.assertIn("~/.cache/qmd/models must contain", committed.stderr)
            hosted = check(GITHUB_ACTIONS="true")
            self.assertEqual(hosted.returncode, 0, hosted.stdout + hosted.stderr)

    def test_setup_timeout_retains_worker_diagnostics(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo = base / "timeout-adopter"
            shutil.copytree(ROOT / "starter", repo)
            subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
            (repo / "bin/setup").write_text("#!/bin/sh\nmkdir -p .cache/qmd\nprintf 'model download stalled\\n' > .cache/qmd/index.log\nexec sleep 10\n")
            qmd = base / "qmd"
            qmd.write_text("#!/bin/sh\necho 'qmd 2.8.3'\n")
            qmd.chmod(0o755)
            result = subprocess.run([str(ROOT / "bin/smoke-qmd"), "--project", str(repo),
                                     "--qmd", str(qmd), "--download-models", "--command-timeout", "0.5"],
                                    env=os.environ | {"HOME": str(base / "home")},
                                    text=True, capture_output=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("model download stalled", result.stderr)
            report = json.loads((ROOT / ".cache/validation/smoke-qmd-timeout-adopter.json").read_text())
            self.assertEqual(report["status"], "failed")
            self.assertIn("model download stalled", report["error"])

    def test_strict_mode_rejects_warnings_from_a_successful_command(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo = base / "adopter"
            shutil.copytree(ROOT / "starter", repo)
            subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
            # Color codes around a diagnostic word still leave it a word.
            (repo / "bin/setup").write_text("#!/bin/sh\nprintf '\\033[33mWarning\\033[0m: GPU fallback\\n' >&2\nexit 0\n")
            models = base / "home/.cache/qmd/models"
            models.mkdir(parents=True)
            (models / "hf_ggml-org_embeddinggemma-300M-Q8_0.gguf").touch()
            qmd = base / "qmd"
            qmd.write_text("#!/bin/sh\necho 'qmd 2.8.3'\n")
            qmd.chmod(0o755)
            result = subprocess.run([str(ROOT / "bin/smoke-qmd"), "--project", str(repo),
                                     "--qmd", str(qmd), "--strict-diagnostics"],
                                    env=os.environ | {"HOME": str(base / "home")},
                                    text=True, capture_output=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unexpected diagnostics", result.stderr)
            self.assertIn("GPU fallback", result.stderr)

    def test_adopter_uses_current_files_and_leaves_source_untouched_on_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo = base / "adopted project"
            shutil.copytree(ROOT / "starter", repo)
            subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
            (repo / "bin/setup").write_text("#!/bin/sh\necho adopter-specific-setup-failure >&2\nexit 42\n")
            (repo / "local-readme").symlink_to("README.md")
            models = base / "home/.cache/qmd/models"
            models.mkdir(parents=True)
            (models / "hf_ggml-org_embeddinggemma-300M-Q8_0.gguf").touch()
            qmd = base / "qmd"
            qmd.write_text("#!/bin/sh\necho 'qmd 2.1.0 (fixture)'\n")
            qmd.chmod(0o755)
            before = {str(p.relative_to(repo)): p.read_bytes() for p in repo.rglob("*") if p.is_file()}
            result = subprocess.run([str(ROOT / "bin/smoke-qmd"), "--project", str(repo), "--qmd", str(qmd)],
                                    env=os.environ | {"HOME": str(base / "home")}, text=True,
                                    capture_output=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("adopter-specific-setup-failure", result.stderr)
            after = {str(p.relative_to(repo)): p.read_bytes() for p in repo.rglob("*") if p.is_file()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()

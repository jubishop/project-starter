"""Test the maintainer bin/check's command line."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CheckCommandLineTests(unittest.TestCase):
    def run_check(self, *args):
        # A copy outside any Git checkout fails and prints at once if it starts checking, and can never run this
        # suite again from inside itself.
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            (repo / "bin").mkdir()
            shutil.copy2(ROOT / "bin/check", repo / "bin/check")
            shutil.copytree(ROOT / "starter/bin", repo / "starter/bin", ignore=shutil.ignore_patterns("__pycache__"))
            env = {key: value for key, value in os.environ.items() if not key.startswith(("GIT_", "GITHUB_"))}
            return subprocess.run([str(repo / "bin/check"), *args], cwd=repo, env=env, text=True,
                                  capture_output=True, timeout=60)

    def test_help_prints_usage_without_checking(self):
        for args in (("--help",), ("-h",)):
            with self.subTest(args=args):
                result = self.run_check(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.startswith("Usage: bin/check"), result.stdout)
                self.assertIn("always runs everything", result.stdout)
                self.assertEqual(result.stderr, "")

    def test_other_arguments_fail_with_usage_without_checking(self):
        for args in (("--full",), ("--documents-only",), ("--help", "--full"), ("extra",)):
            with self.subTest(args=args):
                result = self.run_check(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr.startswith("Usage: bin/check"), result.stderr)
                self.assertEqual(result.stdout, "")

    def test_project_starters_own_skills_follow_the_frontmatter_rules(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary).resolve() / "starter checkout"
            (repo / "bin").mkdir(parents=True)
            shutil.copy2(ROOT / "bin/check", repo / "bin/check")
            shutil.copytree(ROOT / "starter", repo / "starter", ignore=shutil.ignore_patterns("__pycache__", ".cache"))
            (repo / "docs").mkdir()
            (repo / "docs/README.md").write_text("# Design\n")
            skill = repo / ".agents/skills/sync-fleet/SKILL.md"
            skill.parent.mkdir(parents=True)
            # Without ShellCheck on PATH, a run whose document checks pass stops before the tests, which it would
            # otherwise run from inside itself.
            tools = repo.parent / "tools"
            tools.mkdir()
            for name, target in (("python3", sys.executable), ("git", shutil.which("git"))):
                (tools / name).symlink_to(target)
            env = {key: value for key, value in os.environ.items() if not key.startswith(("GIT_", "GITHUB_"))}
            env.update(PATH=str(tools), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
            subprocess.run(["git", "init", "-q"], cwd=repo, env=env, check=True)
            for flag, expected in (("user_invocable: true\n", ".agents/skills/sync-fleet/SKILL.md: user_invocable is a"
                                    " spelling no runtime reads; use user-invocable\n"),
                                   ("", "Install shellcheck before running bin/check.\n")):
                with self.subTest(flag=flag):
                    skill.write_text("---\nname: sync-fleet\ndescription: Sync the fleet.\n" + flag
                                     + "disable-model-invocation: false\n---\n\n# Sync the Fleet\n")
                    result = subprocess.run([str(repo / "bin/check")], cwd=repo, env=env, text=True,
                                            capture_output=True, timeout=60)
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(result.stderr, expected)


if __name__ == "__main__":
    unittest.main()

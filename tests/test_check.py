"""Test the maintainer bin/check's command line."""
import os
from pathlib import Path
import shutil
import subprocess
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


if __name__ == "__main__":
    unittest.main()

"""Verify the optional GitHub overlay in an adopted copy of the starter."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GitHubIntegrationTests(unittest.TestCase):
    def test_workflow_links_survive_copied_document_tests(self):
        with tempfile.TemporaryDirectory(prefix="starter GitHub adoption ") as temporary:
            repo = Path(temporary) / "adopted checkout"
            shutil.copytree(ROOT / "starter", repo,
                            ignore=shutil.ignore_patterns("__pycache__", ".cache"))
            shutil.copytree(ROOT / "extras/github/.github", repo / ".github")
            # CI must retain behavior tests when the local default is fast.
            workflow = (repo / ".github/workflows/check.yml").read_text()
            self.assertIn("run: bin/check --full\n", workflow)
            for relative, link in (
                ("README.md", ".github/workflows/check.yml"),
                ("docs/development-workflow.md", "../.github/workflows/check.yml"),
            ):
                with (repo / relative).open("a") as stream:
                    stream.write(f"\n[Repository checks]({link}) run on GitHub Actions.\n")
            env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
            env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                       PYTHONDONTWRITEBYTECODE="1")

            def run(*command):
                result = subprocess.run(command, cwd=repo, env=env, text=True,
                                        capture_output=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            run("git", "init", "-b", "main")
            run("bin/check", "--documents-only")
            # Check the further copies these tests make, not just the adopted
            # docs: the inner copies also need the linked workflow.
            run(sys.executable, "-B", "tests/test_knowledge.py", "-v",
                "KnowledgeTests.test_document_schema_names_and_index_coverage",
                "KnowledgeTests.test_heading_anchors_spaces_parentheses_and_reference_links",
                "KnowledgeTests.test_unsupported_metadata_and_generated_exclusions")


if __name__ == "__main__":
    unittest.main()

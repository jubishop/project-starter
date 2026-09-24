"""Verify license links in an adopted copy of the starter."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LicenseIntegrationTests(unittest.TestCase):
    def test_license_links_survive_copied_document_tests(self):
        for project_license in (False, True):
            with self.subTest(project_license=project_license), tempfile.TemporaryDirectory(
                    prefix="starter license adoption ") as temporary:
                repo = Path(temporary) / "adopted checkout"
                shutil.copytree(ROOT / "starter", repo,
                                ignore=shutil.ignore_patterns("__pycache__", ".cache"))
                links = "\n[Starter license](LICENSE.project-starter)\n"
                if project_license:
                    (repo / "LICENSE").write_text("Project license fixture.\n")
                    links += "\n[Project license](LICENSE)\n"
                with (repo / "README.md").open("a") as stream:
                    stream.write(links)
                env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
                env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                           PYTHONDONTWRITEBYTECODE="1")

                def run(*command):
                    result = subprocess.run(command, cwd=repo, env=env, text=True,
                                            capture_output=True, timeout=60)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

                run("git", "init", "-b", "main")
                run("bin/check", "--documents-only")
                run(sys.executable, "-B", "tests/test_knowledge.py", "-v",
                    "KnowledgeTests.test_document_schema_names_and_index_coverage")


if __name__ == "__main__":
    unittest.main()

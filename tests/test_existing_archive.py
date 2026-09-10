"""Verify adoption into a project that already has archived memory."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExistingArchiveTests(unittest.TestCase):
    def test_copied_checks_accept_existing_memory_archive(self):
        with tempfile.TemporaryDirectory(prefix="starter archive adoption ") as temporary:
            repo = Path(temporary) / "adopted checkout"
            shutil.copytree(ROOT / "starter", repo,
                            ignore=shutil.ignore_patterns("__pycache__", ".cache"))
            archive = repo / "memory/archive"
            archive.mkdir(exist_ok=True)
            incident = archive / "prior-incident.md"
            content = ("---\nname: prior-incident\ndescription: A resolved incident.\n"
                       "type: project\nstatus: resolved\n---\n\n# Prior incident\n\n"
                       "Preserve the existing project history.\n")
            incident.write_text(content)
            env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
            env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                       PYTHONDONTWRITEBYTECODE="1")
            # These copied tests create further disposable repositories. They
            # must work when those copies already contain archived knowledge.
            result = subprocess.run(
                [sys.executable, "-B", "tests/test_knowledge.py", "-v",
                 "KnowledgeTests.test_collection_config_changes_and_archive_edits",
                 "KnowledgeTests.test_archived_pages_cannot_remain_in_active_indexes"],
                cwd=repo, env=env, text=True, capture_output=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(incident.read_text(), content)


if __name__ == "__main__":
    unittest.main()

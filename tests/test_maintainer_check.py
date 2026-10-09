"""Verify maintainer consistency checks that run before the test suite."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MaintainerCheckTests(unittest.TestCase):
    def test_tested_qmd_version_must_match_validation_manifest(self):
        with tempfile.TemporaryDirectory(prefix="starter maintainer check ") as temporary:
            source = Path(temporary) / "starter source"
            shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", ".cache", ".todos", "__pycache__"))
            manifest = source / "tools/qmd/package.json"
            package = json.loads(manifest.read_text())
            package["dependencies"]["@tobilu/qmd"] = "0.0.1"
            manifest.write_text(json.dumps(package))
            env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
            env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, PYTHONDONTWRITEBYTECODE="1")
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=source, env=env, check=True)
            result = subprocess.run(["bin/check"], cwd=source, env=env, text=True, capture_output=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("TESTED_QMD", result.stderr)
            self.assertIn("0.0.1", result.stderr)


if __name__ == "__main__":
    unittest.main()

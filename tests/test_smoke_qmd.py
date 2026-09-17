"""Exercise adopter selection and failure safety through the smoke CLI."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SmokeTests(unittest.TestCase):
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

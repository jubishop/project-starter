"""Exercise adopter selection and failure safety through the smoke CLI."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SmokeTests(unittest.TestCase):
    def test_cpu_mode_requires_explicit_opt_in_and_sets_backend_mode(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo = base / "cpu-adopter"
            shutil.copytree(ROOT / "starter", repo)
            subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
            (repo / "bin/setup").write_text('#!/bin/sh\necho "cpu-setting=$QMD_FORCE_CPU" >&2\nexit 42\n')
            qmd = base / "qmd"
            notice = "QMD Warning: no GPU acceleration, running on CPU (slow). Run 'qmd doctor' for device diagnostics."
            qmd.write_text("#!/bin/sh\nprintf '\\033[?25l' >&2\necho \"" + notice + "\" >&2\necho 'qmd 2.8.3'\n")
            qmd.chmod(0o755)
            command = [str(ROOT / "bin/smoke-qmd"), "--project", str(repo), "--qmd", str(qmd),
                       "--download-models", "--strict-diagnostics"]
            env = os.environ | {"HOME": str(base / "home")}
            blocked = subprocess.run(command, env=env, text=True, capture_output=True, timeout=15)
            self.assertIn("Unexpected diagnostics", blocked.stderr)
            allowed = subprocess.run([*command, "--cpu-only"], env=env, text=True, capture_output=True, timeout=15)
            self.assertNotEqual(allowed.returncode, 0)
            self.assertIn("cpu-setting=1", allowed.stderr)
            self.assertNotIn("Unexpected diagnostics", allowed.stderr)

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
            (repo / "bin/setup").write_text("#!/bin/sh\necho 'QMD Warning: GPU fallback' >&2\nexit 0\n")
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

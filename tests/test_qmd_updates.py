"""Exercise release checks through a local registry and installed package files."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.install = self.root / 'install'
        self.state = self.root / 'updates.json'
        self.versions = {'@tobilu/qmd': '2.8.3', 'node-llama-cpp': '3.21.1'}
        for name, version in self.versions.items():
            path = self.install / 'node_modules' / name / 'package.json'
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'name': name, 'version': version}))
        versions = self.versions
        class Registry(BaseHTTPRequestHandler):
            def do_GET(self):
                from urllib.parse import unquote
                name = unquote(self.path[1:].removesuffix('/latest'))
                payload = {'name': name, 'version': versions[name]}
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode())
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Registry)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.registry = 'http://127.0.0.1:' + str(server.server_port)

    def run_check(self, *extra, env=None):
        return subprocess.run([sys.executable, str(ROOT / 'bin/qmd-updates'),
                               '--installation', str(self.install), '--registry', self.registry,
                               '--state-file', str(self.state), *extra],
                              text=True, capture_output=True, timeout=10, env=env)

    def test_current_then_new_qmd_and_backend_releases(self):
        current = self.run_check()
        self.assertEqual(current.returncode, 0, current.stderr)
        self.assertEqual(json.loads(current.stdout)['status'], 'current')
        self.versions.update({'@tobilu/qmd': '2.9.0', 'node-llama-cpp': '3.22.0'})
        update = self.run_check()
        self.assertEqual(update.returncode, 2, update.stderr)
        report = json.loads(update.stdout)
        self.assertEqual(len(report['updates']), 2)
        self.assertEqual(json.loads(self.state.read_text())['status'], 'updates_available')

    def test_bad_registry_data_is_failure_and_does_not_claim_current(self):
        self.run_check()
        self.versions['@tobilu/qmd'] = 'not-a-version'
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(self.state.read_text())['status'], 'failed')

    def test_nested_backend_is_the_installed_backend(self):
        nested = self.install / 'node_modules/@tobilu/qmd/node_modules/node-llama-cpp'
        nested.mkdir(parents=True)
        (nested / 'package.json').write_text(json.dumps({'version': '3.20.0'}))
        result = self.run_check()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)['updates'][0]['installed'], '3.20.0')

    def test_notification_is_sent_once_for_each_release_set(self):
        self.versions['@tobilu/qmd'] = '2.9.0'
        tools = self.root / 'tools'; tools.mkdir()
        log = self.root / 'notifications'
        executable = tools / 'osascript'
        executable.write_text('#!' + sys.executable + '\nfrom pathlib import Path\nwith Path(' + repr(str(log)) + ').open("a") as f: f.write("sent\\n")\n')
        executable.chmod(0o755)
        env = os.environ | {'PATH': str(tools) + os.pathsep + os.environ['PATH']}
        for _ in range(2):
            self.assertEqual(self.run_check('--notify', env=env).returncode, 2)
        self.assertEqual(log.read_text().splitlines(), ['sent'])

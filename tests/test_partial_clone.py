"""Test bin/check in a GitHub Actions checkout that is a sparse, partial clone of a private repository.

A local smart-HTTP server stands in for GitHub and answers only requests that carry the job's token, as GitHub does
for a private repository; no other network is used.
"""

import base64
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "starter"
GIT = shutil.which("git")
TOKEN = "job-token"
# actions/checkout authenticates as x-access-token with the job's token.
AUTHORIZATION = "Basic " + base64.b64encode(("x-access-token:" + TOKEN).encode()).decode()


class PrivateGitServer(http.server.BaseHTTPRequestHandler):
    """Serve the repositories under server.root by Git's smart HTTP protocol, only to requests with the token."""

    # Headers and body go out in separate writes, which Nagle's algorithm would hold for the client's delayed ACK.
    disable_nagle_algorithm = True

    def do_GET(self):
        self.serve()

    def do_POST(self):
        self.serve()

    def serve(self):
        if self.headers.get("Authorization") != AUTHORIZATION:
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="private"')
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        path, _, query = self.path.partition("?")
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        environment = {"GIT_PROJECT_ROOT": str(self.server.root), "GIT_HTTP_EXPORT_ALL": "1", "PATH_INFO": path,
                       "QUERY_STRING": query, "REQUEST_METHOD": self.command, "CONTENT_LENGTH": str(len(body)),
                       "CONTENT_TYPE": self.headers.get("Content-Type", ""),
                       "HTTP_CONTENT_ENCODING": self.headers.get("Content-Encoding", ""),
                       "GIT_PROTOCOL": self.headers.get("Git-Protocol", ""), "REMOTE_ADDR": "127.0.0.1",
                       "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
        output = subprocess.run([GIT, "http-backend"], input=body, env=environment, capture_output=True,
                                check=True).stdout
        head, _, payload = output.partition(b"\r\n\r\n")
        status, headers = 200, []
        for line in head.decode().split("\r\n"):
            name, _, value = line.partition(":")
            if name.lower() == "status":
                status = int(value.split()[0])
            else:
                headers.append((name, value.strip()))
        self.send_response(status)
        for name, value in headers:
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


class PartialCloneTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="project starter partial clone ")
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.repo = self.base / "main checkout"
        shutil.copytree(SOURCE, self.repo, ignore=shutil.ignore_patterns("__pycache__", ".cache"))
        tools = self.base / "fake tools"
        tools.mkdir()
        for name, target in (("python3", sys.executable), ("git", GIT)):
            (tools / name).symlink_to(target)
        (tools / "shellcheck").write_text("#!/bin/sh\nexit 0\n")
        (tools / "shellcheck").chmod(0o755)
        # CI's own GitHub Actions variables would describe this repository's run, not the fixture's.
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GITHUB_", "GH_"))}
        self.env.update(PATH=str(tools), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        HOME=str(self.base / "home"), PYTHONDONTWRITEBYTECODE="1", GIT_TERMINAL_PROMPT="0")
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Starter test")
        self.git("config", "user.email", "test@example.invalid")
        served = self.base / "served"
        self.remote = served / "project.git"
        self.git("init", "--quiet", "--bare", "-b", "main", str(self.remote))
        self.git("config", "uploadpack.allowFilter", "true", root=self.remote)
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), PrivateGitServer)
        server.root = served
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.url = "http://127.0.0.1:%d/project.git" % server.server_port

    def git(self, *args, root=None, extra=None, check=True):
        return self.run_command("git", *args, root=root, extra=extra, check=check)

    def run_command(self, *args, root=None, extra=None, check=True):
        result = subprocess.run(args, cwd=root or self.repo, env=self.env | (extra or {}), text=True,
                                capture_output=True, timeout=30)
        if check:
            self.assertEqual(result.returncode, 0, (args, result.stdout, result.stderr))
        return result

    def commit(self, files):
        for name, text in files.items():
            (self.repo / name).write_text(text)
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "Change")
        return self.git("rev-parse", "HEAD").stdout.strip()

    def checkout(self, name, ref):
        """Check out ref as actions/checkout does with fetch-depth: 0, a sparse checkout that leaves out .env, and
        persist-credentials: false: a blob:none fetch, then a checkout, both with the token, which then goes away."""
        ci = self.base / name
        self.git("init", "--quiet", str(ci))
        self.git("remote", "add", "origin", self.url, root=ci)
        self.git("config", "core.sparseCheckout", "true", root=ci)
        (ci / ".git/info").mkdir(exist_ok=True)
        (ci / ".git/info/sparse-checkout").write_text("/*\n!.env\n")
        token = ("-c", "http.extraHeader=Authorization: " + AUTHORIZATION)
        self.git(*token, "fetch", "--quiet", "--no-tags", "--filter=blob:none", "origin",
                 "+refs/heads/*:refs/remotes/origin/*", "+" + ref + ":refs/remotes/checkout", root=ci)
        self.git(*token, "checkout", "--quiet", "--detach", "refs/remotes/checkout", root=ci)
        return ci

    def github(self, name, **payload):
        event = self.base / (name + ".json")
        event.write_text(json.dumps(payload))
        return {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": name, "GITHUB_EVENT_PATH": str(event),
                "GITHUB_BASE_REF": "main" if name == "pull_request" else ""}

    def assert_missing(self, root, *objects):
        """Each object is still only on the server; GIT_NO_LAZY_FETCH keeps the probe from fetching it."""
        for name in objects:
            result = self.git("cat-file", "-e", name, root=root, extra={"GIT_NO_LAZY_FETCH": "1"}, check=False)
            self.assertNotEqual(result.returncode, 0, name)

    def test_check_reads_a_sparse_partial_clone_only_after_fetch_base(self):
        before = self.commit({".env": "SECRET=1\n", "notes.txt": "old\n", "fixture.txt": "published trailing space \n"})
        self.git("push", "--quiet", str(self.remote), "main")
        # Pull request 1 edits .env, adds whitespace to notes.txt, and deletes fixture.txt; 2 changes notes.txt cleanly.
        for number, files in ((1, {".env": "SECRET=2 \n", "notes.txt": "old\nnew trailing space \n"}),
                              (2, {"notes.txt": "old\nclean\n"})):
            self.git("switch", "--quiet", "--create", "branch-%d" % number, "main")
            if number == 1:
                self.git("rm", "--quiet", "fixture.txt")
            self.commit(files)
            self.git("switch", "--quiet", "--detach", "main")
            self.git("merge", "--quiet", "--no-ff", "-m", "Merge", "branch-%d" % number)
            self.git("push", "--quiet", str(self.remote), "HEAD:refs/pull/%d/merge" % number)
        secrets = ("origin/main:.env", "HEAD:.env")
        pull_request = self.github("pull_request", number=1)
        ci = self.checkout("pull 1", "refs/pull/1/merge")
        self.assert_missing(ci, *secrets, "origin/main:notes.txt", "origin/main:fixture.txt")

        # The check step holds no token, so it fails with its own guidance instead of asking for credentials.
        result = self.run_command("bin/check", root=ci, extra=pull_request, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("bin/check --fetch-base", result.stderr)
        self.assertIn("docs/foundation/engineering-policy.md#hosted-ci", result.stderr)
        self.assertNotIn("Username", result.stderr)
        self.assertIn("\n### Hosted CI\n", (ci / "docs/foundation/engineering-policy.md").read_text())
        # So does the fetch without the token, which a private repository needs.
        result = self.run_command("bin/check", "--fetch-base", root=ci, extra=pull_request, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GH_TOKEN: ${{ github.token }}", result.stderr)
        self.assertIn("docs/foundation/engineering-policy.md#hosted-ci", result.stderr)

        fetched = self.run_command("bin/check", "--fetch-base", root=ci, extra=pull_request | {"GH_TOKEN": TOKEN})
        self.assertNotIn("Document metadata", fetched.stdout)
        self.assertNotIn(TOKEN, (ci / ".git/config").read_text())
        result = self.run_command("bin/check", root=ci, extra=pull_request, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("notes.txt:2: trailing whitespace", result.stdout)
        self.assertNotIn(".env", result.stdout)
        self.assertNotIn("fixture.txt", result.stdout)
        self.assert_missing(ci, *secrets)

        # Whitespace already on the base branch passes.
        clean = self.checkout("pull 2", "refs/pull/2/merge")
        self.run_command("bin/check", "--fetch-base", root=clean, extra=pull_request | {"GH_TOKEN": TOKEN})
        self.run_command("bin/check", root=clean, extra=pull_request)
        self.assert_missing(clean, "HEAD:.env")

        # A push to the default branch is checked from the commit it replaced.
        self.git("update-ref", "refs/heads/main", "refs/pull/1/merge", root=self.remote)
        pushed = self.checkout("push", "refs/heads/main")
        push = self.github("push", before=before)
        self.run_command("bin/check", "--fetch-base", root=pushed, extra=push | {"GH_TOKEN": TOKEN})
        result = self.run_command("bin/check", root=pushed, extra=push, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("notes.txt:2: trailing whitespace", result.stdout)
        self.assertNotIn(".env", result.stdout)
        self.assert_missing(pushed, before + ":.env", "HEAD:.env")

    def test_fetch_base_does_nothing_outside_a_hosted_partial_clone(self):
        self.commit({"notes.txt": "old\n"})
        self.commit({"notes.txt": "new trailing space \n"})
        # Neither a local run nor a GitHub Actions run in a checkout that isn't a partial clone fetches anything.
        for extra in ({}, self.github("push", before=self.git("rev-parse", "HEAD~").stdout.strip())):
            result = self.run_command("bin/check", "--fetch-base", extra=extra)
            self.assertNotIn("Document metadata", result.stdout)


if __name__ == "__main__":
    unittest.main()

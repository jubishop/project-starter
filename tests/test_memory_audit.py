"""Exercise the memory audit feature through bin/memory-audit in disposable adopters with fake services."""

import fcntl
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
README = ("# Memory\n\nPreserve this policy.\n\n## Active pages\n\n"
          "- [Incident](incident.md): an incident whose entry\n  spans two lines.\n")
CONTENT = ("---\nname: incident\ndescription: An incident.\ntype: project\nstatus: active\n---\n\n"
           "# Incident\n\nA durable rule.\n")
REPOSITORY = "example-owner/example"
API_KEY = "sk-ant-api03-fixture"
# Stream-json failures as Claude Code 2.1.312 prints them, trimmed to the fields the runner reads. The
# invalid key is from a real run on a bogus key; Claude Code shortens the API's credit refusal.
INVALID_KEY = (
    {"type": "assistant", "message": {"model": "<synthetic>", "role": "assistant", "content": [
        {"type": "text", "text": "Invalid API key · Fix external API key"}]},
     "error": "authentication_failed", "is_api_error_message": True, "api_error_status": 401},
    {"type": "result", "subtype": "success", "is_error": True, "api_error_status": 401,
     "result": "Invalid API key · Fix external API key", "terminal_reason": "api_error"},
)
REVOKED_KEY = ({"type": "result", "subtype": "success", "is_error": True, "api_error_status": 403,
                "result": "API Error: 403 permission_error", "terminal_reason": "api_error"},)
LOW_CREDIT = (
    {"type": "assistant", "message": {"model": "<synthetic>", "role": "assistant", "content": [
        {"type": "text", "text": "Credit balance is too low"}]},
     "error": "billing_error", "is_api_error_message": True, "api_error_status": 400},
    {"type": "result", "subtype": "success", "is_error": True, "api_error_status": 400,
     "result": "Credit balance is too low", "terminal_reason": "api_error"},
)
LOW_CREDIT_FROM_API = ({"type": "result", "subtype": "success", "is_error": True, "api_error_status": 400,
                        "result": "Your credit balance is too low to access the Anthropic API. Please go to "
                                  "Plans & Billing to upgrade or purchase credits.", "terminal_reason": "api_error"},)
USAGE_LIMIT = (
    {"type": "assistant", "message": {"content": [{"type": "text", "text": (
        'API Error: 400 {"type":"error","error":{"type":"invalid_request_error","message":"You have reached your '
        'specified API usage limits. You will regain access on 2026-11-01 at 00:00 UTC."}}')}]},
     "error": "invalid_request", "is_api_error_message": True, "api_error_status": 400},
    {"type": "result", "subtype": "success", "is_error": True, "api_error_status": 400,
     "result": "You have reached your specified API usage limits. You will regain access on 2026-11-01 at 00:00 UTC."},
)
RATE_LIMITED = (
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "API Error: Rate limit reached"}]},
     "error": "rate_limit", "is_api_error_message": True, "api_error_status": 429},
    {"type": "result", "subtype": "success", "is_error": True, "api_error_status": 429,
     "result": "API Error: Rate limit reached"},
)
# The model quoting a note is not an API refusal.
QUOTED_CREDIT = ({"type": "assistant", "message": {"content": [
    {"type": "text", "text": "The note says the credit balance is too low; the key was rejected with 401."}]}},)


def clean_environment(home):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, HOME=str(home), PYTHONDONTWRITEBYTECODE="1")
    return env


class MemoryAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One adopter with the feature enabled, copied by each test.
        cls.template_dir = tempfile.TemporaryDirectory(prefix="memory audit template ")
        cls.template = Path(cls.template_dir.name).resolve() / "adopter"
        cls.template.mkdir()
        env = clean_environment(cls.template.parent)
        for args in (["git", "init", "--quiet", "-b", "main"], ["git", "config", "user.name", "Audit test"],
                     ["git", "config", "user.email", "test@example.invalid"],
                     [str(ROOT / "bin/sync"), "--init", "--ref", "WORKTREE", "--enable", "memory-audit", "."]):
            subprocess.run(args, cwd=cls.template, env=env, check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.template_dir.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="memory audit ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.repo = self.base / "repo"
        shutil.copytree(self.template, self.repo, symlinks=True)
        self.fake = self.base / "tools"
        self.fake.mkdir()
        self.env = clean_environment(self.base)
        self.env["PATH"] = str(self.fake) + os.pathsep + os.environ["PATH"]
        self.note = self.repo / "memory/incident.md"
        self.note.write_text(CONTENT)
        self.readme = self.repo / "memory/README.md"
        self.readme.write_text(README)
        self.configure(repository=REPOSITORY)
        self.git("add", ".")
        self.git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "✅ test: Add memory audit fixture")
        self.origin = self.base / "origin.git"
        self.git("init", "--quiet", "--bare", "-b", "main", str(self.origin), root=self.base)
        self.git("remote", "add", "origin", str(self.origin))
        self.git("push", "--quiet", "origin", "main")
        self.head = self.git("rev-parse", "HEAD")
        self.result = {
            "report": "# Memory audit report\n\n- Active notes reviewed: 1\n\n## Per-note findings\n\nIncident checked.\n",
            "findings": [{"path": "memory/incident.md", "verdict": "keep", "evidence": "Current source keeps the rule."}],
            "changes": [],
        }
        self.response = self.base / "response.json"
        self.calls = self.base / "calls.jsonl"
        # What the model looks at: notes it reads, and other reads and searches.
        self.session = {"reads": ["memory/incident.md"], "lookups": 1}
        self.session_file = self.base / "session.json"
        # A commit the fake model pushes to origin as another session would, while the audit runs.
        self.during = self.base / "during.json"
        self.gh_calls = self.base / "gh-calls.jsonl"
        self.open_issues = self.base / "open-issues.json"
        self.missing_labels = self.base / "missing-labels"
        self.notifications = self.base / "notifications.jsonl"
        self.launchd_calls = self.base / "launchctl.jsonl"
        self.qmd_config = self.base / "qmd-index.yml"
        self.qmd_index = self.base / "qmd-index-path"
        # The GitHub CLI keeps the open failure issues in a file, so a create is seen by later lists.
        self.executable("gh", (
            "import json,pathlib,sys\n"
            "args = sys.argv[1:]\n"
            "body = sys.stdin.read() if '--body-file' in args else None\n"
            f"with open({str(self.gh_calls)!r}, 'a') as f: f.write(json.dumps({{'args': args, 'body': body}})+'\\n')\n"
            f"issues = pathlib.Path({str(self.open_issues)!r})\n"
            "if args[:2] == ['issue', 'list'] and '--search' in args:\n"
            " print(issues.read_text() if issues.exists() else '[]')\n"
            "elif args[:2] == ['issue', 'create']:\n"
            f" if '--label' in args and pathlib.Path({str(self.missing_labels)!r}).exists():\n"
            "  sys.exit(\"could not add label: 'area: tooling' not found\")\n"
            " issues.write_text(json.dumps([{'number': 999, 'title': args[args.index('--title') + 1]}]))\n"
            " print('https://github.com/example-owner/example/issues/999')\n"
            "elif args[:2] == ['issue', 'close']:\n"
            " issues.write_text(json.dumps([i for i in json.loads(issues.read_text()) if str(i['number']) != args[2]]))\n"
            "elif args[1:2] == ['list']:\n"
            " print('[]')\n"
        ))
        self.executable("osascript", (
            "import json,sys\n"
            f"with open({str(self.notifications)!r}, 'a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')\n"
        ))
        self.executable("qmd", (
            "import os,pathlib,sys\n"
            # Like QMD, an INDEX_PATH must be in an existing folder.
            "if 'INDEX_PATH' in os.environ and not pathlib.Path(os.environ['INDEX_PATH']).parent.is_dir():\n"
            " sys.exit('SQLiteError: unable to open database file')\n"
            "if sys.argv[1:] == ['update']:\n"
            f" pathlib.Path({str(self.qmd_config)!r}).write_text("
            "(pathlib.Path(os.environ['QMD_CONFIG_DIR']) / 'index.yml').read_text())\n"
            f" pathlib.Path({str(self.qmd_index)!r}).write_text(os.environ.get('INDEX_PATH', ''))\n"
            "print('Index ready')\n"
        ))
        self.executable("claude", (
            "import json,os,pathlib,subprocess,sys\n"
            "status = sys.argv[1:3] == ['auth','status']\n"
            "prompt = '' if status else sys.stdin.read()\n"
            f"with open({str(self.calls)!r}, 'a') as f: f.write(json.dumps({{'args':sys.argv[1:], 'env':dict(os.environ), 'prompt':prompt}})+'\\n')\n"
            # Like Claude Code, an ANTHROPIC_API_KEY takes precedence over the saved subscription login.
            "if status and 'ANTHROPIC_API_KEY' in os.environ:\n"
            " print(json.dumps({'loggedIn':True,'authMethod':'api_key','apiProvider':'firstParty',"
            "'apiKeySource':'ANTHROPIC_API_KEY'}))\n"
            f"elif status and pathlib.Path({str(self.base / 'logged-out')!r}).exists():\n"
            " print(json.dumps({'loggedIn':False,'authMethod':'none','apiProvider':'firstParty'}))\n"
            "elif status:\n print(json.dumps({'loggedIn':True,'authMethod':'claude.ai','apiProvider':'firstParty'}))\n"
            "else:\n"
            f" response=json.loads(pathlib.Path({str(self.response)!r}).read_text())\n"
            f" calls=[json.loads(x) for x in pathlib.Path({str(self.calls)!r}).read_text().splitlines()]\n"
            " attempt=sum('-p' in c['args'] for c in calls)-1\n"
            " if isinstance(response,list): response=response[attempt]\n"
            f" session=json.loads(pathlib.Path({str(self.session_file)!r}).read_text())\n"
            " if isinstance(session,list): session=session[attempt]\n"
            " uses=[('Read',{'file_path':os.path.join(os.getcwd(),path)}) for path in session['reads']]\n"
            " uses+=[('Grep',{'pattern':'rule','path':os.getcwd()})]*session['lookups']\n"
            " for n,(name,args) in enumerate(uses):\n"
            "  print(json.dumps({'type':'assistant','message':{'content':[{'type':'tool_use','id':str(n),'name':name,'input':args}]}}))\n"
            " print(json.dumps({'type':'result','subtype':'success','structured_output':response}))\n"
            f" during=pathlib.Path({str(self.during)!r})\n"
            " if during.exists():\n"
            "  change=json.loads(during.read_text())\n"
            f"  other={str(self.base / 'other')!r}\n"
            f"  subprocess.run(['git','clone','--quiet',{str(self.origin)!r},other],check=True,capture_output=True)\n"
            "  pathlib.Path(other,change['path']).write_text(change['text'])\n"
            "  for args in (['add','-A'],['-c','user.name=Other','-c','user.email=other@example.invalid','commit','--quiet','-m','Other work'],['push','--quiet','origin','HEAD:main']):\n"
            "   subprocess.run(['git','-C',other,*args],check=True,capture_output=True)\n"
        ))

    def executable(self, name, body):
        path = self.fake / name
        path.write_text(f"#!{sys.executable}\n" + body)
        path.chmod(0o755)

    def git(self, *args, root=None):
        result = subprocess.run(["git", *args], cwd=root or self.repo, env=self.env, text=True,
                                capture_output=True, check=True)
        return result.stdout.strip()

    def configure(self, **memory_audit):
        path = self.repo / ".config/knowledge.json"
        config = json.loads((ROOT / "starter/.config/knowledge.json").read_text())
        config["memoryAudit"] = memory_audit
        path.write_text(json.dumps(config, indent=2) + "\n")

    def audit(self, *args, env=None, check=True):
        result = subprocess.run([str(self.repo / "bin/memory-audit"), *args], cwd=self.repo, env=env or self.env,
                                text=True, capture_output=True, timeout=120)
        if check:
            self.assertEqual(result.returncode, 0, (args, result.stdout, result.stderr))
        return result

    def run_audit(self, force=False):
        """Run an audit that must succeed, and return its JSON result."""
        self.response.write_text(json.dumps(self.result))
        self.session_file.write_text(json.dumps(self.session))
        return json.loads(self.audit("run", *(["--force"] if force else [])).stdout)

    def failed_audit(self, message, force=False):
        """Run an audit that must fail with a message matching the pattern."""
        self.response.write_text(json.dumps(self.result))
        self.session_file.write_text(json.dumps(self.session))
        result = self.audit("run", *(["--force"] if force else []), check=False)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertRegex(result.stderr, message)
        return result

    def commit_fixture(self, path, message):
        """Commit and push a fixture change, since each audit starts from origin's main."""
        self.git("add", path)
        self.git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", message)
        self.git("push", "--quiet", "origin", "main")

    def remote_head(self):
        return self.git("rev-parse", "main", root=self.origin)

    def gh(self, *prefix):
        if not self.gh_calls.exists():
            return []
        calls = [json.loads(line) for line in self.gh_calls.read_text().splitlines()]
        return [call for call in calls if call["args"][:len(prefix)] == list(prefix)]

    def model_calls(self):
        if not self.calls.exists():
            return []
        return [call for call in map(json.loads, self.calls.read_text().splitlines()) if "-p" in call["args"]]

    def fail_model(self):
        self.executable("claude", "import json,sys\n"
                        "print(json.dumps({'loggedIn': True, 'authMethod': 'claude.ai', 'apiProvider': 'firstParty'}))\n"
                        "sys.exit(0 if sys.argv[1:3] == ['auth','status'] else 1)\n")

    def keep_working_model(self):
        shutil.copy2(self.fake / "claude", self.base / "claude-working")

    def restore_model(self):
        """Return a model failed by fail_model to working order."""
        shutil.copy2(self.base / "claude-working", self.fake / "claude")

    def archive(self):
        self.result["findings"][0]["verdict"] = "archive"
        self.result["changes"] = [{"path": "memory/incident.md", "archive": True,
                                   "content": CONTENT.replace("status: active", "status: resolved")}]

    def add_notes(self, readme, *names):
        """Commit more reference notes and a new README, and expect the model to review them too."""
        for name in names:
            (self.repo / "memory" / (name + ".md")).write_text(
                f"---\nname: {name}\ndescription: A {name} lesson.\ntype: reference\n---\n\n# {name.title()}\n\n"
                "A lasting lesson.\n")
        self.readme.write_text(readme)
        self.commit_fixture("memory", "✅ test: Add more memory notes")
        notes = sorted(["incident", *names])
        self.result["report"] = self.result["report"].replace("reviewed: 1", f"reviewed: {len(notes)}")
        self.result["findings"] = [{"path": f"memory/{name}.md", "verdict": "keep", "evidence": "Checked."}
                                   for name in notes]
        self.session = {"reads": [f"memory/{name}.md" for name in notes], "lookups": len(notes)}

    def published_files(self, commit):
        return sorted(self.git("show", "--no-renames", "--name-only", "--format=", commit,
                               root=self.origin).splitlines())

    # Publishing

    def test_archive_is_committed_to_main_without_touching_user_checkout(self):
        self.archive()
        self.note.write_text(CONTENT + "\nUncommitted user edit.\n")
        before = self.note.read_bytes()
        output = self.run_audit()
        self.assertEqual(output["status"], "success")
        self.assertEqual(self.note.read_bytes(), before)
        self.assertEqual(self.readme.read_text(), README)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.head)
        published = output["publishedCommit"]
        self.assertEqual(self.remote_head(), published)
        self.assertEqual(self.git("rev-parse", published + "^", root=self.origin), self.head)
        self.assertEqual(self.published_files(published),
                         ["memory/README.md", "memory/archive/incident.md", "memory/incident.md"])
        self.assertIn("memory audit", self.git("log", "-1", "--format=%s", published, root=self.origin))
        self.assertEqual(self.git("log", "-1", "--format=%an", published, root=self.origin), "Audit test")
        self.assertEqual(self.git("log", "-1", "--format=%(trailers:only)", published, root=self.origin), "")
        archived = self.git("show", published + ":memory/archive/incident.md", root=self.origin)
        self.assertIn("status: resolved", archived)
        index = self.git("show", published + ":memory/README.md", root=self.origin)
        self.assertIn("Preserve this policy.", index)
        self.assertIn("## Active pages", index)
        self.assertNotIn("incident", index)
        run_dir = Path(output["directory"])
        self.assertFalse((run_dir / "repository").exists())
        self.assertIn("memory/archive/incident.md", (run_dir / "memory-audit.patch").read_text())
        # The user's edit is unstaged, so the index still matches the audited revision.
        self.git("apply", "--cached", "--check", str(run_dir / "memory-audit.patch"))

    def test_the_audit_commit_carries_the_configured_trailers(self):
        self.configure(repository=REPOSITORY, commitTrailers={
            "Example-Deploy": "skip", "Example-Deploy-Reason": "Memory notes do not run in production."})
        self.commit_fixture(".config/knowledge.json", "✅ test: Add audit trailers")
        self.archive()
        published = self.run_audit()["publishedCommit"]
        trailers = self.git("log", "-1", "--format=%(trailers:only,unfold)", published, root=self.origin)
        self.assertEqual(trailers.splitlines(), ["Example-Deploy: skip",
                                                 "Example-Deploy-Reason: Memory notes do not run in production."])

    def test_the_commit_reaches_every_push_url(self):
        mirror = self.base / "mirror.git"
        self.git("init", "--quiet", "--bare", "-b", "main", str(mirror), root=self.base)
        self.git("push", "--quiet", str(mirror), "main")
        self.git("remote", "set-url", "--add", "--push", "origin", str(self.origin))
        self.git("remote", "set-url", "--add", "--push", "origin", str(mirror))
        self.archive()
        published = self.run_audit()["publishedCommit"]
        self.assertEqual(self.remote_head(), published)
        self.assertEqual(self.git("rev-parse", "main", root=mirror), published)

    def test_archive_removes_only_that_notes_index_entry(self):
        self.add_notes(
            "# Memory\n\nPreserve this policy.\n\n## Active pages\n\n"
            "- [Alpha](alpha.md): the first lesson.\n"
            "- [Incident](incident.md): an incident whose entry\n  spans two lines.\n"
            "- [Omega](omega.md): the last lesson,\n  also on two lines.\n\n## Later\n\nMore policy.\n",
            "alpha", "omega")
        self.result["findings"][1]["verdict"] = "archive"
        self.result["changes"] = [{"path": "memory/incident.md", "archive": True,
                                   "content": CONTENT.replace("status: active", "status: resolved")}]
        published = self.run_audit()["publishedCommit"]
        self.assertEqual(self.git("show", published + ":memory/README.md", root=self.origin) + "\n",
                         "# Memory\n\nPreserve this policy.\n\n## Active pages\n\n"
                         "- [Alpha](alpha.md): the first lesson.\n"
                         "- [Omega](omega.md): the last lesson,\n  also on two lines.\n\n## Later\n\nMore policy.\n")

    def test_a_configured_index_heading_names_the_list_to_edit(self):
        self.readme.write_text(README.replace("## Active pages", "## Active memory index"))
        self.configure(repository=REPOSITORY, indexHeading="Active memory index")
        self.commit_fixture(".", "✅ test: Rename the active index")
        self.archive()
        output = self.run_audit()
        index = self.git("show", output["publishedCommit"] + ":memory/README.md", root=self.origin)
        self.assertIn("## Active memory index", index)
        self.assertNotIn("incident", index)
        self.assertIn('"Active memory index" list', self.model_calls()[0]["prompt"])

    def test_a_readme_without_the_index_heading_fails_before_the_model(self):
        self.readme.write_text(README.replace("## Active pages", "## Active notes"))
        self.commit_fixture("memory/README.md", "✅ test: Rename the active index")
        self.failed_audit("no '## Active pages' heading.*memoryAudit.indexHeading")
        self.assertEqual(self.model_calls(), [])

    def test_an_update_leaves_the_readme_untouched(self):
        self.result["changes"] = [{"path": "memory/incident.md", "archive": False,
                                   "content": CONTENT + "\nVerified against current source.\n"}]
        published = self.run_audit()["publishedCommit"]
        self.assertEqual(self.published_files(published), ["memory/incident.md"])

    def test_an_archive_linked_from_readme_policy_is_rejected(self):
        self.readme.write_text(README.replace("this policy.", "this policy and [the incident](incident.md)."))
        self.commit_fixture("memory/README.md", "✅ test: Link a note from README policy")
        self.archive()
        self.result = [self.result, self.result]
        self.failed_audit("memory/README.md: missing link destination incident.md")
        self.assertEqual(self.remote_head(), self.git("rev-parse", "HEAD"))

    def test_a_run_without_changes_publishes_nothing(self):
        output = self.run_audit()
        self.assertEqual(output["status"], "success")
        self.assertNotIn("publishedCommit", output)
        self.assertEqual(self.remote_head(), self.head)

    def test_changes_land_on_a_main_that_moved_elsewhere_during_the_audit(self):
        self.archive()
        self.during.write_text(json.dumps({"path": "docs/README.md", "text": "# Docs\n\nNewer.\n"}))
        published = self.run_audit()["publishedCommit"]
        self.assertEqual(self.remote_head(), published)
        self.assertEqual(self.git("log", "-1", "--format=%s", published + "^", root=self.origin), "Other work")

    def test_memory_changed_on_main_during_the_audit_fails_without_pushing(self):
        self.archive()
        self.during.write_text(json.dumps({"path": "memory/incident.md", "text": CONTENT + "\nNewer fact.\n"}))
        self.failed_audit("main changed memory/")
        self.assertEqual(self.git("log", "-1", "--format=%s", "main", root=self.origin), "Other work")
        self.assertEqual(len(self.gh("issue", "create")), 1)

    # Model, evidence, and change gate

    def test_without_a_key_a_read_only_audit_uses_the_subscription(self):
        # Only the checkout's .env supplies the audit's key, and an empty one is no key.
        self.env.update(ANTHROPIC_API_KEY="fixture-key", OPENROUTER_API_KEY="fixture-router",
                        MEMORY_AUDIT_ANTHROPIC_API_KEY="fixture-shell-key")
        self.set_api_key("MEMORY_AUDIT_ANTHROPIC_API_KEY=")
        output = self.run_audit()
        self.assertEqual(output["credential"], "subscription")
        self.assertNotIn("fallback", output)
        [call] = self.model_calls()
        args = call["args"]
        self.assertEqual(args[args.index("--model") + 1], "claude-sonnet-5-5")
        self.assertEqual(args[args.index("--effort") + 1], "high")
        for flag in ("--restricted", "--no-session-persistence", "--strict-mcp-config"):
            self.assertIn(flag, args)
        self.assertEqual(args[args.index("--tools") + 1], "Bash,Read,Glob,Grep")
        self.assertEqual(args[args.index("--permission-mode") + 1], "manual")
        self.assertEqual(args[args.index("--permission-prompts") + 1], "none")
        rules = json.loads(args[args.index("--settings") + 1])["permissions"]
        self.assertFalse([rule for rule in rules["allow"] if not rule.startswith(("Bash(jq ", "Bash(qmd search "))])
        for key in ("ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "MEMORY_AUDIT_ANTHROPIC_API_KEY"):
            self.assertNotIn(key, call["env"])
        self.assertNotIn("{{", call["prompt"])
        self.assertNotIn("Project context", call["prompt"])
        self.assertIn('"Active pages" list', call["prompt"])

    def test_project_context_joins_the_prompt(self):
        self.configure(repository=REPOSITORY, context="Ledgers under memory/sentry/ are historical.")
        self.commit_fixture(".config/knowledge.json", "✅ test: Add audit context")
        self.run_audit()
        prompt = self.model_calls()[0]["prompt"]
        self.assertIn("## Project context\n\nLedgers under memory/sentry/ are historical.\n\n## Evidence", prompt)

    def test_search_index_holds_only_the_clones_collections(self):
        personal = self.base / "home-memory"
        personal.mkdir()
        self.git("config", "knowledge.homeMemoryPath", str(personal))
        output = self.run_audit()
        clone = Path(output["directory"]) / "repository"
        collections = json.loads(self.qmd_config.read_text())["collections"]
        shared = json.loads((ROOT / "starter/.config/knowledge.json").read_text())["collections"]
        self.assertEqual(set(collections), set(shared))
        for collection in collections.values():
            self.assertTrue(Path(collection["path"]).is_relative_to(clone), collection["path"])
        # Claude Code withholds XDG_CACHE_HOME from the model's tools, so qmd search finds the index by INDEX_PATH.
        index = self.model_calls()[0]["env"].get("INDEX_PATH", "")
        self.assertTrue(Path(index).is_relative_to(clone), index)
        self.assertEqual(self.qmd_index.read_text(), index)

    def test_api_key_login_stops_before_model_request(self):
        self.executable("claude", "import json\nprint(json.dumps({'loggedIn': True, 'authMethod': 'api_key', "
                        "'apiProvider': 'firstParty'}))\n")
        self.failed_audit("Claude subscription")
        self.assertFalse((self.repo / ".cache/memory-audit/last-success.json").exists())

    # Credentials

    def set_api_key(self, line="MEMORY_AUDIT_ANTHROPIC_API_KEY=" + API_KEY):
        """Write the project's key line into the checkout's ignored .env, among unrelated settings."""
        (self.repo / ".env").write_text("DATABASE_URL=postgresql://localhost/example\n" + line + "\nOTHER=1\n")

    def refuse_key(self, events, from_call=0):
        """Make model runs that bill the API key, from the given model call on, print these events and exit 1."""
        (self.base / "refusal.json").write_text(json.dumps(events))
        working = self.base / "claude-working"
        if not working.exists():
            self.keep_working_model()
        self.executable("claude", (
            "import json,os,pathlib,sys\n"
            f"log = pathlib.Path({str(self.calls)!r})\n"
            "earlier = sum('-p' in json.loads(x)['args'] for x in log.read_text().splitlines()) if log.exists() else 0\n"
            f"if '-p' in sys.argv and 'ANTHROPIC_API_KEY' in os.environ and earlier >= {from_call}:\n"
            f" with open({str(self.calls)!r}, 'a') as f: f.write(json.dumps({{'args':sys.argv[1:], "
            "'env':dict(os.environ), 'prompt':sys.stdin.read()})+'\\n')\n"
            f" for event in json.loads(pathlib.Path({str(self.base / 'refusal.json')!r}).read_text()):\n"
            "  print(json.dumps(event))\n"
            " sys.exit(1)\n"
            f"os.execv(sys.executable, [sys.executable, {str(working)!r}, *sys.argv[1:]])\n"
        ))

    def latest(self):
        return json.loads((self.repo / ".cache/memory-audit/latest.json").read_text())

    def test_the_projects_key_from_its_env_file_bills_the_audit(self):
        self.set_api_key(f'export MEMORY_AUDIT_ANTHROPIC_API_KEY="{API_KEY}"  # this project only')
        output = self.run_audit()
        self.assertEqual((output["status"], output["credential"]), ("success", "api-key"))
        self.assertNotIn("fallback", output)
        [call] = self.model_calls()
        self.assertEqual(call["env"]["ANTHROPIC_API_KEY"], API_KEY)
        for key in ("MEMORY_AUDIT_ANTHROPIC_API_KEY", "DATABASE_URL", "OTHER"):
            self.assertNotIn(key, call["env"])
        self.assertEqual(json.loads((Path(output["directory"]) / "run-meta.json").read_text())["credential"], "api-key")

    def test_claude_withholds_the_key_from_the_models_tools(self):
        # Claude Code passes its environment to Bash, where jq's env builtin reads it without approval. Scrub
        # mode still bills the key but withholds it from tool processes, on every attempt and whatever the shell sets.
        self.env["CLAUDE_CODE_SUBPROCESS_ENV_SCRUB"] = "0"
        self.set_api_key()
        self.refuse_key(LOW_CREDIT)
        self.run_audit()
        key_attempt, subscription_attempt = self.model_calls()
        self.assertEqual(key_attempt["env"]["ANTHROPIC_API_KEY"], API_KEY)
        for call in (key_attempt, subscription_attempt):
            self.assertEqual(call["env"].get("CLAUDE_CODE_SUBPROCESS_ENV_SCRUB"), "1")

    def test_a_key_claude_would_not_use_stops_before_the_model(self):
        self.set_api_key()
        self.executable("claude", "import json\nprint(json.dumps({'loggedIn': True, 'authMethod': 'claude.ai', "
                        "'apiProvider': 'firstParty'}))\n")
        self.failed_audit("MEMORY_AUDIT_ANTHROPIC_API_KEY")
        self.assertEqual(self.model_calls(), [])

    def test_a_refused_key_reruns_the_attempt_on_the_subscription(self):
        self.set_api_key()
        cases = (("invalid", INVALID_KEY, "key-rejected", 401), ("revoked", REVOKED_KEY, "key-rejected", 403),
                 ("shortened credit message", LOW_CREDIT, "credit-balance", 400),
                 ("API credit message", LOW_CREDIT_FROM_API, "credit-balance", 400),
                 ("spend limit", USAGE_LIMIT, "usage-limit", 400))
        for name, events, trigger, status in cases:
            with self.subTest(name):
                self.refuse_key(events)
                before = len(self.model_calls())
                output = self.run_audit(force=True)
                key_attempt, subscription_attempt = self.model_calls()[before:]
                self.assertEqual(key_attempt["env"]["ANTHROPIC_API_KEY"], API_KEY)
                self.assertNotIn("ANTHROPIC_API_KEY", subscription_attempt["env"])
                self.assertEqual(subscription_attempt["prompt"], key_attempt["prompt"])
                self.assertEqual((output["status"], output["credential"]), ("success", "subscription"))
                fallback = output["fallback"]
                self.assertEqual((fallback["trigger"], fallback["status"]), (trigger, status))
                self.assertEqual(fallback["message"], events[-1]["result"])
                run_dir = Path(output["directory"])
                self.assertIn("api_error_status", (run_dir / "api-key-events.jsonl").read_text())
                self.assertTrue((run_dir / "api-key-claude.log").exists())
                self.assertNotIn("api_error_status", (run_dir / "events.jsonl").read_text())

    def test_a_refused_key_on_the_repair_attempt_also_falls_back(self):
        self.set_api_key()
        self.refuse_key(LOW_CREDIT, from_call=1)
        # The key's first attempt skips a note, its repair is refused, and the subscription repairs it.
        self.session = [{"reads": [], "lookups": 1}, None, {"reads": ["memory/incident.md"], "lookups": 1}]
        output = self.run_audit()
        self.assertEqual((output["status"], output["credential"]), ("success", "subscription"))
        self.assertEqual(output["fallback"]["trigger"], "credit-balance")
        first, refused, repaired = self.model_calls()
        self.assertEqual([("ANTHROPIC_API_KEY" in call["env"]) for call in (first, refused, repaired)],
                         [True, True, False])
        self.assertEqual(repaired["prompt"], refused["prompt"])
        self.assertIn("not read: memory/incident.md", repaired["prompt"])
        run_dir = Path(output["directory"])
        for name in ("first-attempt-events.jsonl", "api-key-events.jsonl", "events.jsonl"):
            self.assertTrue((run_dir / name).exists(), name)

    def test_other_failures_on_the_key_do_not_fall_back(self):
        self.set_api_key()
        for name, events in (("rate limit", RATE_LIMITED), ("quoted credit error", QUOTED_CREDIT)):
            with self.subTest(name):
                self.refuse_key(events)
                before = len(self.model_calls())
                self.failed_audit("Claude exited 1", force=True)
                self.assertEqual(len(self.model_calls()) - before, 1)
                latest = self.latest()
                self.assertEqual((latest["status"], latest["credential"]), ("failed", "api-key"))
                self.assertNotIn("fallback", latest)

    def test_a_fallback_without_a_subscription_login_fails_and_reports(self):
        self.set_api_key()
        self.refuse_key(INVALID_KEY)
        (self.base / "logged-out").touch()
        self.failed_audit("Invalid API key.*HTTP 401.*claude auth login")
        self.assertEqual(len(self.model_calls()), 1)
        self.assertEqual(self.latest()["fallback"]["trigger"], "key-rejected")
        [created] = self.gh("issue", "create")
        self.assertIn("Invalid API key", created["body"])
        self.assertNotIn(API_KEY, created["body"])

    def test_unchanged_inputs_skip_model_and_force_runs_again(self):
        self.run_audit()
        self.assertEqual(self.run_audit()["status"], "skipped")
        self.assertEqual(len(self.model_calls()), 1)
        self.assertEqual(self.run_audit(force=True)["status"], "success")
        self.assertEqual(len(self.model_calls()), 2)

    def test_github_activity_invalidates_change_gate(self):
        self.run_audit()
        self.executable("gh", "print('[{\"number\":1,\"state\":\"OPEN\",\"updatedAt\":\"2026-10-02T00:00:00Z\"}]')\n")
        self.assertEqual(self.run_audit()["status"], "success")

    def test_a_project_without_notes_skips_the_model(self):
        self.note.unlink()
        self.readme.write_text("# Memory\n\n## Active pages\n\nNo notes yet.\n")
        self.commit_fixture("memory", "✅ test: Start without notes")
        output = self.run_audit()
        self.assertEqual(output["status"], "skipped")
        self.assertEqual(self.model_calls(), [])

    def test_the_context_lists_commits_since_the_last_audit(self):
        output = self.run_audit()
        context = json.loads((Path(output["directory"]) / "memory-audit-context.json").read_text())
        self.assertTrue(any(line.endswith("✅ test: Add memory audit fixture")
                            for line in context["commitsSinceLastAudit"]))
        self.assertEqual(context["activeNotes"], ["memory/incident.md"])
        [issues] = [call for call in self.gh("issue", "list") if "--search" not in call["args"]]
        self.assertEqual(issues["args"][issues["args"].index("--repo") + 1], REPOSITORY)

    def test_lock_prevents_overlapping_audits(self):
        state = self.repo / ".cache/memory-audit"
        state.mkdir(parents=True)
        with (state / "lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(self.run_audit()["status"], "skipped")
        self.assertFalse(self.calls.exists())

    def hold_turn(self):
        """Hold the lock that every project's audit on this machine takes turns with."""
        path = self.base / ".cache/project-starter/memory-audit.lock"
        path.parent.mkdir(parents=True, exist_ok=True)
        lock = path.open("a")
        self.addCleanup(lock.close)
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock

    def test_audits_of_different_projects_take_turns(self):
        lock = self.hold_turn()
        self.response.write_text(json.dumps(self.result))
        self.session_file.write_text(json.dumps(self.session))
        process = subprocess.Popen([str(self.repo / "bin/memory-audit"), "run"], cwd=self.repo, env=self.env,
                                   text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: process.poll() is None and process.kill())
        latest = self.repo / ".cache/memory-audit/latest.json"
        deadline = time.monotonic() + 30
        while not (latest.exists() and json.loads(latest.read_text())["status"] == "waiting"):
            self.assertLess(time.monotonic(), deadline, "the audit never waited for its turn")
            time.sleep(0.05)
        time.sleep(1.5)
        self.assertIsNone(process.poll())
        self.assertEqual(self.model_calls(), [])
        self.assertFalse(self.gh_calls.exists())
        lock.close()
        stdout, stderr = process.communicate(timeout=60)
        self.assertEqual(process.returncode, 0, stderr)
        self.assertEqual(json.loads(stdout)["status"], "success")
        self.assertEqual(len(self.model_calls()), 1)

    def test_a_turn_that_never_comes_fails_and_reports(self):
        self.configure(repository=REPOSITORY, lockWaitMinutes=0)
        self.hold_turn()
        self.failed_audit("Waited 0 minutes for another memory audit on this machine")
        self.assertEqual(self.model_calls(), [])
        self.assertIn("Waited 0 minutes", " ".join(json.loads(self.notifications.read_text())))
        [created] = self.gh("issue", "create")
        self.assertIn("~/.cache/project-starter/memory-audit.lock", created["body"])

    def test_runs_older_than_the_retention_window_are_pruned(self):
        runs = self.repo / ".cache/memory-audit/runs"
        old, recent = runs / "20260101T000000Z-old", runs / "20261001T000000Z-recent"
        for directory in (old, recent):
            directory.mkdir(parents=True)
        stale = time.time() - 61 * 86400
        os.utime(old, (stale, stale))
        self.run_audit()
        self.assertFalse(old.exists())
        self.assertTrue(recent.exists())

    # Validation

    def test_missing_note_coverage_rejects_result_and_keeps_failure_evidence(self):
        self.result["findings"] = []
        self.failed_audit("every active note")
        state = self.repo / ".cache/memory-audit"
        self.assertEqual(json.loads((state / "latest.json").read_text())["status"], "failed")
        self.assertFalse((state / "last-success.json").exists())

    def test_disallowed_writes_and_archive_overwrites_are_rejected(self):
        for target in ("memory/README.md", "memory/new.md", "memory/../AGENTS.md", "docs/README.md"):
            with self.subTest(target=target):
                self.result["changes"] = [{"path": target, "archive": False, "content": CONTENT}]
                self.failed_audit("existing active note")
        self.archive()
        (self.repo / "memory/archive").mkdir()
        (self.repo / "memory/archive/incident.md").write_text("Existing archive\n")
        self.commit_fixture("memory/archive", "✅ test: Add existing archive fixture")
        self.failed_audit("existing archive")

    def test_invalid_metadata_or_links_block_success(self):
        for content in (CONTENT.replace("status: active", "status: resolved"), CONTENT + "\n[Missing](missing.md)\n"):
            with self.subTest(content=content):
                self.result["changes"] = [{"path": "memory/incident.md", "archive": False, "content": content}]
                self.failed_audit("status must be active|missing link")

    def test_failed_model_does_not_export_patch_or_advance_success(self):
        self.fail_model()
        self.failed_audit("Claude exited 1")
        state = self.repo / ".cache/memory-audit"
        meta = json.loads((state / "latest.json").read_text())
        self.assertFalse((Path(meta["directory"]) / "memory-audit.patch").exists())
        self.assertFalse((Path(meta["directory"]) / "repository").exists())
        self.assertTrue((Path(meta["directory"]) / "claude.log").exists())
        self.assertFalse((state / "last-success.json").exists())

    def test_rejected_archive_is_restored_before_one_repair_attempt(self):
        (self.repo / "memory/archive").mkdir()
        (self.repo / "memory/archive/older.md").write_text(
            "---\nname: older\ndescription: Older evidence.\ntype: reference\n---\n\n# Older\n\n[Incident](../incident.md)\n")
        self.commit_fixture("memory/archive", "✅ test: Add an archived backlink fixture")
        self.archive()
        corrected = json.loads(json.dumps(self.result))
        corrected["findings"][0]["verdict"] = "keep"
        corrected["changes"] = []
        self.result = [self.result, corrected]
        output = self.run_audit()
        run_dir = Path(output["directory"])
        self.assertEqual(output["status"], "success")
        # An empty patch shows the repair started from the restored notes and README.
        self.assertEqual((run_dir / "memory-audit.patch").read_text(), "")
        self.assertTrue((run_dir / "rejected-result.json").exists())
        calls = self.model_calls()
        self.assertEqual(len(calls), 2)
        self.assertIn("missing link destination ../incident.md", calls[-1]["prompt"])

    def test_an_unread_note_gets_one_repair_attempt_then_fails(self):
        self.session = [{"reads": [], "lookups": 1}, {"reads": [], "lookups": 0}]
        self.failed_audit("not read: memory/incident.md")
        self.assertIn("not read: memory/incident.md", self.model_calls()[-1]["prompt"])
        self.assertEqual(self.remote_head(), self.head)

    def test_reading_the_notes_on_repair_is_accepted(self):
        self.session = [{"reads": [], "lookups": 1}, {"reads": ["memory/incident.md"], "lookups": 0}]
        self.assertEqual(self.run_audit()["status"], "success")

    def test_too_few_source_checks_are_rejected(self):
        self.session = {"reads": ["memory/incident.md"], "lookups": 0}
        self.failed_audit("0 source or evidence lookups for 1 note")

    # Failure reporting

    def test_a_failure_notifies_and_opens_the_issue_and_the_next_success_closes_it(self):
        self.keep_working_model()
        self.fail_model()
        self.failed_audit("Claude exited 1", force=True)
        [notification] = [json.loads(line) for line in self.notifications.read_text().splitlines()]
        self.assertIn("example memory audit failed", notification)
        self.assertIn("Claude exited 1", " ".join(notification))
        [created] = self.gh("issue", "create")
        args = created["args"]
        self.assertEqual(args[args.index("--repo") + 1], REPOSITORY)
        self.assertEqual(args[args.index("--title") + 1], "Memory audit failing")
        self.assertNotIn("--label", args)
        self.assertIn("Claude exited 1", created["body"])
        self.assertIn("next successful run closes this issue", created["body"])
        self.restore_model()
        self.assertEqual(self.run_audit()["status"], "success")
        [closed] = self.gh("issue", "close")
        self.assertEqual(closed["args"][2:5], ["999", "--repo", REPOSITORY])
        self.assertEqual(json.loads(self.open_issues.read_text()), [])
        self.assertEqual(len(self.notifications.read_text().splitlines()), 1)

    def test_the_failure_issue_carries_the_configured_labels(self):
        self.configure(repository=REPOSITORY, issueLabels=["bug", "area: tooling"])
        self.fail_model()
        self.failed_audit("Claude exited 1")
        [created] = self.gh("issue", "create")
        args = created["args"]
        self.assertEqual([args[i + 1] for i, arg in enumerate(args) if arg == "--label"], ["bug", "area: tooling"])

    def test_labels_that_cannot_be_applied_still_open_the_issue(self):
        self.configure(repository=REPOSITORY, issueLabels=["area: tooling"])
        self.missing_labels.touch()
        self.fail_model()
        self.failed_audit("Claude exited 1")
        refused, created = self.gh("issue", "create")
        self.assertIn("--label", refused["args"])
        self.assertNotIn("--label", created["args"])
        self.assertIn("could not apply the labels area: tooling", created["body"])
        self.assertIn("Claude exited 1", created["body"])

    def test_a_repeated_failure_comments_on_the_open_issue(self):
        self.open_issues.write_text(json.dumps([{"number": 41, "title": "Memory audit failing"}]))
        self.fail_model()
        self.failed_audit("Claude exited 1")
        self.assertEqual(self.gh("issue", "create"), [])
        [comment] = self.gh("issue", "comment", "41")
        self.assertIn("Claude exited 1", comment["body"])

    def test_a_success_closes_only_the_exact_failure_issue(self):
        self.open_issues.write_text(json.dumps([{"number": 7, "title": "Memory audit failing later"},
                                                {"number": 41, "title": "Memory audit failing"}]))
        self.assertEqual(self.run_audit()["status"], "success")
        [closed] = self.gh("issue", "close")
        self.assertEqual(closed["args"][2], "41")
        self.assertFalse(self.notifications.exists())

    def test_a_failed_run_is_never_skipped_next_time(self):
        self.run_audit()
        self.keep_working_model()
        self.fail_model()
        self.failed_audit("Claude exited 1", force=True)
        self.restore_model()
        self.assertEqual(self.run_audit()["status"], "success")

    def test_invalid_settings_fail_the_run_and_still_notify(self):
        self.configure(repository=REPOSITORY, schedule={"hour": 25})
        self.failed_audit("schedule.hour")
        [notification] = [json.loads(line) for line in self.notifications.read_text().splitlines()]
        self.assertIn("schedule.hour", " ".join(notification))
        self.assertEqual(self.gh("issue"), [])
        self.assertEqual(self.model_calls(), [])

    # Settings

    def settings(self, origin=None, check=True):
        if origin is not None:
            self.git("remote", "set-url", "origin", origin)
        result = self.audit("settings", check=check)
        return json.loads(result.stdout) if check else result

    def test_settings_default_from_a_github_origin(self):
        self.configure()
        for origin in ("git@github.com:jubishop/screenr.git", "https://github.com/jubishop/screenr",
                       "ssh://git@github.com/jubishop/screenr.git", "https://github.com/jubishop/screenr.git/"):
            with self.subTest(origin=origin):
                self.assertEqual(self.settings(origin), {
                    "repository": "jubishop/screenr", "launchAgentLabel": "com.jubishop.screenr.memory-audit",
                    "schedule": {"weekday": "Saturday", "hour": 6, "minute": 0}, "issueLabels": [],
                    "commitTrailers": {}, "indexHeading": "Active pages", "context": "", "lockWaitMinutes": 180})
        self.assertEqual(self.settings("git@github.com:JubiShop/PodHaven.git")["launchAgentLabel"],
                         "com.jubishop.podhaven.memory-audit")
        (self.repo / ".config/knowledge.json").write_text(
            (ROOT / "starter/.config/knowledge.json").read_text())
        self.assertEqual(self.settings()["repository"], "JubiShop/PodHaven")

    def test_settings_override_the_defaults(self):
        chosen = {"repository": "jubishop/screenr", "launchAgentLabel": "com.example.audit",
                  "schedule": {"weekday": "Sunday", "hour": 8, "minute": 30}, "issueLabels": ["bug", "area: tooling"],
                  "commitTrailers": {"Screenr-Deploy": "skip"}, "indexHeading": "Active memory index",
                  "context": "Historical ledgers stay.", "lockWaitMinutes": 30}
        self.configure(**chosen)
        self.assertEqual(self.settings("/not/github"), chosen)
        self.configure(schedule={"hour": 8})
        self.assertEqual(self.settings("git@github.com:jubishop/screenr.git")["schedule"],
                         {"weekday": "Saturday", "hour": 8, "minute": 0})

    def test_invalid_settings_are_rejected_with_their_name(self):
        cases = (({"lable": "x"}, "unsupported lable"), ({"repository": "screenr"}, "repository"),
                 ({"launchAgentLabel": "com/example"}, "launchAgentLabel"),
                 ({"schedule": {"weekday": "Caturday"}}, "schedule.weekday"),
                 ({"schedule": {"hour": True}}, "schedule.hour"), ({"schedule": {"minute": 60}}, "schedule.minute"),
                 ({"schedule": {"day": 1}}, "schedule"), ({"issueLabels": "bug"}, "issueLabels"),
                 ({"issueLabels": ["bug,docs"]}, "issueLabels"), ({"commitTrailers": {"Bad key": "x"}}, "commitTrailers"),
                 ({"commitTrailers": {"Deploy": "two\nlines"}}, "commitTrailers"),
                 ({"indexHeading": "## Active"}, "indexHeading"), ({"indexHeading": ""}, "indexHeading"),
                 ({"context": ["x"]}, "context"), ({"lockWaitMinutes": -1}, "lockWaitMinutes"),
                 ({"lockWaitMinutes": 1.5}, "lockWaitMinutes"), ({"lockWaitMinutes": True}, "lockWaitMinutes"))
        for setting, message in cases:
            with self.subTest(setting=setting):
                self.configure(**({"repository": REPOSITORY} | setting))
                result = self.settings(check=False)
                self.assertEqual(result.returncode, 1)
                self.assertIn(message, result.stderr)
        path = self.repo / ".config/knowledge.json"
        path.write_text(json.dumps(json.loads(path.read_text()) | {"memoryAudit": []}))
        self.assertIn("must be an object", self.settings(check=False).stderr)
        self.configure()
        result = self.settings(check=False)
        self.assertIn("origin is " + str(self.origin), result.stderr)
        self.assertIn("memoryAudit.repository", result.stderr)

    # Installation

    def default_python(self):
        python = self.base / ".local/bin/python3"
        python.parent.mkdir(parents=True)
        python.symlink_to(sys.executable)
        return python

    def fake_launchd(self):
        self.executable("launchctl", (
            "import json,sys\n"
            f"with open({str(self.launchd_calls)!r}, 'a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')\n"
            "sys.exit(1 if sys.argv[1] == 'print' else 0)\n"
        ))
        for name in ("plutil", "rg", "jq", "node"):
            self.executable(name, "pass\n")

    def install(self, env=None, check=True):
        result = self.audit("install", env=env, check=check)
        return json.loads(result.stdout) if check else result

    @unittest.skipUnless(sys.platform == "darwin", "launchd is macOS-only")
    def test_installer_registers_weekly_job_with_default_python_without_running_it(self):
        self.fake_launchd()
        self.configure(repository="jubishop/screenr")
        self.assertIn("uv python install --default", self.install(check=False).stderr)
        self.assertFalse(self.launchd_calls.exists())
        python = self.default_python()
        result = self.install()
        self.assertEqual(result["schedule"], "Saturday 06:00, Mac local time")
        self.assertEqual(Path(result["plist"]), self.base / "Library/LaunchAgents/com.jubishop.screenr.memory-audit.plist")
        settings = plistlib.loads(Path(result["plist"]).read_bytes())
        self.assertEqual(settings["Label"], "com.jubishop.screenr.memory-audit")
        self.assertEqual(settings["StartCalendarInterval"], {"Weekday": 6, "Hour": 6, "Minute": 0})
        self.assertEqual(settings["ProgramArguments"],
                         ["/bin/sh", "-c", 'exec "$0" "$@"', str(python), "-B", str(self.repo / "bin/memory-audit"), "run"])
        self.assertEqual(settings["EnvironmentVariables"]["PATH"].split(os.pathsep)[0], str(python.parent))
        calls = [json.loads(line) for line in self.launchd_calls.read_text().splitlines()]
        self.assertEqual([call[0] for call in calls], ["print", "bootstrap", "enable"])
        self.assertFalse(self.model_calls())

    @unittest.skipUnless(sys.platform == "darwin", "launchd is macOS-only")
    def test_installer_uses_the_configured_label_and_schedule(self):
        self.fake_launchd()
        self.default_python()
        self.configure(repository="jubishop/screenr", launchAgentLabel="com.example.audit",
                       schedule={"weekday": "Sunday", "hour": 8, "minute": 30})
        result = self.install()
        self.assertEqual(result["schedule"], "Sunday 08:30, Mac local time")
        settings = plistlib.loads(Path(result["plist"]).read_bytes())
        self.assertEqual((Path(result["plist"]).name, settings["Label"]), ("com.example.audit.plist", "com.example.audit"))
        self.assertEqual(settings["StartCalendarInterval"], {"Weekday": 0, "Hour": 8, "Minute": 30})
        calls = [json.loads(line) for line in self.launchd_calls.read_text().splitlines()]
        self.assertIn("gui/" + str(os.getuid()) + "/com.example.audit", calls[-1])

    @unittest.skipUnless(sys.platform == "darwin", "launchd is macOS-only")
    def test_installer_requires_the_tools_the_audit_uses(self):
        self.executable("launchctl", "import sys\nsys.exit(1 if sys.argv[1] == 'print' else 0)\n")
        for name in ("plutil", "rg", "git"):
            self.executable(name, "pass\n")
        self.default_python()
        # Only the fake tools and the interpreter are on PATH, and jq is not among them.
        (self.fake / "python3").symlink_to(sys.executable)
        result = self.install(env=self.env | {"PATH": str(self.fake)}, check=False)
        self.assertIn("Missing required command: jq", result.stderr)

    @unittest.skipUnless(sys.platform == "darwin", "launchd is macOS-only")
    def test_installer_uses_fnm_default_alias_instead_of_a_node_version(self):
        fnm = self.base / ".local/share/fnm"
        version_bin = fnm / "node-versions/v24.21.0/installation/bin"
        version_bin.mkdir(parents=True)
        (version_bin / "node").write_text(f"#!{sys.executable}\n")
        (version_bin / "node").chmod(0o755)
        (fnm / "aliases").mkdir(parents=True)
        (fnm / "aliases/default").symlink_to(fnm / "node-versions/v24.21.0/installation")
        shell = self.base / "fnm_multishells/123/bin"
        shell.parent.mkdir(parents=True)
        shell.symlink_to(version_bin)
        self.fake_launchd()
        (self.fake / "node").unlink()
        self.default_python()
        result = self.install(env=self.env | {"PATH": str(shell) + os.pathsep + self.env["PATH"]})
        entries = plistlib.loads(Path(result["plist"]).read_bytes())["EnvironmentVariables"]["PATH"].split(os.pathsep)
        self.assertIn(str(fnm / "aliases/default/bin"), entries)
        self.assertFalse([entry for entry in entries if "node-versions" in entry or "fnm_multishells" in entry], entries)

    @unittest.skipUnless(sys.platform == "darwin", "launchd is macOS-only")
    def test_installed_path_can_run_qmd_with_its_separate_runtime(self):
        runtime = self.base / "runtime"
        runtime.mkdir()
        bun = runtime / "bun"
        bun.write_text(f"#!{sys.executable}\nprint('Runtime ready')\n")
        bun.chmod(0o755)
        self.executable("qmd", "import subprocess\nsubprocess.run(['bun'], check=True)\n")
        self.fake_launchd()
        self.default_python()
        result = self.install(env=self.env | {"PATH": str(runtime) + os.pathsep + self.env["PATH"]})
        settings = plistlib.loads(Path(result["plist"]).read_bytes())
        result = subprocess.run([str(self.fake / "qmd"), "--version"],
                                env=settings["EnvironmentVariables"], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()

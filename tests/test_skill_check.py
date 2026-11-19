"""Test that the bundle's bin/check holds each skill in .agents/skills to the frontmatter rules runtimes read."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "starter"
# A description of exactly 1,024 characters, the Agent Skills limit, once YAML folds its lines together.
LONGEST = " ".join(["abcdefg"] * 128) + "."


def folded(text, words_per_line=8):
    """Return text as an indented >- block, several words to a line."""
    words = text.split(" ")
    return ">-\n" + "".join("  " + " ".join(words[i:i + words_per_line]) + "\n"
                            for i in range(0, len(words), words_per_line))


class SkillCheckTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="project starter skills ")
        self.addCleanup(temp.cleanup)
        base = Path(temp.name).resolve()
        self.repo = base / "adopter"
        # The bundle is the fixture: tests never depend on an adopter's documents.
        shutil.copytree(SOURCE, self.repo, ignore=shutil.ignore_patterns("__pycache__", ".cache"))
        tools = base / "tools"
        tools.mkdir()
        for name, target in (("python3", sys.executable), ("git", shutil.which("git"))):
            (tools / name).symlink_to(target)
        (tools / "shellcheck").write_text("#!/bin/sh\n")
        (tools / "shellcheck").chmod(0o755)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "GITHUB_"))}
        self.env.update(PATH=str(tools), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        HOME=str(base / "home"), PYTHONDONTWRITEBYTECODE="1")
        self.git("init", "-b", "main")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, env=self.env, check=True, capture_output=True)

    def check(self, *args):
        return subprocess.run(["bin/check", *args], cwd=self.repo, env=self.env, text=True, capture_output=True,
                              timeout=30)

    def skill(self, name, frontmatter, codex=None):
        """Write a skill whose SKILL.md has this frontmatter, and its agents/openai.yaml when given."""
        folder = self.repo / ".agents/skills" / name
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text("---\n" + frontmatter + "---\n\n# Skill\n" if frontmatter is not None
                                         else "# Skill\n")
        if codex is not None:
            (folder / "agents").mkdir()
            (folder / "agents/openai.yaml").write_text(codex)

    def test_skills_that_runtimes_read_correctly_pass(self):
        self.skill("plain", "name: plain\ndescription: Plain text, at https://example.com.  # a comment\n"
                            "disable-model-invocation: false\n")
        self.skill("quoted", "name: \"quoted\"\ndescription: 'It''s quoted: with a colon.'\n"
                             "disable-model-invocation: false # implicit\nargument-hint: \"[name ...]\"\n")
        # Only the checked fields' values are read, so a list or map elsewhere is no error.
        self.skill("folded", "name: folded\ndescription: " + folded(LONGEST) + "disable-model-invocation: false\n"
                             "allowed-tools:\n- Bash\n- Read\nuser-invocable: true\nmetadata:\n  owner: [a, b]\n"
                             "  notes: |\n    Anything: at all.\n")
        self.assertGreater(len((self.repo / ".agents/skills/folded/SKILL.md").read_text()), 1024)
        self.skill("literal", "name: literal\ndescription: |\n  Line one.\n\n  Line two.\n"
                              "disable-model-invocation: false\n",
                   codex="policy:\n  allow_implicit_invocation: true\n")
        self.skill("explicit", "name: explicit\ndescription: >\n  Only when invoked.\ndisable-model-invocation: true\n",
                   codex='interface:\n  display_name: "Explicit"\npolicy:\n  # Codex ignores the frontmatter field.\n'
                         "  allow_implicit_invocation: false\n")
        # A guide beside SKILL.md is no skill, and a linked skill folder belongs to the repository it points into.
        (self.repo / ".agents/skills/folded/references").mkdir()
        (self.repo / ".agents/skills/folded/references/guide.md").write_text("# Guide\n")
        (self.repo / ".agents/skills/linked").symlink_to("/nonexistent/vps-infra/.agents/skills/linked")
        self.git("add", "-A")
        result = self.check("--documents-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_each_broken_rule_fails_naming_the_skill_and_the_rule(self):
        valid = "description: A skill.\ndisable-model-invocation: false\n"
        explicit = "description: A skill.\ndisable-model-invocation: true\n"
        self.skill("misnamed", "name: other\n" + valid)
        self.skill("empty-description", "name: empty-description\ndescription: \"\"\ndisable-model-invocation: false\n")
        self.skill("no-description", "name: no-description\ndisable-model-invocation: false\n")
        self.skill("long-description", "name: long-description\ndescription: " + folded(LONGEST + "!")
                   + "disable-model-invocation: false\n")
        self.skill("no-flag", "name: no-flag\ndescription: A skill.\n")
        self.skill("yes-flag", "name: yes-flag\ndescription: A skill.\ndisable-model-invocation: yes\n")
        self.skill("underscored", "name: underscored\n" + valid + "user_invocable: true\ndisable_model_invocation: "
                   "false\nargument_hint: \"[name]\"\nallowed_tools: Bash\nargument: Optional names\n")
        self.skill("explicit-only", "name: explicit-only\n" + explicit)
        self.skill("explicit-implicit", "name: explicit-implicit\n" + explicit,
                   codex="policy:\n  allow_implicit_invocation: true\n")
        self.skill("policy-only", "name: policy-only\n" + valid, codex="policy:\n  allow_implicit_invocation: false\n")
        self.skill("no-frontmatter", None)
        self.skill("colon", "name: colon\ndescription: Use this: when asked.\ndisable-model-invocation: false\n")
        self.skill("duplicate", "name: duplicate\nname: duplicate\n" + valid)
        result = self.check("--documents-only")
        self.assertEqual(result.returncode, 1, result.stderr)
        problems = {
            "misnamed": ["name must be misnamed, its folder's name"],
            "empty-description": ["description must not be empty"],
            "no-description": ["description must not be empty"],
            "long-description": ["description is 1,025 characters; the Agent Skills limit is 1,024"],
            "no-flag": ["disable-model-invocation must be true or false"],
            "yes-flag": ["disable-model-invocation must be true or false"],
            "underscored": [wrong + " is a spelling no runtime reads; use " + right for wrong, right in (
                ("user_invocable", "user-invocable"), ("disable_model_invocation", "disable-model-invocation"),
                ("argument_hint", "argument-hint"), ("allowed_tools", "allowed-tools"),
                ("argument", "argument-hint"))],
            "explicit-only": ["disable-model-invocation is true, so agents/openai.yaml must set "
                              "policy.allow_implicit_invocation: false; Codex ignores the frontmatter field"],
            "policy-only": ["agents/openai.yaml sets policy.allow_implicit_invocation: false, so "
                            "disable-model-invocation must be true"],
            "no-frontmatter": ["missing frontmatter"],
            "colon": ["description is not a plain YAML string; quote it or fold it with >-"],
            "duplicate": ["duplicate frontmatter field: name"],
        }
        problems["explicit-implicit"] = problems["explicit-only"]
        expected = {".agents/skills/" + name + "/SKILL.md: " + problem
                    for name, messages in problems.items() for problem in messages}
        self.assertEqual(set(result.stderr.splitlines()), expected)

    def test_every_mode_fails_on_a_broken_skill(self):
        self.skill("sync-fleet", "name: sync-fleet\ndescription: A skill.\nuser_invocable: true\n"
                                 "disable-model-invocation: false\n")
        for args in (("--documents-only",), (), ("--full",)):
            with self.subTest(args=args):
                result = self.check(*args)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(".agents/skills/sync-fleet/SKILL.md: user_invocable is a spelling no runtime reads; "
                              "use user-invocable", result.stderr)


if __name__ == "__main__":
    unittest.main()

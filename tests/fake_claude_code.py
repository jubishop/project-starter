"""Stand in for Claude Code's print mode against the local API that the memory audit's boundary check serves.

Like Claude Code 2.1.312, it runs a Bash command only when an allow rule matches and a Read only inside the
working directory, denying the rest, and scrub mode withholds secret-named variables and XDG_CACHE_HOME from
its tools. ~/claude-code.json can make it break one of those promises, as a later release might:
ignoreScrub, withhold (variable names), allowCommands (first words), and readAnywhere.
"""

import fnmatch
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request


def ask(env, messages, tools):
    """Send one streaming Messages API request and return the response's content blocks."""
    request = urllib.request.Request(
        env["ANTHROPIC_BASE_URL"] + "/v1/messages?beta=true",
        json.dumps({"model": "fake", "stream": True, "messages": messages, "tools": tools}).encode(),
        {"content-type": "application/json", "x-api-key": env["ANTHROPIC_API_KEY"]})
    blocks = []
    with urllib.request.urlopen(request, timeout=30) as response:
        for line in response.read().decode().splitlines():
            event = json.loads(line[6:]) if line.startswith("data: ") else {}
            if event.get("type") == "content_block_start":
                blocks.append(event["content_block"] | {"partial": ""})
            elif event.get("type") == "content_block_delta":
                delta = event["delta"]
                if delta["type"] == "input_json_delta":
                    blocks[-1]["partial"] += delta["partial_json"]
                elif delta["type"] == "text_delta":
                    blocks[-1]["text"] += delta["text"]
    for block in blocks:
        partial = block.pop("partial")
        if block["type"] == "tool_use":
            block["input"] = json.loads(partial or "{}")
    return blocks


def run_tool(use, allow, tool_env, behavior):
    name, arguments = use["name"], use["input"]
    output, error = "Permission for this tool use was denied.", True
    if name == "Bash":
        command = arguments["command"]
        if any(fnmatch.fnmatchcase(command, rule[5:-1]) for rule in allow if rule.startswith("Bash(")) \
                or command.split()[0] in behavior.get("allowCommands", []):
            result = subprocess.run(command, shell=True, env=tool_env, capture_output=True, text=True)
            output, error = result.stdout + result.stderr, bool(result.returncode)
    elif name == "Read":
        path = Path(arguments["file_path"]).resolve()
        if path.is_relative_to(Path.cwd().resolve()) or behavior.get("readAnywhere"):
            output, error = path.read_text(), False
    return {"type": "tool_result", "tool_use_id": use["id"], "content": output, "is_error": error}


def main():
    args = sys.argv[1:]
    sys.stdin.read()
    settings = Path.home() / "claude-code.json"
    behavior = json.loads(settings.read_text()) if settings.exists() else {}
    with (Path.home() / "boundary-calls.jsonl").open("a") as calls:
        calls.write(json.dumps({"args": args, "env": dict(os.environ)}) + "\n")
    allow = json.loads(args[args.index("--settings") + 1])["permissions"]["allow"]
    schema = json.loads(args[args.index("--json-schema") + 1])
    env = dict(os.environ)
    tool_env = dict(env)
    if env.get("CLAUDE_CODE_SUBPROCESS_ENV_SCRUB") == "1" and not behavior.get("ignoreScrub"):
        tool_env = {key: value for key, value in env.items()
                    if not key.endswith("_API_KEY") and key != "XDG_CACHE_HOME"}
    for name in behavior.get("withhold", []):
        tool_env.pop(name, None)
    tools = [{"name": name, "input_schema": {"type": "object"}} for name in ("Bash", "Glob", "Grep", "Read")]
    tools.append({"name": "StructuredOutput", "input_schema": schema})
    messages = [{"role": "user", "content": "Audit"}]
    print(json.dumps({"type": "system", "subtype": "init", "claude_code_version": "9.9.9"}), flush=True)
    while True:
        blocks = ask(env, messages, tools)
        print(json.dumps({"type": "assistant", "message": {"content": blocks}}), flush=True)
        uses = [block for block in blocks if block["type"] == "tool_use"]
        final = next((use for use in uses if use["name"] == "StructuredOutput"), None)
        if final or not uses:
            print(json.dumps({"type": "result", "subtype": "success",
                              "structured_output": final and final["input"]}), flush=True)
            return
        results = [run_tool(use, allow, tool_env, behavior) for use in uses]
        print(json.dumps({"type": "user", "message": {"content": results}}), flush=True)
        messages += [{"role": "assistant", "content": blocks}, {"role": "user", "content": results}]


if __name__ == "__main__":
    main()

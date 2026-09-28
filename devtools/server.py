#!/usr/bin/env python3
"""Minimal stdio MCP server exposing a developer toolchain over a persistent workspace."""
import json
import os
import subprocess
import sys

WORKSPACE = os.environ.get("WORKSPACE", "/workspace")

TOOLS = [
    {
        "name": "run_command",
        "description": "Run a shell command in the workspace. Use for git, python, pytest, npm, ls, grep.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to run"},
                "cwd": {"type": "string", "description": "Directory relative to the workspace root"},
                "timeout": {"type": "number", "description": "Seconds before the command is killed (default 300)"},
            },
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": "Read a file from the workspace with line numbers.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a file in the workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace an exact string in a file. old_string must appear exactly once.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_string": {"type": "string"},
                "new_string": {"type": "string"},
            },
            "required": ["path", "old_string", "new_string"],
        },
    },
]


def resolve(path):
    full = os.path.realpath(os.path.join(WORKSPACE, path))
    if not full.startswith(os.path.realpath(WORKSPACE)):
        raise ValueError(f"path escapes the workspace: {path}")
    return full


def run_command(args):
    cwd = resolve(args.get("cwd", "."))
    os.makedirs(cwd, exist_ok=True)
    p = subprocess.run(
        args["command"], shell=True, cwd=cwd, capture_output=True, text=True,
        timeout=args.get("timeout", 300),
    )
    out = f"exit={p.returncode}\n"
    if p.stdout:
        out += f"--- stdout ---\n{p.stdout[-20000:]}\n"
    if p.stderr:
        out += f"--- stderr ---\n{p.stderr[-8000:]}\n"
    return out


def read_file(args):
    with open(resolve(args["path"])) as f:
        return "".join(f"{i:6d}\t{l}" for i, l in enumerate(f, 1))[:40000]


def write_file(args):
    full = resolve(args["path"])
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(args["content"])
    return f"wrote {len(args['content'])} bytes to {args['path']}"


def edit_file(args):
    full = resolve(args["path"])
    s = open(full).read()
    n = s.count(args["old_string"])
    if n == 0:
        return "ERROR: old_string not found. Read the file and match exactly."
    if n > 1:
        return f"ERROR: old_string appears {n} times, must be unique. Add surrounding context."
    open(full, "w").write(s.replace(args["old_string"], args["new_string"]))
    return f"edited {args['path']}"


HANDLERS = {"run_command": run_command, "read_file": read_file,
            "write_file": write_file, "edit_file": edit_file}


def reply(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main():
    os.makedirs(WORKSPACE, exist_ok=True)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        method, rid = req.get("method"), req.get("id")
        if method == "initialize":
            reply({"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "devtools", "version": "0.1.0"}}})
        elif method == "tools/list":
            reply({"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            name = req["params"]["name"]
            try:
                text = HANDLERS[name](req["params"].get("arguments", {}))
                err = False
            except Exception as e:
                text, err = f"{type(e).__name__}: {e}", True
            reply({"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": text}], "isError": err}})
        elif rid is not None:
            reply({"jsonrpc": "2.0", "id": rid,
                   "error": {"code": -32601, "message": f"unknown method {method}"}})


if __name__ == "__main__":
    main()

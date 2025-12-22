from __future__ import annotations

import json
import os
import subprocess
import sys
from json import JSONDecodeError
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonpatch
import jsonschema


JSONValue = Any


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]


def _repo_root() -> Path:
    # Allow overriding for tests/embedding, but default to CWD.
    return Path(os.environ.get("N8N_LAB_ROOT", Path.cwd())).resolve()


def _workflows_dir(root: Path) -> Path:
    return root / "workflows"


def _schemas_dir(root: Path) -> Path:
    return root / "schemas"


def _schema_path(root: Path) -> Path:
    return _schemas_dir(root) / "n8n-workflow.schema.json"


def _load_schema(root: Path) -> dict[str, Any]:
    with _schema_path(root).open("r", encoding="utf-8") as f:
        return json.load(f)


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )


def _git_config_get(key: str, cwd: Path) -> str | None:
    res = _run_git(["config", "--get", key], cwd=cwd)
    if res.returncode != 0:
        return None
    value = res.stdout.strip()
    return value or None


def _resolve_human_coauthor(cwd: Path) -> str | None:
    """
    Resolve the human co-author line value in the format: 'Name <email>'.

    Priority:
    1) N8N_HUMAN_COAUTHOR env var (already in the correct format)
    2) git config user.name + user.email
    """
    env_value = os.environ.get("N8N_HUMAN_COAUTHOR")
    if env_value and "<" in env_value and ">" in env_value:
        return env_value.strip()

    name = _git_config_get("user.name", cwd=cwd)
    email = _git_config_get("user.email", cwd=cwd)
    if name and email:
        return f"{name} <{email}>"

    return None


def _with_coauthors(message: str, cwd: Path) -> str:
    human = _resolve_human_coauthor(cwd=cwd)
    if not human:
        raise ValueError(
            "Missing human co-author identity. Set N8N_HUMAN_COAUTHOR='Name <email>' "
            "or configure git user.name and user.email."
        )

    # Always include both trailers.
    trailers = [
        f"Co-authored-by: {human}",
        "Co-authored-by: Cursor <claude@users.noreply.github.com>",
    ]
    return message.rstrip() + "\n\n" + "\n".join(trailers) + "\n"


def _require_glob_scoped_workflows(paths: list[str]) -> None:
    for p in paths:
        if not p.startswith("workflows/") or not p.endswith(".json") or "/" in p[len("workflows/") :].strip("/"):
            # Enforce `workflows/*.json` (no nested dirs).
            raise ValueError("Only paths matching 'workflows/*.json' are allowed.")


def _workflow_path(root: Path, slug: str) -> Path:
    if "/" in slug or slug.strip() != slug or slug == "":
        raise ValueError("Invalid slug.")
    return _workflows_dir(root) / f"{slug}.json"


def _read_json_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_file(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(_canonical_json(obj))


def _validate_workflow(root: Path, wf: Any) -> list[str]:
    schema = _load_schema(root)
    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(wf), key=lambda e: list(e.path))
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]


def tool_specs() -> list[ToolSpec]:
    return [
        ToolSpec(
            name="workflow_list",
            description="List workflow slugs found in workflows/*.json.",
            input_schema={"type": "object", "properties": {}, "additionalProperties": False},
        ),
        ToolSpec(
            name="workflow_get",
            description="Get a workflow JSON by slug (workflows/<slug>.json).",
            input_schema={
                "type": "object",
                "properties": {"slug": {"type": "string"}},
                "required": ["slug"],
                "additionalProperties": False,
            },
        ),
        ToolSpec(
            name="workflow_create",
            description="Create a new workflow file from a minimal template.",
            input_schema={
                "type": "object",
                "properties": {
                    "slug": {"type": "string"},
                    "name": {"type": "string"},
                },
                "required": ["slug", "name"],
                "additionalProperties": False,
            },
        ),
        ToolSpec(
            name="workflow_update",
            description="Replace the workflow JSON for a slug (validates and formats).",
            input_schema={
                "type": "object",
                "properties": {
                    "slug": {"type": "string"},
                    "workflow": {"type": "object"},
                },
                "required": ["slug", "workflow"],
                "additionalProperties": False,
            },
        ),
        ToolSpec(
            name="workflow_patch",
            description="Apply RFC6902 JSON Patch operations to a workflow (validates and formats).",
            input_schema={
                "type": "object",
                "properties": {
                    "slug": {"type": "string"},
                    "patch": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["slug", "patch"],
                "additionalProperties": False,
            },
        ),
        ToolSpec(
            name="workflow_delete",
            description="Delete a workflow JSON file by slug.",
            input_schema={
                "type": "object",
                "properties": {"slug": {"type": "string"}},
                "required": ["slug"],
                "additionalProperties": False,
            },
        ),
        ToolSpec(
            name="workflow_validate",
            description="Validate a workflow JSON file (parse + JSONSchema) and return errors.",
            input_schema={
                "type": "object",
                "properties": {"slug": {"type": "string"}},
                "required": ["slug"],
                "additionalProperties": False,
            },
        ),
        ToolSpec(
            name="workflow_format",
            description="Rewrite a workflow JSON file in canonical formatting (sort keys, 2-space indent).",
            input_schema={
                "type": "object",
                "properties": {"slug": {"type": "string"}},
                "required": ["slug"],
                "additionalProperties": False,
            },
        ),
        ToolSpec(
            name="git_checkout_branch",
            description="Checkout (or create) a git branch.",
            input_schema={
                "type": "object",
                "properties": {"branch": {"type": "string"}},
                "required": ["branch"],
                "additionalProperties": False,
            },
        ),
        ToolSpec(
            name="git_status_scoped",
            description="Show git status, optionally scoped to a path prefix (e.g. workflows/).",
            input_schema={
                "type": "object",
                "properties": {"prefix": {"type": "string"}},
                "additionalProperties": False,
            },
        ),
        ToolSpec(
            name="git_commit_scoped",
            description="Stage and commit changes for specific paths. Enforces workflows/*.json when in workflows branch.",
            input_schema={
                "type": "object",
                "properties": {
                    "paths": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "message": {"type": "string", "minLength": 1},
                },
                "required": ["paths", "message"],
                "additionalProperties": False,
            },
        ),
        ToolSpec(
            name="git_revert",
            description="Revert a commit SHA (or HEAD if omitted).",
            input_schema={
                "type": "object",
                "properties": {"ref": {"type": "string"}},
                "additionalProperties": False,
            },
        ),
    ]


def _tool_result(content: Any) -> dict[str, Any]:
    # MCP expects { content: [{type:'text', text:'...'}] } or similar.
    return {"content": [{"type": "text", "text": json.dumps(content, ensure_ascii=False, indent=2)}]}


def _error_result(message: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": message}], "isError": True}


def _handle_tool_call(name: str, args: dict[str, Any]) -> dict[str, Any]:
    root = _repo_root()

    try:
        if name == "workflow_list":
            wdir = _workflows_dir(root)
            wdir.mkdir(parents=True, exist_ok=True)
            slugs = sorted(p.stem for p in wdir.glob("*.json") if p.is_file())
            return _tool_result({"slugs": slugs})

        if name == "workflow_get":
            path = _workflow_path(root, args["slug"])
            wf = _read_json_file(path)
            return _tool_result({"workflow": wf})

        if name == "workflow_create":
            slug = args["slug"]
            path = _workflow_path(root, slug)
            if path.exists():
                return _error_result(f"Workflow already exists: {path}")
            wf = {"name": args["name"], "nodes": [], "connections": {}, "settings": {}}
            errors = _validate_workflow(root, wf)
            if errors:
                return _error_result("Template failed schema validation: " + "; ".join(errors))
            _write_json_file(path, wf)
            return _tool_result({"created": str(path)})

        if name == "workflow_update":
            slug = args["slug"]
            path = _workflow_path(root, slug)
            wf = args["workflow"]
            errors = _validate_workflow(root, wf)
            if errors:
                return _tool_result({"ok": False, "errors": errors})
            _write_json_file(path, wf)
            return _tool_result({"ok": True, "path": str(path)})

        if name == "workflow_patch":
            slug = args["slug"]
            path = _workflow_path(root, slug)
            wf = _read_json_file(path)
            patch_ops = args["patch"]
            new_wf = jsonpatch.apply_patch(wf, patch_ops, in_place=False)
            errors = _validate_workflow(root, new_wf)
            if errors:
                return _tool_result({"ok": False, "errors": errors})
            _write_json_file(path, new_wf)
            return _tool_result({"ok": True, "path": str(path)})

        if name == "workflow_delete":
            path = _workflow_path(root, args["slug"])
            if path.exists():
                path.unlink()
            return _tool_result({"deleted": str(path)})

        if name == "workflow_validate":
            path = _workflow_path(root, args["slug"])
            wf = _read_json_file(path)
            errors = _validate_workflow(root, wf)
            return _tool_result({"ok": len(errors) == 0, "errors": errors})

        if name == "workflow_format":
            path = _workflow_path(root, args["slug"])
            wf = _read_json_file(path)
            _write_json_file(path, wf)
            return _tool_result({"formatted": str(path)})

        if name == "git_checkout_branch":
            branch = args["branch"]
            # Try checkout; if missing, create.
            res = _run_git(["checkout", branch], cwd=root)
            if res.returncode != 0:
                res2 = _run_git(["checkout", "-b", branch], cwd=root)
                if res2.returncode != 0:
                    return _error_result(res2.stderr.strip() or res2.stdout.strip() or "git checkout failed")
            return _tool_result({"ok": True, "branch": branch})

        if name == "git_status_scoped":
            prefix = args.get("prefix", "")
            cmd = ["status", "--porcelain"]
            res = _run_git(cmd, cwd=root)
            if res.returncode != 0:
                return _error_result(res.stderr.strip() or "git status failed")
            lines = [ln for ln in res.stdout.splitlines() if ln.strip()]
            if prefix:
                lines = [ln for ln in lines if ln.endswith(prefix) or ln[3:].startswith(prefix)]
            return _tool_result({"status": lines})

        if name == "git_commit_scoped":
            paths: list[str] = args["paths"]
            message: str = args["message"]

            head = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=root)
            branch = head.stdout.strip() if head.returncode == 0 else ""
            if branch == "workflows":
                _require_glob_scoped_workflows(paths)

            add = _run_git(["add", "--", *paths], cwd=root)
            if add.returncode != 0:
                return _error_result(add.stderr.strip() or add.stdout.strip() or "git add failed")

            commit_message = _with_coauthors(message, cwd=root)
            commit = _run_git(["commit", "-m", commit_message], cwd=root)
            if commit.returncode != 0:
                # If there is nothing to commit, treat as ok but return message.
                out = (commit.stderr + "\n" + commit.stdout).strip()
                return _tool_result({"ok": False, "message": out})

            return _tool_result({"ok": True, "message": message})

        if name == "git_revert":
            ref = args.get("ref") or "HEAD"
            res = _run_git(["revert", "--no-edit", ref], cwd=root)
            if res.returncode != 0:
                return _error_result(res.stderr.strip() or res.stdout.strip() or "git revert failed")
            return _tool_result({"ok": True, "ref": ref})

        return _error_result(f"Unknown tool: {name}")
    except Exception as e:  # noqa: BLE001
        return _error_result(str(e))


def _mcp_tools_list() -> dict[str, Any]:
    return {
        "tools": [
            {
                "name": s.name,
                "description": s.description,
                "inputSchema": s.input_schema,
            }
            for s in tool_specs()
        ]
    }


def _mcp_initialize_result(client_params: dict[str, Any]) -> dict[str, Any]:
    """
    MCP handshake response.

    Cursor expects `serverInfo` to exist; otherwise it reports "No server info found".
    """
    protocol_version = client_params.get("protocolVersion") or "2024-11-05"
    return {
        "protocolVersion": protocol_version,
        "capabilities": {
            "tools": {
                "listChanged": False,
            }
        },
        "serverInfo": {
            "name": "n8n-workflows-mcp",
            "version": "0.1.0",
        },
    }


def _write_line(obj: dict[str, Any]) -> None:
    """
    Cursor's MCP runner expects line-delimited JSON on stdio.
    """
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except JSONDecodeError:
            _write_line({"jsonrpc": "2.0", "id": None, "error": {"message": "Invalid JSON"}})
            continue

        method = msg.get("method")
        msg_id = msg.get("id")
        params = msg.get("params") or {}

        # Notifications have no id; do not respond.
        if msg_id is None:
            continue

        if method == "initialize":
            result = _mcp_initialize_result(params)
        elif method == "tools/list":
            result = _mcp_tools_list()
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments") or {}
            if not isinstance(tool_name, str):
                result = _error_result("Missing tool name")
            else:
                result = _handle_tool_call(tool_name, tool_args)
        else:
            result = _error_result(f"Unsupported method: {method}")

        resp = {"jsonrpc": "2.0", "id": msg_id, "result": result}
        _write_line(resp)


if __name__ == "__main__":
    main()



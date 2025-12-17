# n8n Creative Lab (repo-first workflows)

This repo is designed to **develop n8n workflows as JSON files** using **Cursor** as the primary tool.

## Structure

- `workflows/`: versioned workflows (**only** `workflows/*.json` in the `workflows` branch)
- `agents/`: Cursor rules / agent prompts 
- `prompts/`: laboratory prompts
- `mcp/`: local MCP server in Python (`lab` branch)
- `schemas/`: JSONSchema(s) to validate workflows
- `docs/`: documentation and official links
- `kb/`: editable knowledge base (company + workflow style)

## Tooling

- Python: `uv`
- Task runner: Poe the Poet: `https://poethepoet.natn.io/`

## Operating principle

- Workflows are edited **via MCP tools** (CRUD/patch/validate/format) to avoid manual edits of large JSON blobs.
- Backup/rollback relies exclusively on **Git** (small commits + `git revert`).

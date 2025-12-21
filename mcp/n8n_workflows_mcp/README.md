# n8n workflows MCP (repo-first)

This MCP server provides **CRUD + validation + formatting + Git operations** for n8n workflow JSON files stored in `workflows/*.json`.

## Goals

- Avoid manual edits of large workflow JSON blobs
- Enforce repo policies:
  - `workflows` branch: only `workflows/*.json`
  - rollback via `git revert`
- Provide low-token summaries to the agent

## Running (local)

This project uses **uv** and **Poe the Poet**. Poe docs: `https://poethepoet.natn.io/`.

Planned tasks will be added under `[tool.poe.tasks]` in `pyproject.toml`.






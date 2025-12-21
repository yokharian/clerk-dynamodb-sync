# Branching policy (lab / prompts / workflows)

This repository separates responsibilities into **3 branches** to reduce diff noise, simplify reviews, and allow the agent to operate safely.

## Branches

- **`lab`**: lab tooling (MCP server, schemas, docs, kb, scripts).
- **`prompts`**: **only** laboratory prompts versions (`prompts/*.md`).
- **`workflows`**: **only** versions `workflows/*.json`.

## Mandatory rules

### `workflows` branch

- Only create/modify/delete files that match `workflows/*.json`.
- Do not commit any other paths (including `schemas/`, `docs/`, `agents/`, `kb/`, `mcp/`).
- The agent must use MCP Git tools to:
  - create/checkout the branch
  - `add` only `workflows/*.json`
  - create small commits (one intent per commit)
  - rollback via `git revert` when a change breaks validation/conventions

### `prompts` branch

- Only version `prompts/*.md`
- Prompt changes must be reviewable and stable: one policy change per commit.

### `lab` branch

- Lab code and docs: `mcp/`, `schemas/`, `docs/`, `kb/`.

## Rollback (backup = Git)

- **Default**: `git revert <sha>` (does not rewrite history).
- **Advanced (only by explicit request)**: `git reset --hard`.

## Commit trailers (mandatory)

All commits created by tooling must include both trailers:

- `Co-authored-by: <HumanName> <HumanEmail>`
- `Co-authored-by: Cursor <claude@users.noreply.github.com>`

## Commit message conventions (recommended)

- Workflows: `wf(<slug>): <summary>`
- Prompts: `prompts: <summary>`
- Lab: `lab: <summary>`

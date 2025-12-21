# Agents (global policies)

This document defines **mandatory rules** for generating and maintaining n8n workflows in this repo using Cursor.

## Guiding principle

- **Workflows must be managed via MCP tools**, not by manually editing large JSON blobs.
- **Backup/rollback relies exclusively on Git**: small commits + `git revert`.

## Branching policy (mandatory)

See [`docs/git-branching-policy.md`](../docs/git-branching-policy.md).

Operational summary:

- Workflow changes: **always** in `workflows` branch and **only** `workflows/*.json`.
- Laboratory prompts: **always** in `prompts` branch and **only** `prompts/*.md`..
- Lab changes (MCP server, schemas, docs, kb): `lab` branch.

## Project tooling (mandatory)

- **Python with uv**
- **Tasks with Poe the Poet**: official docs at [`https://poethepoet.natn.io/`](https://poethepoet.natn.io/)

## Agent hard rules

- Do not run ad-hoc `git add`/`git commit` if an MCP Git tool exists; use the MCP tool.
- In `workflows` branch, the agent may version **only** `workflows/*.json`.
- Every workflow change must:
  - pass JSON parsing
  - pass JSONSchema validation
  - be written in canonical format (clean diffs)
  - be committed with a small, clear message
- If a change makes a workflow invalid, the agent must rollback using `git revert`.
- Every `git commit` created by tools must include **both** commit trailers:
  - `Co-authored-by: <HumanName> <HumanEmail>`
  - `Co-authored-by: Cursor <claude@users.noreply.github.com>`

## Workflow authoring style (defaults)

- After the trigger, add an early node to define **global/static variables** (configurable).
- Prefer **JMESPath** where applicable for selection/transformation.
- Prefer **JSONSchema** to validate payloads/contracts.

## Recommended official sources (by topic)

Use these official sources before assuming behavior:

- **Workflows (concepts, connections, structure)**: [`https://docs.n8n.io/workflows/`](https://docs.n8n.io/workflows/)
- **Code / expressions / data**: [`https://docs.n8n.io/code/`](https://docs.n8n.io/code/)
- **Integrations / nodes**: [`https://docs.n8n.io/integrations/`](https://docs.n8n.io/integrations/)
- **API reference (version-dependent)**: [`https://docs.n8n.io/api-reference/`](https://docs.n8n.io/api-reference/)
- **Templates and examples**: [`https://n8n.io/workflows/`](https://n8n.io/workflows/)
- **Official repository (types/implementation)**: [`https://github.com/n8n-io/n8n`](https://github.com/n8n-io/n8n)
- **Community (not official, useful supporting source)**: [`https://community.n8n.io/`](https://community.n8n.io/)

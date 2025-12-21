# Workflow Author (editing guide)

## Goal

Create/update n8n workflows as JSON in `workflows/*.json` with incremental changes and readable diffs.

## Recommended flow

- Ensure you are on the `workflows` branch.
- Use MCP tools to:
  - create a workflow from a minimal template
  - apply small patches (JSON Patch)
  - validate/format
  - commit

## Per-change checklist

- JSON parse: OK
- JSONSchema: OK
- Conventions: OK
  - Trigger -> early global/static variables node
  - Prefer JMESPath and JSONSchema when applicable
- Commit message: `wf(<slug>): <summary>`



# Workflow style & strategic decisions (fill in)

This file captures **team conventions** and **strategic decisions** so workflow generation remains consistent.

## Strategic defaults (current)

- After every trigger, create an early node to define **global/static variables** that can be reused across the workflow.
- Prefer **JMESPath** when possible for data selection/transformation.
- Prefer **JSONSchema** when possible for validating payloads/contracts.

## Workflow structure conventions

- Trigger placement:
- Global/static variables node:
- Error handling:
- Retries/timeouts:
- Logging/auditing:

## Data handling conventions

- Preferred patterns for mapping/transforming data:
- Preferred patterns for validation (JSONSchema):
- Preferred patterns for filtering (JMESPath):

## Node naming conventions

- Prefixes/suffixes:
- Use of emojis: (yes/no)
- Use of environment tags:

## “Do not do” list

- Secrets in workflow JSON
- Large manual edits to workflow JSON blobs (use MCP patch tools)






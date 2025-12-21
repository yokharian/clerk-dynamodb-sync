# n8n workflow JSON data model (repo-first)

This document describes a **pragmatic** workflow JSON model for **repo-first** development:

- One file per workflow in `workflows/*.json`
- Validated on read/write via JSON parsing + JSONSchema
- Written in canonical formatting for clean diffs

It is intentionally **not** a full, strict re-implementation of n8n internals. Instead, it captures the stable structure we need for tooling.

## High-level mental model

An n8n workflow is a **directed graph**:

- **nodes**: steps (trigger, actions, transforms, conditionals, etc.)
- **connections**: edges between node outputs and node inputs
- **settings**: workflow-level execution settings

## Top-level workflow object (common fields)

Expected top-level shape:

- **name**: string, human-readable workflow name
- **nodes**: array of node objects
- **connections**: object describing edges between nodes
- **settings**: object of workflow settings

Common optional fields (version-dependent):

- **active**: boolean
- **meta**: object (UI/metadata)
- **tags**: array
- **versionId**: string
- **id**: string/number (if exported from a running instance)
- **createdAt / updatedAt**: timestamps
- **pinData / staticData**: auxiliary data (may exist depending on features)

## Node object (pragmatic)

Minimum fields we expect to exist or to be meaningfully present:

- **name**: string (unique within the workflow, used as the key in `connections`)
- **type**: string (node type identifier, e.g. trigger or integration node)
- **parameters**: object (node configuration; may be empty)
- **position**: array of two numbers (UI position)

Common optional fields:

- **typeVersion**: number
- **credentials**: object (references only; never store secrets)
- **disabled**: boolean
- **notesInFlow**: boolean
- **continueOnFail**: boolean
- **onError**: string

## Connections object (conceptual)

`connections` is typically an object keyed by **source node name**, where each value describes one or more outputs (often `main`) with arrays of target references.

The exact shape may vary by version, but conceptually it represents:

- source node output → list of target node inputs

Because this is version-dependent, our JSONSchema will validate **presence + basic types** without over-constraining the nested structure.

## Security rule: never store secrets

- Do not store credential secrets, tokens, passwords, or API keys inside workflow JSON.
- Workflows should only reference credentials by name/id as supported by n8n.

## Repo-first conventions (team defaults)

- Add an early node (right after the trigger) to define **global/static variables** for the workflow.
- Prefer **JMESPath** and **JSONSchema** where applicable.






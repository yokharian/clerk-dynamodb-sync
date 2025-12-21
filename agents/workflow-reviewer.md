# Workflow Reviewer (review guide)

## What to check first

- The change is on the correct branch (`workflows`) and touches only `workflows/*.json`.
- The workflow passes JSON + JSONSchema validation.
- The diff is small and communicates a single clear intent.

## Quality checklist

- Nodes have clear, consistent names.
- Error handling is defined (when applicable).
- Early global/static variables node after the trigger (team convention).
- Prefer JMESPath and JSONSchema when applicable.



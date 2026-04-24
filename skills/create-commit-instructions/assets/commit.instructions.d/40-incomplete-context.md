---

## BEHAVIOR WHEN CONTEXT IS INCOMPLETE

- If the diff is ambiguous, prefer the most **conservative accurate type**
  (e.g., `refactor` over `feat` when behavior did not clearly change).
- Do **not** invent features, bugs, or behaviors not supported by the visible diff.
- Base the message **only** on the staged changes or the diff provided.
- Prefer **clarity and correctness** over clever or creative wording.
- API changes, default value changes, persisted data/schema changes, generated
  artifact changes, and integration contract changes are usually behavior
  changes - not `chore`.
- If only comments, formatting, or import/include order changed, prefer `docs`,
  `style`, or `chore` over `refactor`.

---

## ALLOWED TYPES

| Type       | When to use                                                         |
| ---------- | ------------------------------------------------------------------- |
| `feat`     | New user-visible behavior, API, command, capability, or feature     |
| `fix`      | A bug fix in production behavior, integration, state, or tooling    |
| `docs`     | Documentation-only changes - no code change                         |
| `style`    | Formatting or whitespace changes that do not affect logic           |
| `refactor` | Internal restructuring with no intended behavior change             |
| `perf`     | A code change that improves speed, memory use, or resource use      |
| `test`     | Adding or modifying tests; no production code change                |
| `build`    | Build system, dependency, packaging, or generated artifact changes  |
| `ci`       | CI/CD pipeline, workflow, or automation changes                     |
| `chore`    | Maintenance work that does not modify production or test behavior   |
| `revert`   | Reverting a previous commit                                         |

**Selection rule:** pick the single most accurate type for the dominant
intent of the staged diff. When in doubt, prefer the more conservative
accurate type over an optimistic one. If the change affects public behavior,
compatibility, persisted data, generated outputs, or integration contracts, do
not use `chore`.

---

## GRAMMAR AND FORMATTING RULES

- **Tense:** Imperative, present tense only. Write `add validation` not
  `added validation` or `adds validation`.
- **Case:** The description must begin with a lowercase letter.
- **Period:** No trailing period on the subject line.
- **Length:** Subject line must be 72 characters or fewer. Aim for 50 or fewer.
- **Clarity:** Every subject line must convey a clear, specific intent. Vague
  descriptions are not acceptable.
- **Scope specificity:** When a scope is used, it must name a real module,
  subsystem, package, command, or file area - never a generic term.
- **Code fences:** Do not wrap the commit message in a markdown code block.
- **Multiple files:** When many files changed, summarize the **main intent** of
  the commit, not every file.

---

## BREAKING CHANGES

Signal a breaking change in **at least one** of the following ways (both may be used simultaneously):

1. Append `!` immediately after the type/scope on the subject line:

   ```text
   feat(api)!: rename response fields
   ```

2. Include a `BREAKING CHANGE:` footer that describes what broke and how to migrate:

   ```text
   BREAKING CHANGE: clients must read the new response field names.
   ```

Use both when the breakage needs to be visible in both the short log and the detailed log.

---

## BODY (optional)

- Separate from the subject with exactly one blank line.
- Explain the **motivation** - WHAT changed and WHY, not HOW.
- Contrast before vs. after behavior where helpful, especially for public
  behavior, compatibility, data formats, performance, or operational impact.
- Wrap lines at 72 characters.
- Use `*` bullet points for listing multiple distinct points.

---

## FOOTERS (optional)

- Separate from the body (or subject, if no body) with exactly one blank line.
- Format: `<Token>: <value>` or `<Token> #<value>` for issue references.
- Valid tokens in this repo: `BREAKING CHANGE`, `Closes`, `Refs`,
  `Reviewed-by`, `Assisted-by`.
- When AI assistance is present, use the exact footer format
  `Assisted-by: AGENT_NAME:MODEL_VERSION`.
- Do not add `Co-authored-by` for an AI assistant.

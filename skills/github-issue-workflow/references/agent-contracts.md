# Agent Contracts and Focused Handoffs

Use this reference when spawning agents. Start each **new** agent in a clean context. Pass links, paths, acceptance criteria, and concise findings instead of copying entire source trees or lengthy logs. Include repository location, baseline SHA, scope, pre-existing changes to protect, file ownership, and a no-checks reminder. Do not expose private secrets.

## Shared compact handoff

- GitHub issue URL and short requirement summary; relevant acceptance criteria.
- Fixed baseline SHA and noteworthy pre-existing user changes.
- Relevant repository conventions and paths (not full file contents).
- Assigned deliverable and owned files/interfaces; dependency assumptions.
- Explicit constraint: **do not run tests, builds, lint, or static analysis** during implementation, review, or review remediation.
- Return changed paths, key decisions, known risks, and status, normally within 200–400 words.

## Three parallel implementation agents

**Code:** Implement production behavior, honor the repository architecture, preserve compatibility where required, avoid unrelated changes. Do not write documentation or tests unless coordination requires a shared interface tweak; communicate contract changes.

**Tests:** Independently derive tests from issue acceptance criteria; cover edge cases and regressions; write tests but never execute them. Coordinate only on externally visible interfaces, and avoid altering production code.

**Documentation:** Update pertinent user/developer docs and examples. Confirm descriptions match the intended public behavior; do not modify production code or tests.

All three are launched concurrently. Prefer distinct file ownership. When overlap is unavoidable, the orchestrator resolves it after all three finish.

## Review agent

Explicitly invoke Matt Pocock's installed `code-review` skill using the phrase: **"review the changes since [baseline SHA]"** and the exact **Standards** and **Spec** axes. The skill runs those reviews in parallel subagents; don't replace it. Return side-by-side findings with evidence, severity, paths/lines, and a concise consolidated fix queue. Review relevant new/untracked files too.

## Review-fix agent

One agent with a fresh context, actual review findings, relevant source paths, and high-effort model selection. Validate each finding conceptually, fix valid ones, update affected tests/docs, and justify any dismissal. Do not run checks.

## Test-fix agent

Only if checks fail. Pass precise failed commands, exit codes, diagnostic excerpts, paths to logs, and relevant changed files. Fix root causes; do not disable useful checks or weaken valid assertions. The orchestrator, not this agent, performs official staged revalidation.

## Final response format

- Implementation: completed behavior and major affected files.
- Review: Standards vs Spec findings and resolutions.
- Validation: exact commands and results; clearly mark unrun checks.
- Commit: hash, Conventional Commit subject (if successful), or reason not committed.
- Remaining issues: only concrete blockers or risks.

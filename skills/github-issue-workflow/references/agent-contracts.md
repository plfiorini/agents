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

### Complexity and model configuration

During Plan Mode, the main orchestrator classifies the issue:

- **Simple:** Localized changes, straightforward behavior, limited dependencies.
- **Standard:** Multiple related changes, moderate logic, or meaningful regression risk.
- **Complex:** Architectural changes, concurrency, advanced DSP, numerical algorithms, realtime constraints, or substantial cross-module interactions.

Default to **Standard** when uncertain. Record the complexity, a short rationale, and the requested model and reasoning effort for Code, Tests, and Documentation in the Implementation Brief. Select settings without requesting separate user approval.

Default model assignments:

| Agent | Claude Code | Codex |
| --- | --- | --- |
| Code | Sonnet 5.5 | GPT-6.1 Sol |
| Tests | Sonnet 5.5 | GPT-6.1 Sol |
| Documentation | Haiku 5.5 | GPT-6 Luna |

Default reasoning effort by complexity, for both hosts where supported:

| Complexity | Code | Tests | Documentation |
| --- | --- | --- | --- |
| Simple | Medium | Medium | Low |
| Standard | High | Medium | Low |
| Complex | High | High | Medium |

Resolve model and effort independently for each role: **explicit per-role settings in the invoking request → explicit per-role host settings → the defaults above**. Use existing host configuration mechanisms; introduce no skill-specific configuration file. Overrides apply only to these three implementation agents.

Before launching all three concurrently:

1. Inspect the runtime's supported models, effort levels, and launch controls. The table uses display names; translate them only to identifiers verified in the runtime. Never invent model identifiers or configuration parameters.
2. Set model and effort explicitly when supported while retaining clean, isolated contexts. If an override requires a different context mechanism, use the runtime's supported clean-context mechanism rather than inheriting a broad main-session history.
3. If a requested model or effort is unavailable, use the closest suitable supported alternative that maintains quality for the assigned role and complexity. Prefer a comparable model for the role and a supported effort at least as high as requested when available. If effort cannot be configured, use the runtime default and disclose the limitation.
4. Report requested and actual settings, the fallback reason, and any setting the runtime does not expose or cannot verify. Never silently claim a requested model or effort was used. Include a compact per-role configuration summary in the launch handoff and final report; this does not require an additional approval gate.

Model selection preserves exactly **three parallel implementation agents**, their responsibilities, and full required coverage. Keep role context focused and handoffs concise; reuse verified planning findings instead of repeating broad exploration. Matt Pocock's `code-review` skill controls its own internal model selection. Review-fix and test-fix agents retain the separate High-effort assignments and unavailable-configuration policy in [validation.md](validation.md).

### Responsibilities

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

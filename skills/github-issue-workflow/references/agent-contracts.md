# Agent Contracts and Focused Handoffs

Use this reference when spawning agents. Start each **new** agent in a clean context. Pass links, paths, acceptance criteria, and concise findings instead of copying entire source trees or lengthy logs. Include repository location, baseline SHA, scope, pre-existing changes to protect, file ownership, and a no-checks reminder. Do not expose private secrets.

## Shared compact handoff

- GitHub issue URL and short requirement summary; relevant acceptance criteria.
- Fixed baseline SHA and noteworthy pre-existing user changes.
- Relevant repository conventions and paths (not full file contents).
- Assigned deliverable and owned files/interfaces; dependency assumptions.
- Explicit constraint: **do not run tests, builds, lint, or static analysis** during implementation, review, or review remediation.
- Return changed paths, key decisions, known risks, and status, normally within 200–400 words.

## Complexity and model configuration

During Plan Mode, the main orchestrator classifies the issue:

- **Simple:** Localized changes, straightforward logic, minimal dependencies.
- **Standard:** Multiple related changes, moderate complexity, or meaningful regression risk.
- **Complex:** Architectural changes, concurrency, advanced DSP, numerical algorithms, realtime processing, or significant cross-module interactions.

Default to **Standard** when uncertain. Record complexity and rationale, detected runtime, preferred families and requested efforts for implementation and remediation, review delegation, and the resolution/fallback policy in the Implementation Brief. Any runtime-verified configuration can be recorded provisionally; resolve again at creation time. Model selection needs no separate approval gate.

### Model-family preferences

These are logical preferences, never literal launch identifiers or pinned versions:

| Agent | Claude Code | Codex |
| --- | --- | --- |
| Code | Latest available Sonnet | Latest available Sol |
| Tests | Latest available Sonnet | Latest available Sol |
| Documentation | Latest available Haiku | Latest available Luna |
| Code Review | Managed by code-review skill | Managed by code-review skill |
| Review Remediation | Latest available Sonnet | Latest available Sol |
| Test Remediation | Latest available Sonnet | Latest available Sol |

Requested reasoning effort, where supported:

| Complexity | Code | Tests | Documentation |
| --- | --- | --- | --- |
| Simple | Medium | Medium | Low |
| Standard | High | Medium | Low |
| Complex | High | High | Medium |

Review-remediation and test-remediation agents **always request High effort**, independently of complexity. Complexity affects only model configuration and effort; it never changes the required three implementation agents or their responsibilities and coverage.

### Dynamic resolution at agent creation

Apply this procedure to every implementation and remediation launch. For the review wrapper, leave model/effort at supported runtime defaults and delegate review model selection to Matt Pocock's `code-review` skill; do not override its internal agent configuration.

1. Detect Claude Code or Codex from the active runtime and its exposed tools/configuration. Inspect supported launch controls, model catalog, alias semantics, and effort levels. Reuse runtime information already available; avoid web searches when it suffices.
2. Resolve the role's preferred family using native runtime configuration. Prefer a version-independent alias **only when the runtime documents that it selects the latest available compatible family member**. An unversioned name alone does not establish this behavior.
3. Otherwise, select the newest compatible family member from the runtime's available catalog, using its release/version metadata or documented ordering. Use only verified identifiers. Never hardcode versions in this skill, invent aliases/parameters, or infer release order from display names without evidence. If latest status cannot be established, disclose that uncertainty and use a suitable supported option without claiming it is newest.
4. If the preferred family is unavailable, select a suitable supported fallback for the role and complexity. Preserve quality and required coverage; report the reason and actual selected model. Do not silently substitute.
5. Apply requested effort only through supported controls and accepted values. If the exact level is unavailable, prefer a supported level at least as high when available; otherwise use the supported default and disclose the limitation. If explicit model selection is unavailable, use runtime defaults and report that limitation rather than adding an approval gate.
6. Retain a fresh isolated context for each new agent. In Codex, when the exposed tool requires it for model/effort overrides, use `fork_turns="none"` and provide a focused handoff. In other runtimes, use their supported clean-context mechanism. Never invent an equivalent parameter.
7. Record requested family/effort, actual model/effort, resolution source, fallback reason, and any unsupported or unverifiable setting in the launch summary and final report. When runtime defaults do not expose the actual identifier or effort, mark it unknown; do not claim a requested configuration was used.

Use existing runtime mechanisms only; add no lookup scripts, dependencies, or custom configuration files. Resolve at each new creation, reusing catalog information while still current. When reusing an existing agent, retain and report its actual configuration rather than claiming a new selection. Explicit user configuration takes precedence; report any departure from these preferences. Runtime configuration constrains what is available and configurable.

## Three parallel implementation agents

### Responsibilities

**Code:** Implement production behavior, honor the repository architecture, preserve compatibility where required, avoid unrelated changes. Do not write documentation or tests unless coordination requires a shared interface tweak; communicate contract changes.

**Tests:** Independently derive tests from issue acceptance criteria; cover edge cases and regressions; write tests but never execute them. Coordinate only on externally visible interfaces, and avoid altering production code.

**Documentation:** Update pertinent user/developer docs and examples. Confirm descriptions match the intended public behavior; do not modify production code or tests.

All three are launched concurrently. Prefer distinct file ownership. When overlap is unavoidable, the orchestrator resolves it after all three finish.

## Review agent

Explicitly invoke Matt Pocock's installed `code-review` skill using the phrase: **"review the changes since [baseline SHA]"** and the exact **Standards** and **Spec** axes. The skill runs those reviews in parallel subagents; don't replace it. Return side-by-side findings with evidence, severity, paths/lines, and a concise consolidated fix queue. Review relevant new/untracked files too.

## Review-fix agent

One agent with a fresh context, actual review findings, relevant source paths, and the latest available Sonnet/Sol preference at High effort under the shared resolution policy. Validate each finding conceptually, fix valid ones, update affected tests/docs, and justify any dismissal. Do not run checks.

## Test-fix agent

Only if checks fail. Request the latest available Sonnet/Sol at High effort under the shared resolution policy. Reuse this agent for related debugging iterations when beneficial. Pass precise failed commands, exit codes, diagnostic excerpts, paths to logs, and relevant changed files. Fix root causes; do not disable useful checks or weaken valid assertions. The orchestrator, not this agent, performs official staged revalidation.

## Final response format

- Configuration: complexity, requested family/effort and actual settings, fallbacks or runtime limitations.
- Implementation: completed behavior and major affected files.
- Review: Standards vs Spec findings and resolutions.
- Validation: exact commands and results; clearly mark unrun checks.
- Commit: hash, Conventional Commit subject (if successful), or reason not committed.
- Remaining issues: only concrete blockers or risks.

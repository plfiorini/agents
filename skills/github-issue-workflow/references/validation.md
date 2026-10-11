# Review, Verification and Commit Guardrails

## Review scope

Record a fixed baseline before implementation. At review time inspect working-tree changes **and** commits since baseline when applicable, including new/untracked issue files. Beware that pre-existing unrelated changes may also appear: mark scope clearly and exclude them from remediation or commit. For example, `git status --short`, `git diff --stat <sha>`, `git diff <sha>`, and `git ls-files --others --exclude-standard` can aid inspection; choose commands appropriate to the repo and working state.

The installed Matt Pocock `code-review` skill is mandatory: ask it to **review the changes since a fixed point** on **Standards** and **Spec** and **run both reviews in parallel sub-agents, reported side by side**. Let the skill prescribe its actual process and internal model selection; leave review-wrapper model/effort at runtime defaults. No test/build/lint/static-analysis execution before review remediation is complete.

## Review remediation

After review, spawn one dedicated fresh-context agent to resolve actionable findings and justify dismissals, updating tests/docs as needed. Request the latest available Sonnet in Claude Code or Sol in Codex at **High effort** using [agent-contracts.md](agent-contracts.md#dynamic-resolution-at-agent-creation). Apply its disclosed fallback/default policy when configuration is unsupported. Complete this phase before running any checks.

## Deferred test order

Use discovered project commands, not placeholder invocations. After remediation:

1. Lightweight build/type/static/lint checks where applicable.
2. Focused tests covering issue-modified modules.
3. Complete relevant unit suite.
4. Relevant integration/end-to-end suite and other mandatory checks.

Stop early if a failed prerequisite makes later results meaningless. Capture bulky output outside conversation; use concise summaries including command, exit status, failure signature and log location. Failed checks invoke one dedicated debugging agent requesting the same latest-family preference at **High effort**, followed by orchestrator reruns of affected checks and final required validation. Reuse debugging context for related failures when beneficial; avoid redundant checks or reviews unless changes or unresolved concerns warrant them. Continue only until validation passes or a specific blocker is documented. Never misreport skipped tests as successes.

## Commit gate

Require all of: acceptance criteria assessed, review findings resolved or justified, required checks passing, final diff reviewed, no unrelated/pre-existing user changes staged, no secrets committed.

Invoke **`git-commit` skill directly in the orchestrator** for the actual Conventional Commit. Do not replace its prescribed behavior or spawn a commit agent. Push or open a PR only when explicitly requested. If the skill is missing, validation failed, or a blocker remains: leave changes uncommitted and report why.

## Model settings

The family table and runtime resolution procedure in [agent-contracts.md](agent-contracts.md#model-family-preferences) govern both remediation roles. Always request **High effort**; if model/effort configuration is unsupported, proceed with supported defaults and disclose the actual settings or that they cannot be verified. Model fallback alone introduces no additional approval gate. Required review/commit skills and validation gates remain mandatory.

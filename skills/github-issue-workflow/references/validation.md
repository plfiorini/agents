# Review, Verification and Commit Guardrails

## Review scope

Record a fixed baseline before implementation. At review time inspect working-tree changes **and** commits since baseline when applicable, including new/untracked issue files. Beware that pre-existing unrelated changes may also appear: mark scope clearly and exclude them from remediation or commit. For example, `git status --short`, `git diff --stat <sha>`, `git diff <sha>`, and `git ls-files --others --exclude-standard` can aid inspection; choose commands appropriate to the repo and working state.

The installed Matt Pocock `code-review` skill is mandatory: ask it to **review the changes since a fixed point** on **Standards** and **Spec** and **run both reviews in parallel sub-agents, reported side by side**. Let the skill prescribe its actual process. No test/build/lint/static-analysis execution before review remediation is complete.

## Deferred test order

Use discovered project commands, not placeholder invocations. After remediation:

1. Lightweight build/type/static/lint checks where applicable.
2. Focused tests covering issue-modified modules.
3. Complete relevant unit suite.
4. Relevant integration/end-to-end suite and other mandatory checks.

Stop early if a failed prerequisite makes later results meaningless. Capture bulky output outside conversation; use concise summaries including command, exit status, failure signature and log location. Failed checks invoke one high-effort fix agent, followed by orchestrator reruns. Continue only until validation passes or a specific blocker is documented. Never misreport skipped tests as successes.

## Commit gate

Require all of: acceptance criteria assessed, review findings resolved or justified, required checks passing, final diff reviewed, no unrelated/pre-existing user changes staged, no secrets committed.

Invoke **`git-commit` skill directly in the orchestrator** for the actual Conventional Commit. Do not replace its prescribed behavior or spawn a commit agent. Do not push or open a PR. If the skill is missing, validation failed, or a blocker remains: leave changes uncommitted and report why.

## Model settings

For review remediation and conditional test remediation, request:
- Claude Code: **Sonnet 5.5, High effort**.
- Codex: **GPT 6.1 Sol, High effort**.

Model names and effort availability depend on host configuration; do not falsely claim a model was selected. If selection is unsupported, surface the limitation and request configuration before the model-constrained phase.

---
name: git-commit
description: >
  Use when creating Git commits to ensure they follow the Conventional Commits specification. It provides guidance on commit message structure, types, scopes, and best practices for writing clear, consistent, and automated-friendly commit messages. Use when committing code changes or reviewing commit history.
allowed-tools: Agent
---

# Conventional Commits

Delegate this task to the `git-commit` agent (via the `Agent` tool, `subagent_type: git-commit`) — it runs on Haiku to keep commit-creation cheap. Forward any user-specified scope, message wording, or file constraints from the current conversation in the delegation prompt. The agent inspects `git status`/`git diff` itself, stages files if needed, and creates the Conventional Commits-compliant commit — no need to paste diff content into the prompt.

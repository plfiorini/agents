---
name: create-commit-instructions
description: Generate or update `.github/instructions/commit.instructions.md` for the current workspace from bundled `assets/commit.instructions.d` fragments. Use when the user asks to create commit instructions, Conventional Commit guidance, repository-specific commit message rules, or GitHub Copilot/agent commit instructions, especially when the SCOPE GUIDANCE and GOOD EXAMPLES sections must be adapted to the project being edited.
---

# Create Commit Instructions

Generate `.github/instructions/commit.instructions.md` for the active
workspace from the ordered fragments in `assets/commit.instructions.d`.
Copy the stable sections from the assets, and adapt only these sections to
the target project:

- `SCOPE GUIDANCE`
- `GOOD EXAMPLES`

## Workflow

1. Resolve the target workspace:
   - Use the user's explicit path when provided.
   - Otherwise use `git rev-parse --show-toplevel`.
   - If the directory is not a Git repository, use the current working
     directory.
2. Inspect the project before writing:
   - Run `rg --files` from the workspace root, excluding dependency and
     generated directories such as `node_modules`, `.git`, `dist`, `build`,
     `coverage`, `.next`, `target`, and `vendor` unless those directories
     are first-party source in this repository.
   - Read the top-level build and package files that identify the stack
     (`package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`,
     `CMakeLists.txt`, `*.sln`, `pom.xml`, `build.gradle*`, `Makefile`,
     workflow files, and similar files that exist).
   - Inspect the primary source, test, docs, scripts, infrastructure, and
     CI directories enough to identify real subsystem names.
3. Read every file in `assets/commit.instructions.d` in lexicographic order.
4. Assemble the output by concatenating the fragments with exactly one blank
   line between fragments.
5. Replace `[[ADAPT_SCOPE_GUIDANCE]]` with a repository-specific scope
   section.
6. Replace `[[ADAPT_GOOD_EXAMPLES]]` with repository-specific examples.
7. Write the result to `.github/instructions/commit.instructions.md`,
   creating `.github/instructions` if needed.

## Scope Guidance

Use only scopes that are grounded in the inspected repository. Prefer scope
names that a maintainer would recognize from package names, source
directories, feature modules, product domains, test suites, CI/build files, or
documentation areas.

Generate 8 to 18 scopes when the project is large enough. Use fewer scopes for
small projects. Omit a scope instead of inventing one.

The generated section must include:

- A short paragraph explaining when to use a scope and when to omit it.
- A Markdown table with columns `Scope` and `Meaning`.
- Meanings that cite real paths, modules, packages, commands, or subsystems.
- Additional guidance bullets that resolve likely scope conflicts in this
  repository.

Avoid generic scopes unless they map to real project structure. Do not use
stale template scopes such as `processor`, `dsp`, `juce`, `plugin`, or
`neural` unless those terms actually exist in the target repository.

## Good Examples

Generate 8 to 12 examples that match the repository's stack and scopes.
Include a mix of `feat`, `fix`, `refactor`, `perf`, `test`, `build`, `ci`,
`docs`, `chore`, and `revert` only when each type is plausible for this
project.

Examples must:

- Use scopes from the generated `SCOPE GUIDANCE` table when a scope is useful.
- Be specific to project concepts discovered in the repository.
- Stay under 72 characters on the subject line.
- Use lowercase imperative descriptions with no trailing period.
- Include one breaking-change example only when the project has public API,
  persisted state, package contracts, schemas, CLI flags, or other compatibility
  surfaces where breaking changes are meaningful.

## Validation

Before finishing:

- Confirm the output contains no `[[ADAPT_` placeholders.
- Confirm no copied template domain terms remain unless present in the target
  repository.
- Confirm `.github/instructions/commit.instructions.md` starts with the
  `applyTo: "commits"` frontmatter.
- Read the generated `SCOPE GUIDANCE` and `GOOD EXAMPLES` sections once more
  and verify each scope and example is supported by the inspected files.

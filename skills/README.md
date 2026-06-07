# Skills

A skill is a markdown file that teaches an AI agent how to perform a specific task. Skills are installed into your local agents directory and referenced by your VS Code Copilot configuration.

## Available Skills

### `create-commit-instructions`

Generates or updates `.github/instructions/commit.instructions.md` for the active workspace from bundled fragment files. The skill inspects the repository structure and adapts the scope guidance and commit examples to your specific project.

**Install:**
```bash
npx skills add plfiorini/agents --skill create-commit-instructions
```

---

### `node-scaffolding`

Scaffolds a production-ready Node.js + TypeScript project. Supports optional features including a Fastify HTTP server, Prometheus metrics, Sequelize + Postgres database, Azure Entra ID auth, Umzug migrations, Dockerfile, OpenAPI docs, and a VS Code Dev Container.

**Install:**
```bash
npx skills add plfiorini/agents --skill node-scaffolding
```

## Installing All Skills

```bash
npx skills add plfiorini/agents
```

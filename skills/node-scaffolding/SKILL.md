---
name: node-scaffolding
mode: agent
description: >
  Scaffold a production-ready Node.js + TypeScript project. Use this skill
  whenever the user wants to create a new Node.js app, set up a TypeScript
  service, bootstrap an API, start a microservice, or initialize a backend
  project — even if they don't say "scaffold" explicitly.
argument-hint: "[project-name] [--workspace-root|--path <target-path>] [--http] [--metrics] [--db] [--entra-id] [--migrations] [--docker] [--openapi] [--devcontainer]"
metadata:
  author: Pier Luigi Fiorini
  license: MIT
  version: "1.0"
allowed-tools: Bash Read Write
inputs:
  - id: projectName
    description: "Project name — used as the package.json name and as the default directory name when creating under a custom path"
    type: promptString
    default: my-app
  - id: projectLocation
    description: "Where to create the project"
    type: pickString
    options:
      - "workspace-root"
      - "custom-path"
    default: "workspace-root"
  - id: targetPath
    description: "Explicit target path when projectLocation=custom-path"
    type: promptString
    default: ""
  - id: withHttp
    description: "Add a Fastify HTTP server with Kubernetes health probes?"
    type: pickString
    options:
      - "yes"
      - "no"
    default: "no"
  - id: withMetrics
    description: "Expose a Prometheus /metrics endpoint? (forces HTTP server on)"
    type: pickString
    options:
      - "yes"
      - "no"
    default: "no"
  - id: withDb
    description: "Add a Sequelize + Postgres database module?"
    type: pickString
    options:
      - "yes"
      - "no"
    default: "no"
  - id: withEntraId
    description: "Use Azure Entra ID authentication for Azure Database for PostgreSQL? (requires withDb)"
    type: pickString
    options:
      - "yes"
      - "no"
    default: "no"
  - id: withMigrations
    description: "Add Sequelize migrations with Umzug? (requires withDb)"
    type: pickString
    options:
      - "yes"
      - "no"
    default: "no"
  - id: withDocker
    description: "Add a production-ready Dockerfile for Node 24?"
    type: pickString
    options:
      - "yes"
      - "no"
    default: "no"
  - id: withOpenApi
    description: "Add @fastify/swagger + @fastify/swagger-ui for OpenAPI docs? (forces HTTP server on)"
    type: pickString
    options:
      - "yes"
      - "no"
    default: "no"
  - id: withDevContainer
    description: "Add a VS Code Dev Container configuration?"
    type: pickString
    options:
      - "yes"
      - "no"
    default: "no"
---

# Node Scaffolding

Run the bundled scaffolder from this skill directory:

```bash
python3 scripts/scaffold.py [project-name] [--workspace-root|--path <target-path>] [--http] [--metrics] [--db] [--entra-id] [--migrations] [--docker] [--openapi] [--devcontainer]
```

When this skill is running inside VS Code/Copilot, make the generated project visible as Copilot file changes:

1. Run the scaffolder with `--emit-files-json` and the same arguments you would otherwise pass.
2. Parse the JSON response.
3. Create or update every file from `files[].path` using the Copilot/agent file-edit tool, with the exact `files[].content`.
4. Show `postGenerationMessage` after the file edits are applied.

Do not run the scaffolder in direct write mode from VS Code/Copilot unless the user explicitly asks for that. Direct script writes bypass Copilot's file-change UI, so the user will not get the normal Keep/Undo review affordance.

Outside VS Code/Copilot, run the scaffolder normally without `--emit-files-json`.

Map inputs to arguments:

- `projectName` -> `[project-name]`
- `projectLocation=workspace-root` -> `--workspace-root`
- `projectLocation=custom-path` and `targetPath=<value>` -> `--path <value>`
- `withHttp=yes` -> `--http`
- `withMetrics=yes` -> `--metrics`
- `withDb=yes` -> `--db`
- `withEntraId=yes` -> `--entra-id`
- `withMigrations=yes` -> `--migrations`
- `withDocker=yes` -> `--docker`
- `withOpenApi=yes` -> `--openapi`
- `withDevContainer=yes` -> `--devcontainer`

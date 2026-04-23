---
name: node-scaffolding
mode: agent
description: >
  Scaffold a production-ready Node.js + TypeScript project. Use this skill
  whenever the user wants to create a new Node.js app, set up a TypeScript
  service, bootstrap an API, start a microservice, or initialize a backend
  project — even if they don't say "scaffold" explicitly.
argument-hint: "[project-name] [--workspace-root|--path <target-path>] [--http] [--metrics] [--db] [--migrations] [--docker] [--openapi] [--devcontainer]"
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

# Scaffold a Node.js + TypeScript Project

## Step 1 — Resolve parameters

Inputs:

- `projectName`: `package.json` name; also the leaf directory name when the user supplies only a parent path
- `projectLocation`: `workspace-root` or `custom-path`
- `targetPath`: required only for `custom-path`; may be either the final project directory or a parent directory
- `withHttp`, `withMetrics`, `withDb`, `withMigrations`, `withDocker`, `withOpenApi`, `withDevContainer`: feature flags

If the user's message already contains all parameters, infer the values and skip already-answered inputs.

Infer location from the user's wording:

- "in the workspace root", "here", "in this repo", "in the current IDE workspace" → `projectLocation=workspace-root`
- "at /some/path", "under /some/path", "in ~/code/foo", "use this path" → `projectLocation=custom-path` and set `targetPath` from the provided path
- If unspecified, default to `projectLocation=workspace-root`

**Constraints:**
- `projectLocation=custom-path` requires a non-empty `targetPath`.
- If the user gives a parent directory rather than a final project directory, create the project in `<targetPath>/<projectName>`.
- If the user gives a full target directory path, create the project directly at that path and do not append `projectName` again.
- `withMetrics=yes` and `withHttp=no` → treat `withHttp` as `"yes"` and inform the user.
- `withOpenApi=yes` and `withHttp=no` → treat `withHttp` as `"yes"` and inform the user.
- `withMigrations=yes` and `withDb=no` → treat `withDb` as `"yes"` and inform the user.

---

## Step 2 — Generate files

Output every file in full — no placeholders, no `// ...`, no truncation. Generate conditional files only when the relevant input is `"yes"`.

Write files under `<targetRoot>`:

- workspace root when `projectLocation=workspace-root`
- resolved custom directory when `projectLocation=custom-path`

When targeting the workspace root, write directly into the current workspace and do not create an extra `<projectName>/` wrapper directory.

Always generate:

- `package.json`, `tsconfig.json`, `biome.jsonc`, `config.yaml.example`, `.env.example`, `.gitignore`
- `.vscode/settings.json`, `.vscode/extensions.json`
- `src/index.ts`, `src/config.ts`, `src/logger.ts`

Conditional files:

- `Dockerfile`, `.dockerignore` when `withDocker=yes`
- `.devcontainer/devcontainer.json` when `withDevContainer=yes`
- `migrations/20240101000000-create-example.ts`, `migrations/20240101000001-create-example.up.sql`, `migrations/20240101000001-create-example.down.sql`, `src/migrate.ts` when `withMigrations=yes`
- `src/database.ts` when `withDb=yes`
- `src/metrics.ts` when `withMetrics=yes`
- `src/server.ts` and `src/endpoints/health/*` when `withHttp=yes`
- `src/endpoints/metrics/{metrics.route.ts,metrics.controller.ts,metrics.service.ts,metrics.test.ts}` when `withHttp=yes` and `withMetrics=yes`

> **OpenAPI (`withOpenApi`):** no extra files — swagger plugins wire into `src/server.ts` and JSON Schema declarations go inline on each route.

> **Endpoint convention:** every HTTP endpoint lives under `src/endpoints/<endpoint>/` with five files. The `metrics` endpoint has no repository (no database access).

---

## Step 3 — File specifications

### Global rules

- Latest stable TypeScript (`"typescript": "latest"`), `strict: true`, `noUncheckedIndexedAccess`, `noImplicitOverride`, target `ESNext`.
- Run TypeScript source directly via `--experimental-strip-types` — no `ts-node`/`tsx`, no compile step.
- **Local imports use `.ts` extension** (not `.js`) — Node 24 runs source files directly and there is no compiled output to point at.
- `"type": "module"`, `"module": "NodeNext"`, `"moduleResolution": "NodeNext"`, `"allowImportingTsExtensions": true`.
- File-relative paths: `import.meta.url` + `path.dirname`; never `__dirname` or `__filename`.
- Top-level `await` is valid in ESM entry points.
- Biome style: 4-space indent, 120 columns, double quotes, semicolons always, trailing commas all, omit arrow parens for a single param

---

### `package.json`

`"type": "module"` and `"engines": { "node": ">=24.0.0" }` are mandatory.

Scripts:

- Always: `start=node --experimental-strip-types src/index.ts`, `dev=node --watch --experimental-strip-types --env-file=.env src/index.ts`, `typecheck=tsc --noEmit`, `test=node --test --experimental-strip-types "src/**/*.test.ts"`, `lint=biome lint ./src`, `format=biome format --write ./src`, `check=biome check ./src`, `check:fix=biome check --write ./src`
- With migrations: `migrate=node --experimental-strip-types src/migrate.ts up`, `migrate:down=node --experimental-strip-types src/migrate.ts down`, `migrate:pending=node --experimental-strip-types src/migrate.ts pending`

Dependencies:

- Always deps: `pino`, `pino-pretty`, `zod`, `zod-config`
- Always devDeps: `typescript@latest`, `@types/node@latest`, `@biomejs/biome`
- `withHttp`: `fastify`, `@fastify/sensible`
- `withOpenApi`: `@fastify/swagger`, `@fastify/swagger-ui`
- `withMetrics`: `prom-client`
- `withDb`: `sequelize`, `pg`, `pg-hstore`, devDep `@types/pg`
- `withMigrations`: `umzug`

> `tsx` and `ts-node` are **not** included. Node 24 covers the full dev and test workflow natively.

---

### Direct copies from assets

- `tsconfig.json` from `assets/tsconfig.json`
- `biome.jsonc` from `assets/biome.jsonc`
- `.vscode/settings.json` from `assets/vscode/settings.json`
- `.vscode/extensions.json` from `assets/vscode/extensions.json`
- `.gitignore` from `assets/gitignore`
- `src/logger.ts` from `assets/src/logger.ts`

### `config.yaml.example`

Copy `assets/config.yaml.example`. Omit `port` when `withHttp=no`. Omit the `openapi` block when `withOpenApi=no`.

> Committed to source control. Contains non-secret base configuration only. Copy to `config.yaml` and adjust per environment.

### `.env.example`

Copy from `assets/env.example`. Replace `<PROJECT_NAME>` using the same SCREAMING_SNAKE_CASE rule as `src/config.ts`. Omit the `<PROJECT_NAME>_DB_URL` line when `withDb=no`.

### `src/config.ts`

Read `assets/src/config.ts` as template, then adapt:

- Replace every literal `<PROJECT_NAME>` with the SCREAMING_SNAKE_CASE form of `projectName`: replace each `-` with `_` then uppercase (e.g. `foo-bar` → `FOO_BAR`, `foobar` → `FOOBAR`).
- Omit `port` field when `withHttp=no`.
- Omit `dbUrl` field when `withDb=no`.
- The `log` nested object is always present; include it as-is.
- Add `openapi` nested object when `withOpenApi=yes` (see `references/openapi.md` for exact field definitions).
- Keep all imports and `import.meta.url` path resolution exactly as shown in the asset — required for `yamlAdapter` to locate `config.yaml` reliably.

### Server-side modules

Read `references/server.md` for:

- `src/database.ts` *(withDb)* — Sequelize instance and connect/close helpers
- `src/metrics.ts` *(withMetrics)* — prom-client registry, ELU gauge, request histogram
- `src/server.ts` *(withHttp)* — Fastify setup, shutdown hook, route registration
- `src/index.ts` — three variants (copy verbatim from asset based on `withHttp`/`withDb`)

When `withMigrations=yes`, also read `references/migrations.md` for `src/migrate.ts` and example migration files.

When `withOpenApi=yes`, also read `references/openapi.md` for config additions, `src/server.ts` plugin registration, and route schema annotations.

Read `references/endpoints.md` for all `src/endpoints/**` files.

### `.devcontainer/devcontainer.json` *(withDevContainer)*

Start from `assets/devcontainer/devcontainer.json`, then apply:

- When `withHttp=yes`, add a top-level `"forwardPorts": [3000]` field and a `"portsAttributes"` block:
  ```json
  "forwardPorts": [3000],
  "portsAttributes": {
    "3000": { "label": "HTTP Server", "onAutoForward": "notify" }
  }
  ```

### `Dockerfile` *(withDocker)*

Copy from `assets/Dockerfile`. Two-stage Alpine build; no compile step — `src/` runs directly as the application.

- Omit the `COPY --chown=appuser:nodejs migrations ./migrations` line when `withMigrations=no`.

### `.dockerignore` *(withDocker)*

Copy verbatim from `assets/dockerignore`.

---

## Step 4 — Post-generation message

Print the template from `assets/post-gen-message.md`, substituting `<projectName>` and omitting lines/sections whose condition does not apply.

Also state the final output path explicitly so the user can verify where the project was created.

---

## Examples

> "Scaffold **order-service** in the workspace root with HTTP and metrics, no database" → `projectLocation=workspace-root`, `withHttp=yes`, `withMetrics=yes`, `withDb=no`
> "Create **worker** at `/home/me/services`" → `projectLocation=custom-path`, `targetPath=/home/me/services`, final directory `/home/me/services/worker`
> "New **api** at `~/code/api` with everything" → `projectLocation=custom-path`, `targetPath=~/code/api`, final directory `~/code/api`, all flags `yes`

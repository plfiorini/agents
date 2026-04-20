---
name: node-scaffolding
mode: agent
description: >
  Scaffold a production-ready Node.js + TypeScript project. Use this skill
  whenever the user wants to create a new Node.js app, set up a TypeScript
  service, bootstrap an API, start a microservice, or initialize a backend
  project — even if they don't say "scaffold" explicitly.
argument-hint: "[project-name] [--http] [--metrics] [--db] [--migrations] [--docker] [--openapi]"
metadata:
  author: Pier Luigi Fiorini
  license: MIT
  version: "1.0"
allowed-tools: Bash Read Write
inputs:
  - id: projectName
    description: "Project name — used as the directory name and package.json name"
    type: promptString
    default: my-app
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
---

# Scaffold a Node.js + TypeScript Project

## Step 1 — Resolve parameters

| Variable | Meaning |
|---|---|
| `${input:projectName}` | directory name and `package.json` `name` |
| `${input:withHttp}` | `"yes"` → generate server files |
| `${input:withMetrics}` | `"yes"` → generate metrics files |
| `${input:withDb}` | `"yes"` → generate database files |
| `${input:withMigrations}` | `"yes"` → generate Umzug migration runner and example migrations |
| `${input:withDocker}` | `"yes"` → generate `Dockerfile` and `.dockerignore` |
| `${input:withOpenApi}` | `"yes"` → register swagger plugins and annotate routes |

If the user's message already contains all parameters, infer the values and skip already-answered inputs.

**Constraints:**
- `withMetrics=yes` and `withHttp=no` → treat `withHttp` as `"yes"` and inform the user.
- `withOpenApi=yes` and `withHttp=no` → treat `withHttp` as `"yes"` and inform the user.
- `withMigrations=yes` and `withDb=no` → treat `withDb` as `"yes"` and inform the user.

---

## Step 2 — Generate files

Output every file in full — no placeholders, no `// ...`, no truncation. Generate conditional files only when the relevant input is `"yes"`.

### Project structure

```
<projectName>/
├── package.json
├── tsconfig.json
├── biome.jsonc
├── config.yaml.example
├── .env.example
├── .gitignore
├── Dockerfile                                    (withDocker)
├── .dockerignore                                 (withDocker)
├── migrations/                                   (withMigrations)
│   ├── 20240101000000-create-example.ts
│   ├── 20240101000001-create-example.up.sql
│   └── 20240101000001-create-example.down.sql
├── .vscode/
│   └── settings.json
└── src/
    ├── index.ts
    ├── config.ts
    ├── logger.ts
    ├── database.ts                               (withDb)
    ├── migrate.ts                                (withMigrations)
    ├── metrics.ts                                (withMetrics)
    ├── server.ts                                 (withHttp)
    └── endpoints/
        ├── health/                               (withHttp)
        │   ├── health.route.ts
        │   ├── health.controller.ts
        │   ├── health.service.ts
        │   ├── health.repository.ts
        │   └── health.test.ts
        └── metrics/                              (withHttp + withMetrics)
            ├── metrics.route.ts
            ├── metrics.controller.ts
            ├── metrics.service.ts
            └── metrics.test.ts
```

> **OpenAPI (`withOpenApi`):** no extra files — swagger plugins wire into `src/server.ts` and JSON Schema declarations go inline on each route.

> **Endpoint convention:** every HTTP endpoint lives under `src/endpoints/<endpoint>/` with five files. The `metrics` endpoint has no repository (no database access).

---

## Step 3 — File specifications

### Global rules

#### TypeScript & Node.js 24

- Latest stable TypeScript (`"typescript": "latest"`), `strict: true`, `noUncheckedIndexedAccess`, `noImplicitOverride`, target `ESNext`.
- Run TypeScript source directly via `--experimental-strip-types` — no `ts-node`/`tsx`, no compile step.
- **Local imports use `.ts` extension** (not `.js`) — Node 24 runs source files directly and there is no compiled output to point at.
- `"type": "module"`, `"module": "NodeNext"`, `"moduleResolution": "NodeNext"`, `"allowImportingTsExtensions": true`.
- File-relative paths: `import.meta.url` + `path.dirname`; never `__dirname` or `__filename`.
- Top-level `await` is valid in ESM entry points.

#### Biome style

| Rule | Value |
|---|---|
| Indent | 4 spaces |
| Line width | 120 |
| Quotes | Double (`"`) |
| Semicolons | Always |
| Trailing commas | All |
| Arrow parens | Omit for single param (`x => x`) |

---

### `package.json`

`"type": "module"` and `"engines": { "node": ">=24.0.0" }` are mandatory.

Scripts:

| Script | Command | Condition |
|---|---|---|
| `start` | `node --experimental-strip-types src/index.ts` | always |
| `dev` | `node --watch --experimental-strip-types --env-file=.env src/index.ts` | always |
| `typecheck` | `tsc --noEmit` | always |
| `test` | `node --test --experimental-strip-types "src/**/*.test.ts"` | always |
| `lint` | `biome lint ./src` | always |
| `format` | `biome format --write ./src` | always |
| `check` | `biome check ./src` | always |
| `check:fix` | `biome check --write ./src` | always |
| `migrate` | `node --experimental-strip-types src/migrate.ts up` | `withMigrations` |
| `migrate:down` | `node --experimental-strip-types src/migrate.ts down` | `withMigrations` |
| `migrate:pending` | `node --experimental-strip-types src/migrate.ts pending` | `withMigrations` |

Dependencies:

| Package | Type | Condition |
|---|---|---|
| `pino` | dependency | always |
| `zod` | dependency | always |
| `zod-config` | dependency | always |
| `fastify` | dependency | `withHttp` |
| `@fastify/sensible` | dependency | `withHttp` |
| `@fastify/swagger` | dependency | `withOpenApi` |
| `@fastify/swagger-ui` | dependency | `withOpenApi` |
| `prom-client` | dependency | `withMetrics` |
| `sequelize` | dependency | `withDb` |
| `pg` | dependency | `withDb` |
| `pg-hstore` | dependency | `withDb` |
| `umzug` | dependency | `withMigrations` |
| `typescript` (`"latest"`) | devDependency | always |
| `@types/node` (`"latest"`) | devDependency | always |
| `@biomejs/biome` | devDependency | always |
| `pino-pretty` | devDependency | always |
| `@types/pg` | devDependency | `withDb` |

> `tsx` and `ts-node` are **not** included. Node 24 covers the full dev and test workflow natively.

---

### `tsconfig.json`

Copy verbatim from `assets/tsconfig.json`.

### `biome.jsonc`

Copy verbatim from `assets/biome.jsonc`.

### `.vscode/settings.json`

Copy verbatim from `assets/vscode-settings.json`.

### `config.yaml.example`

Copy from `assets/config.yaml.example`. Omit the `port` field when `withHttp=no`. Omit the `openapi` block when `withOpenApi=no`.

> Committed to source control. Contains non-secret base configuration only. Copy to `config.yaml` and adjust per environment.

### `.env.example`

Copy from `assets/.env.example`. Omit the `DATABASE_URL` line when `withDb=no`.

### `.gitignore`

Copy verbatim from `assets/.gitignore`.

### `src/config.ts`

Read `assets/src/config.ts` as template, then adapt:

- Omit `port` field when `withHttp=no`.
- Omit `dbUrl` field and `DATABASE_URL` mapping when `withDb=no`.
- The `log` nested object is always present; include it as-is.
- Add `openapi` nested object when `withOpenApi=yes` (see `references/openapi.md` for exact field definitions).
- Keep all imports and `import.meta.url` path resolution exactly as shown in the asset — required for `yamlAdapter` to locate `config.yaml` reliably.

### `src/logger.ts`

Copy verbatim from `assets/src/logger.ts`.

### Server-side modules

Read `references/server.md` for:

- `src/database.ts` *(withDb)* — Sequelize instance and connect/close helpers
- `src/metrics.ts` *(withMetrics)* — prom-client registry, ELU gauge, request histogram
- `src/server.ts` *(withHttp)* — Fastify setup, shutdown hook, route registration
- `src/index.ts` — three variants (copy verbatim from asset based on `withHttp`/`withDb`)

When `withMigrations=yes`, also read `references/migrations.md` for `src/migrate.ts` and example migration files.

When `withOpenApi=yes`, also read `references/openapi.md` for config additions, `src/server.ts` plugin registration, and route schema annotations.

### Endpoint layer

Read `references/endpoints.md` for all files under `src/endpoints/`.

### `Dockerfile` *(withDocker)*

Copy verbatim from `assets/Dockerfile`. Two-stage Alpine build; no compile step — `src/` runs directly as the application.

### `.dockerignore` *(withDocker)*

Copy verbatim from `assets/.dockerignore`.

---

## Step 4 — Post-generation message

Print the template from `assets/post-gen-message.md`, substituting `<projectName>` and omitting lines/sections whose condition does not apply.

---

## Examples

> "Scaffold **order-service** with HTTP and metrics, no database" → `withHttp=yes`, `withMetrics=yes`, `withDb=no`
> "Create a **worker** — no HTTP, just a database" → `withHttp=no`, `withDb=yes`
> "New **api** with everything" → all flags `yes`

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

Use the values collected from the UI inputs above:

| Variable | Comes from | Meaning |
|---|---|---|
| `${input:projectName}` | text input | directory name and `package.json` `name` |
| `${input:withHttp}` | pick | `"yes"` → generate server files |
| `${input:withMetrics}` | pick | `"yes"` → generate metrics files |
| `${input:withDb}` | pick | `"yes"` → generate database files |
| `${input:withMigrations}` | pick | `"yes"` → generate Umzug migration runner and example migration |
| `${input:withDocker}` | pick | `"yes"` → generate `Dockerfile` and `.dockerignore` |
| `${input:withOpenApi}` | pick | `"yes"` → register `@fastify/swagger` + `@fastify/swagger-ui` and annotate routes |

If the user's message already contains all parameters (e.g. *"scaffold payments-api with http and metrics"*), infer the values and skip the UI inputs that were already answered.

**Constraints:**
- If `${input:withMetrics}` is `"yes"` and `${input:withHttp}` is `"no"`, treat `withHttp` as `"yes"` and inform the user.
- If `${input:withOpenApi}` is `"yes"` and `${input:withHttp}` is `"no"`, treat `withHttp` as `"yes"` and inform the user.
- If `${input:withMigrations}` is `"yes"` and `${input:withDb}` is `"no"`, treat `withDb` as `"yes"` and inform the user.


---

## Step 2 — Generate files

Output every file listed below in full — no placeholders, no `// ...`, no truncation. Generate conditional files only when the relevant input is `"yes"`.

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

> **OpenAPI (`withOpenApi`):** no extra files are created. The swagger plugins are wired into
> `src/server.ts` and JSON Schema declarations are added inline to each route handler.

> **Endpoint convention:** every HTTP endpoint lives under `src/endpoints/<endpoint>/` with five files. The `metrics` endpoint has no repository because it does not access a database.

---

## Step 3 — File specifications

### Global rules (apply to every generated file)

#### TypeScript
- Use the **latest stable version** of TypeScript (`"typescript": "latest"`).
- Enable `strict: true` plus `noUncheckedIndexedAccess` and `noImplicitOverride`.
- Target `ESNext`, `lib: ["ESNext"]`.

#### Type-stripping
- Use **Node.js 24 native type-stripping** (`--experimental-strip-types`) for all scripts (`start`, `dev`, `test`).
- Do **not** use `ts-node` or `tsx`. Node 24 runs TypeScript source directly — there is no compilation step.

#### Module system
- `"type": "module"` in `package.json` — ES Modules are mandatory.
- Use `import`/`export` exclusively. Never `require`, `module.exports`, `__dirname`, or `__filename`.
- Use `import.meta.url` with `path.dirname` wherever a file-relative path is needed.
- **All local imports must use the `.ts` extension** — Node 24 runs TypeScript directly; there is no compiled `.js` to point at.
- `"module": "NodeNext"` and `"moduleResolution": "NodeNext"` in `tsconfig.json`.
- `"allowImportingTsExtensions": true` is required in `tsconfig.json` because imports use `.ts` extensions.

#### Async & I/O
- `async/await` everywhere — no `.then()/.catch()` chains, no nested callbacks.
- No synchronous I/O — `fs/promises` only; never any `*Sync` variant.
- Wrap every `await` in `try/catch` or let errors propagate to a documented top-level handler.
- Top-level `await` is allowed in ESM entry points (e.g. `src/index.ts`, `src/config.ts`).

#### Code style — Biome-compliant

Every generated TypeScript file must pass `biome check` without modifications:

| Rule | Value |
|---|---|
| Indent | 4 spaces |
| Line width | 120 characters |
| Quotes | Double (`"`) |
| Semicolons | Always |
| Trailing commas | All (arrays, objects, function parameters) |
| Arrow parens | Omit for single parameter (`x => x`) |
| `const` / `let` | `const` by default; `let` only when reassignment is needed; never `var` |
| Equality | `===` / `!==` only |
| `eval` | Never — `noGlobalEval` is `error` in the Biome config |
| Paths | `path.join()` / `path.resolve()` only; never string concatenation |
| Secrets | Environment variables only; never hardcoded |

---

### `package.json`

- `"type": "module"` and `"engines": { "node": ">=24.0.0" }` are mandatory.
- Scripts:

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

- Dependencies:

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

---

### `biome.jsonc`

Copy verbatim from `assets/biome.jsonc`.

---

### `.vscode/settings.json`

Copy verbatim from `assets/vscode-settings.json`.

---

### `config.yaml.example`

Copy from `assets/config.yaml.example`. Omit the `port` field when `withHttp=no`. Omit the `openapi` block when `withOpenApi=no`.

> Committed to source control. Contains non-secret base configuration only. Copy to `config.yaml` and adjust per environment.

---

### `.env.example`

Copy from `assets/.env.example`. Omit the `DATABASE_URL` line when `withDb=no`.

> Not committed to source control (`.gitignore` excludes `.env`). Contains secrets and values that must override `config.yaml`.

---

### `.gitignore`

Copy verbatim from `assets/.gitignore`.

> `config.yaml` is excluded because it may be customised per developer. The committed `config.yaml.example` is the source of truth for defaults.

---

### `src/config.ts`

Read `assets/src/config.ts` as the starting template, then adapt it to the enabled options:

- **Omit** the `port` field from the schema when `withHttp=no`.
- **Omit** the `dbUrl` field and the `DATABASE_URL` rename mapping when `withDb=no`.
- **Add** the `openapi` nested object to the schema when `withOpenApi=yes` — see `references/openapi.md` for the exact field definitions.
- Keep all import statements and the `__dirname` path resolution exactly as shown in the asset — they are required for the `yamlAdapter` to locate `config.yaml` reliably regardless of the working directory.

---

### `src/logger.ts`

Copy verbatim from `assets/src/logger.ts`.

---

### Server-side modules

Read `references/server.md` for the full specifications of:

- `src/database.ts` *(withDb)* — Sequelize instance and connect/close helpers
- `src/metrics.ts` *(withMetrics)* — prom-client registry, ELU gauge, request histogram
- `src/server.ts` *(withHttp)* — Fastify setup, shutdown hook, route registration
- `src/index.ts` — entry point; two variants (use asset templates, adapt per enabled options)

When `withMigrations=yes`, also read `references/migrations.md` for:

- `src/migrate.ts` — Umzug-based migration runner supporting `.ts` and `.up.sql` files (copy from `assets/src/migrate.ts`)
- `migrations/20240101000000-create-example.ts` — starter TypeScript migration (copy from asset)
- `migrations/20240101000001-create-example.up.sql` + `.down.sql` — starter SQL migration pair (copy from assets)

When `withOpenApi=yes`, also read `references/openapi.md` for:

- Config schema additions (`openapi` nested object)
- `src/server.ts` plugin registration (`@fastify/swagger` + `@fastify/swagger-ui` before routes)
- JSON Schema annotations required on each route

---

### Endpoint layer

Read `references/endpoints.md` for the full specifications of the layered architecture and all files under `src/endpoints/`.

---

### `Dockerfile` *(withDocker)*

Copy verbatim from `assets/Dockerfile`.

The image uses a two-stage Alpine build: stage `deps` installs production-only
dependencies, stage `runtime` copies in only `node_modules`, `src/`, and `package.json`
and runs as a non-root user. Because Node 24 runs TypeScript directly via
`--experimental-strip-types` there is no compiled output — `src/` is the application.

---

### `.dockerignore` *(withDocker)*

Copy verbatim from `assets/.dockerignore`.

---

## Step 4 — Post-generation message

```
✅  Project <projectName> scaffolded.

Next steps:
  cd <projectName>
  cp config.yaml.example config.yaml   # tune base config
  cp .env.example .env                 # add secrets
  npm install
  npm run dev                          # Node 24 runs TypeScript directly

Endpoints:                             # (withHttp only)
  GET /health/live                     Kubernetes liveness probe
  GET /health/ready                    Kubernetes readiness probe
  GET /metrics                         Prometheus scrape endpoint (withMetrics only)
  GET /documentation                   Swagger UI (withOpenApi only)

Migrations:                            # (withMigrations only)
  npm run migrate                      Apply all pending migrations
  npm run migrate:down                 Revert last migration
  npm run migrate:pending              List unapplied migrations

Useful scripts:
  npm test                             Run tests with Node 24 type-stripping
  npm run check                        Biome lint + format
  npm run typecheck                    Type-check without running

Docker:                                # (withDocker only)
  docker build -t <projectName> .
  docker run --rm --env-file .env -p 3000:3000 <projectName>
```

---

## Example prompts

> "Scaffold **order-service** with HTTP and metrics, no database."
→ `projectName=order-service`, `withHttp=yes`, `withMetrics=yes`, `withDb=no`

> "Create a **worker** — no HTTP, just a database."
→ `projectName=worker`, `withHttp=no`, `withMetrics=no`, `withDb=yes`

> "New project **api** with everything."
→ `projectName=api`, `withHttp=yes`, `withMetrics=yes`, `withDb=yes`

> "Scaffold **gateway** with HTTP and Docker, no database."
→ `projectName=gateway`, `withHttp=yes`, `withMetrics=no`, `withDb=no`, `withDocker=yes`

> "New **catalog-api** with HTTP, OpenAPI docs, and a database."
→ `projectName=catalog-api`, `withHttp=yes`, `withOpenApi=yes`, `withDb=yes`

> "Scaffold **billing-service** with a database and migrations."
→ `projectName=billing-service`, `withHttp=no`, `withDb=yes`, `withMigrations=yes`

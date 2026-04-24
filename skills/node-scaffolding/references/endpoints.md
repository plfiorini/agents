# Endpoint Layer Specs *(withHttp only)*

## Architecture

```
route → controller → service → repository
```

| Layer | Responsibility |
|---|---|
| **route** | Registers path(s) on Fastify. Validates input schemas. Delegates to controller. |
| **controller** | Reads `request`, calls service, writes `reply`. No business logic. |
| **service** | All business logic. Calls repository for data access. Framework-agnostic. |
| **repository** | All database / external I/O. Returns plain objects — never Fastify types. |
| **test** | `node:test` + `node:assert`. No extra dependencies. |

Export a named async Fastify plugin from each route file:
`export async function <endpoint>Routes(app: FastifyInstance): Promise<void>`

---

## `src/endpoints/health/`

### `health.repository.ts`
- *(withDb)* Export `checkDatabase(): Promise<boolean>` — `sequelize.authenticate()`, returns
  `true` on success, `false` on error (never throws).
- *(no withDb)* Export an empty module.

### `health.service.ts`
- Export `type HealthStatus = { status: "ok" | "degraded"; checks: Record<string, "ok" | "error"> }`.
- Export `getLiveness(): { status: "ok"; ts: string }` — always returns ok; never checks dependencies.
- Export `getReadiness(): Promise<HealthStatus>` — aggregates `checkDatabase()` when `withDb=yes`.

### `health.controller.ts`
- Export `handleLive(req, reply)` — calls `getLiveness()`, sends `200`.
- Export `handleReady(req, reply)` — calls `getReadiness()`, sends `200` when `status === "ok"` or
  `503` when `status === "degraded"`.

### `health.route.ts`
- `GET /-/health/live` → `handleLive`
- `GET /-/health/ready` → `handleReady`

### `health.test.ts`
- `getLiveness()` returns `{ status: "ok" }`.
- `getReadiness()` returns `{ status: "ok" }` when `checkDatabase` resolves `true`.
- `getReadiness()` returns `{ status: "degraded" }` when `checkDatabase` resolves `false`.

> **Liveness vs. Readiness:** `/-/health/live` must never return 503 due to a downstream failure —
> a failing liveness probe causes Kubernetes to *restart* the pod. `/-/health/ready` checks
> dependencies; a 503 removes the pod from the load balancer without restarting it.

---

## `src/endpoints/metrics/` *(withMetrics only)*

### `metrics.service.ts`
Export `scrape(): Promise<{ body: string; contentType: string }>` — calls `getMetrics()` and
`getContentType()` from `src/metrics.ts`.

### `metrics.controller.ts`
Export `handleMetrics(req, reply)` — calls `scrape()`, sets `Content-Type` header, sends `200`.

### `metrics.route.ts`
`GET /metrics` → `handleMetrics`.

### `metrics.test.ts`
Test that `scrape()` returns a non-empty string body and a non-empty `contentType`.

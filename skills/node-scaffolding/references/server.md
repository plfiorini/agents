# Server-Side Module Specs

## `src/database.ts` *(withDb only)*

- Export a `sequelize` instance: `new Sequelize(config.dbUrl, { dialect: "postgres", logging: msg => logger.debug(msg), pool: { max: 10, min: 2, acquire: 30_000, idle: 10_000 } })`.
- Export `connectDatabase(): Promise<void>` — calls `sequelize.authenticate()`, logs on success.
- Export `closeDatabase(): Promise<void>` — calls `sequelize.close()`, logs on success.

---

## `src/metrics.ts` *(withMetrics only)*

- Create and export `registry = new Registry()`.
- Call `collectDefaultMetrics({ register: registry })`.
- **Event Loop Utilization gauge** — mandatory when metrics are enabled. Use prom-client's `collect`
  callback in the `Gauge` constructor — prom-client calls it automatically on each scrape, so do
  not call it manually anywhere else:

  ```typescript
  import { performance } from "node:perf_hooks";

  let prevELU = performance.eventLoopUtilization();

  const eluGauge = new Gauge({
      name: "nodejs_event_loop_utilization_ratio",
      help: "Event loop utilisation ratio between 0 (idle) and 1 (saturated)",
      registers: [registry],
      collect() {
          const current = performance.eventLoopUtilization();
          const delta = performance.eventLoopUtilization(current, prevELU);
          prevELU = current;
          this.set(delta.utilization);
      },
  });
  ```

- When `withHttp` is `"yes"`, also export `httpRequestDuration` — a `Histogram` with labels
  `method`, `route`, `status`. Use `Histogram` (not `Gauge`) because request durations need count,
  sum, and bucket data for percentile queries (`histogram_quantile`) in Prometheus.
- Export `getMetrics(): Promise<string>` — returns `registry.metrics()`.
- Export `getContentType(): string` — returns `registry.contentType`.

---

## `src/server.ts` *(withHttp only)*

- Module-level `let isShuttingDown = false`.
- Export `buildServer()`:
  - `Fastify({ loggerInstance: logger, trustProxy: true })`.
  - `onRequest` hook: when `isShuttingDown === true`, call
    `reply.code(503).send({ error: "Service shutting down" })` and return.
  - *(withMetrics)* `onResponse` hook: record `reply.elapsedTime / 1000` into
    `httpRequestDuration` using the request's method, route url, and status code as label values.
  - Register `healthRoutes` and *(withMetrics)* `metricsRoutes`.
- Export `startServer(): Promise<void>`:
  - *(withDb)* Call `connectDatabase()` first.
  - `buildServer()` → `app.listen({ port: config.port, host: "0.0.0.0" })`.
  - `SIGTERM` / `SIGINT` shutdown sequence:
    1. `isShuttingDown = true`
    2. `await app.close()` — drains in-flight requests
    3. *(withDb)* `await closeDatabase()`
    4. `logger.info("Graceful shutdown complete")` → `process.exit(0)`
    5. On error → `logger.error(...)` → `process.exit(1)`

---

## `src/index.ts`

Copy `assets/src/index.http.ts` verbatim when `withHttp=yes`.

Copy `assets/src/index.worker.ts` as a starting point when `withHttp=no`, then adapt:
- Remove the `connectDatabase` / `closeDatabase` import line when `withDb=no`.
- Remove the `try { await connectDatabase() }` block when `withDb=no`.
- Remove `await closeDatabase()` from the `shutdown` handler when `withDb=no`.
- When `withDb=no`, `shutdown` has no async work, so it can be a plain `() => void` function.

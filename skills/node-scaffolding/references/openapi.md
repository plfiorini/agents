# OpenAPI Integration *(withOpenApi only)*

## Constraint

Requires `withHttp=yes`. Force it on if the user sets `withOpenApi=yes` without `withHttp`, and inform them.

---

## Config additions (`src/config.ts`)

Add after the `port` field:

```typescript
openapi: z.object({
    title: z.string().default("My API"),
    version: z.string().default("1.0.0"),
    description: z.string().default(""),
}).default({ title: "My API", version: "1.0.0", description: "" }),
```

In `config.yaml.example`, add below `port:`:

```yaml
openapi:
  title: My API
  version: 1.0.0
  description: ""
```

---

## `src/server.ts` additions

Add imports:

```typescript
import fastifySwagger from "@fastify/swagger";
import fastifySwaggerUi from "@fastify/swagger-ui";
```

Register **before** any route plugins inside `buildServer()` — Fastify collects JSON schemas at decoration time, so order matters:

```typescript
await app.register(fastifySwagger, {
    openapi: {
        info: {
            title: config.openapi.title,
            version: config.openapi.version,
            description: config.openapi.description,
        },
        servers: [{ url: "/" }],
    },
});

await app.register(fastifySwaggerUi, {
    routePrefix: "/documentation",
    uiConfig: { docExpansion: "list", deepLinking: true },
});

// Route registrations follow here (healthRoutes, metricsRoutes, …)
```

---

## Route schema pattern

Every route must include a `schema` object so Fastify can generate accurate OpenAPI docs. Use JSON Schema Draft-07:

```typescript
app.get("/path", {
    schema: {
        tags: ["tag"],
        summary: "One-line description",
        response: {
            200: { description: "...", type: "object", properties: { ... }, required: [...] },
        },
    },
}, handler);
```

### `/health/live`

- `tags: ["health"]`, `summary: "Kubernetes liveness probe"`
- 200: `{ status: { type: "string", enum: ["ok"] }, ts: { type: "string", format: "date-time" } }`, required: `["status", "ts"]`

### `/health/ready`

- `tags: ["health"]`, `summary: "Kubernetes readiness probe"`
- 200: `{ status: { enum: ["ok"] }, checks: { type: "object", additionalProperties: { type: "string", enum: ["ok", "error"] } } }`, required: `["status", "checks"]`
- 503: same shape but `status: { enum: ["degraded"] }`

### `/metrics` *(withMetrics + withOpenApi)*

- `tags: ["observability"]`, `summary: "Prometheus scrape endpoint"`
- 200: `{ type: "string", description: "Prometheus metrics in text/plain exposition format" }`
- Note: the handler sets `Content-Type` from `registry.contentType`; this schema declaration is for documentation only.

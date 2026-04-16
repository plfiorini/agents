# OpenAPI Integration Specs *(withOpenApi only)*

## Constraint

`withOpenApi=yes` requires `withHttp=yes`. If the user sets `withOpenApi=yes` and `withHttp=no`,
treat `withHttp` as `"yes"` and inform the user.

---

## Config additions

When `withOpenApi=yes`, extend the Zod schema in `src/config.ts` with an `openapi` object.
Add it after the `port` field (or after `logLevel` when `withHttp=no` is overridden):

```typescript
openapi: z.object({
    title: z.string().default("My API"),
    version: z.string().default("1.0.0"),
    description: z.string().default(""),
}).default({ title: "My API", version: "1.0.0", description: "" }),
```

In `config.yaml.example`, add the block below the `port:` line:

```yaml
openapi:
  title: My API
  version: 1.0.0
  description: ""
```

---

## `src/server.ts` additions

Import both plugins at the top of the file:

```typescript
import fastifySwagger from "@fastify/swagger";
import fastifySwaggerUi from "@fastify/swagger-ui";
```

Inside `buildServer()`, register them **before** any route plugins — Fastify collects JSON schemas
at decoration time, so order matters:

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
    uiConfig: {
        docExpansion: "list",
        deepLinking: true,
    },
});

// Route registrations follow here (healthRoutes, metricsRoutes, …)
```

---

## Route schema conventions

When `withOpenApi=yes`, every route must include a `schema` object so Fastify can generate
accurate OpenAPI docs. Use JSON Schema Draft-07 — Fastify's native format.

```typescript
app.get("/path", {
    schema: {
        tags: ["tag-name"],
        summary: "One-line description",
        response: {
            200: {
                description: "Success response description",
                type: "object",
                properties: { /* … */ },
                required: ["field1", "field2"],
            },
        },
    },
}, handler);
```

---

## `src/endpoints/health/health.route.ts`

Replace the bare `app.get(path, handler)` calls with schema-annotated versions:

```typescript
export async function healthRoutes(app: FastifyInstance): Promise<void> {
    app.get("/health/live", {
        schema: {
            tags: ["health"],
            summary: "Kubernetes liveness probe",
            response: {
                200: {
                    description: "Service is alive",
                    type: "object",
                    properties: {
                        status: { type: "string", enum: ["ok"] },
                        ts: { type: "string", format: "date-time" },
                    },
                    required: ["status", "ts"],
                },
            },
        },
    }, handleLive);

    app.get("/health/ready", {
        schema: {
            tags: ["health"],
            summary: "Kubernetes readiness probe",
            response: {
                200: {
                    description: "Service is ready",
                    type: "object",
                    properties: {
                        status: { type: "string", enum: ["ok"] },
                        checks: {
                            type: "object",
                            additionalProperties: { type: "string", enum: ["ok", "error"] },
                        },
                    },
                    required: ["status", "checks"],
                },
                503: {
                    description: "Service is degraded",
                    type: "object",
                    properties: {
                        status: { type: "string", enum: ["degraded"] },
                        checks: {
                            type: "object",
                            additionalProperties: { type: "string", enum: ["ok", "error"] },
                        },
                    },
                    required: ["status", "checks"],
                },
            },
        },
    }, handleReady);
}
```

---

## `src/endpoints/metrics/metrics.route.ts` *(withMetrics + withOpenApi)*

Replace the bare `app.get` call:

```typescript
app.get("/metrics", {
    schema: {
        tags: ["observability"],
        summary: "Prometheus scrape endpoint",
        response: {
            200: {
                description: "Prometheus metrics in text/plain exposition format",
                type: "string",
            },
        },
    },
}, handleMetrics);
```

> The handler already sets the correct `Content-Type` header (`registry.contentType`);
> the schema declaration here is for documentation only and does not override it.

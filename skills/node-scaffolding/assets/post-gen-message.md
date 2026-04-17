✅  Project <projectName> scaffolded.

Next steps:
  cd <projectName>
  cp config.yaml.example config.yaml   # tune base config
  cp .env.example .env                 # add secrets
  npm install
  npm run dev                          # Node 24 runs TypeScript directly

Endpoints:                             (withHttp only)
  GET /health/live                     Kubernetes liveness probe
  GET /health/ready                    Kubernetes readiness probe
  GET /metrics                         Prometheus scrape endpoint (withMetrics only)
  GET /documentation                   Swagger UI (withOpenApi only)

Migrations:                            (withMigrations only)
  npm run migrate                      Apply all pending migrations
  npm run migrate:down                 Revert last migration
  npm run migrate:pending              List unapplied migrations

Useful scripts:
  npm test                             Run tests with Node 24 type-stripping
  npm run check                        Biome lint + format
  npm run typecheck                    Type-check without running

Docker:                                (withDocker only)
  docker build -t <projectName> .
  docker run --rm --env-file .env -p 3000:3000 <projectName>

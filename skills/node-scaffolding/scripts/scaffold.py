#!/usr/bin/env python3
"""Scaffold a Node.js + TypeScript project from the node-scaffolding skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SKILL_ROOT / "assets"


@dataclass
class Options:
    project_name: str
    target_root: Path
    with_http: bool = False
    with_metrics: bool = False
    with_db: bool = False
    with_entra_id: bool = False
    with_migrations: bool = False
    with_docker: bool = False
    with_openapi: bool = False
    with_devcontainer: bool = False
    force: bool = False
    dry_run: bool = False
    notes: list[str] = field(default_factory=list)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        options = resolve_options(args)
        scaffold(options)
    except ScaffoldError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    return 0


class ScaffoldError(Exception):
    """Raised when user input or filesystem state prevents scaffolding."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scaffold a production-ready Node.js + TypeScript project.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("project_name", nargs="?", default="my-app", help="package.json name and default directory name")

    location = parser.add_mutually_exclusive_group()
    location.add_argument(
        "--workspace-root",
        action="store_true",
        help="write files directly into the current working directory",
    )
    location.add_argument(
        "--path",
        metavar="TARGET_PATH",
        help="custom target path; appends project name unless the final path already ends with it",
    )

    parser.add_argument("--http", action="store_true", help="add Fastify HTTP server and health probes")
    parser.add_argument("--metrics", action="store_true", help="add Prometheus metrics; implies --http")
    parser.add_argument("--db", action="store_true", help="add Sequelize + Postgres database module")
    parser.add_argument("--entra-id", action="store_true", help="add Azure Entra ID PostgreSQL auth; implies --db")
    parser.add_argument("--migrations", action="store_true", help="add Sequelize migrations with Umzug; implies --db")
    parser.add_argument("--docker", action="store_true", help="add Dockerfile and .dockerignore")
    parser.add_argument("--openapi", action="store_true", help="add Swagger/OpenAPI docs; implies --http")
    parser.add_argument("--devcontainer", action="store_true", help="add VS Code Dev Container configuration")
    parser.add_argument("--all", action="store_true", help="enable every optional feature")
    parser.add_argument("--force", action="store_true", help="allow writing into a non-empty target directory")
    parser.add_argument("--dry-run", action="store_true", help="print planned files without writing them")
    return parser


def resolve_options(args: argparse.Namespace) -> Options:
    project_name = args.project_name.strip()
    if not project_name:
        raise ScaffoldError("project name cannot be empty")
    if not re.fullmatch(r"@[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*|[a-z0-9][a-z0-9._-]*", project_name):
        raise ScaffoldError(
            "project name must be a valid lowercase npm package name, optionally scoped (for example my-app)"
        )

    with_http = args.http or args.all
    with_metrics = args.metrics or args.all
    with_db = args.db or args.all
    with_entra_id = args.entra_id or args.all
    with_migrations = args.migrations or args.all
    with_docker = args.docker or args.all
    with_openapi = args.openapi or args.all
    with_devcontainer = args.devcontainer or args.all

    notes: list[str] = []
    if with_metrics and not with_http:
        with_http = True
        notes.append("--metrics requires HTTP; enabling --http.")
    if with_openapi and not with_http:
        with_http = True
        notes.append("--openapi requires HTTP; enabling --http.")
    if with_migrations and not with_db:
        with_db = True
        notes.append("--migrations requires a database module; enabling --db.")
    if with_entra_id and not with_db:
        with_db = True
        notes.append("--entra-id requires a database module; enabling --db.")

    target_root = resolve_target_root(args.path, args.workspace_root, project_name)
    return Options(
        project_name=project_name,
        target_root=target_root,
        with_http=with_http,
        with_metrics=with_metrics,
        with_db=with_db,
        with_entra_id=with_entra_id,
        with_migrations=with_migrations,
        with_docker=with_docker,
        with_openapi=with_openapi,
        with_devcontainer=with_devcontainer,
        force=args.force,
        dry_run=args.dry_run,
        notes=notes,
    )


def resolve_target_root(path_arg: str | None, workspace_root: bool, project_name: str) -> Path:
    if workspace_root and path_arg:
        raise ScaffoldError("--workspace-root and --path are mutually exclusive")
    if path_arg:
        expanded = Path(path_arg).expanduser()
        if expanded.name == package_leaf(project_name):
            return expanded.resolve()
        return (expanded / package_leaf(project_name)).resolve()
    return Path.cwd().resolve()


def package_leaf(project_name: str) -> str:
    return project_name.rsplit("/", 1)[-1]


def screaming_snake(project_name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", project_name.rsplit("/", 1)[-1]).strip("_").upper()


def scaffold(options: Options) -> None:
    files = render_files(options)
    target = options.target_root

    if options.dry_run:
        print_plan(options, files)
        return

    if target.exists() and any(target.iterdir()) and not options.force:
        raise ScaffoldError(f"target directory is not empty: {target}. Use --force to write into it.")

    for relative_path, content in files.items():
        destination = target / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")

    for note in options.notes:
        print(f"note: {note}")
    print_post_generation_message(options)


def print_plan(options: Options, files: dict[str, str]) -> None:
    for note in options.notes:
        print(f"note: {note}")
    print(f"Target path: {options.target_root}")
    print("Files:")
    for relative_path in sorted(files):
        print(f"  {relative_path}")


def render_files(options: Options) -> dict[str, str]:
    files: dict[str, str] = {
        "package.json": render_package_json(options),
        "tsconfig.json": read_asset("tsconfig.json"),
        "biome.jsonc": read_asset("biome.jsonc"),
        "config.yaml.example": render_config_yaml(options),
        ".env.example": render_env_example(options),
        ".gitignore": read_asset("gitignore"),
        ".vscode/settings.json": read_asset("vscode/settings.json"),
        ".vscode/extensions.json": read_asset("vscode/extensions.json"),
        "src/index.ts": render_index(options),
        "src/config.ts": render_config_ts(options),
        "src/logger.ts": read_asset("src/logger.ts"),
    }

    if options.with_docker:
        files["Dockerfile"] = render_dockerfile(options)
        files[".dockerignore"] = read_asset("dockerignore")
    if options.with_devcontainer:
        files[".devcontainer/devcontainer.json"] = render_devcontainer(options)
    if options.with_db:
        files["src/database.ts"] = render_database_ts(options)
    if options.with_metrics:
        files["src/metrics.ts"] = render_metrics_ts(options)
    if options.with_http:
        files["src/server.ts"] = render_server_ts(options)
        files.update(render_health_endpoint(options))
    if options.with_http and options.with_metrics:
        files.update(render_metrics_endpoint(options))
    if options.with_migrations:
        files["src/migrate.ts"] = read_asset("src/migrate.ts")
        files["migrations/20240101000000-create-example.ts"] = read_asset(
            "migrations/20240101000000-create-example.ts"
        )
        files["migrations/20240101000001-create-example.up.sql"] = read_asset(
            "migrations/20240101000001-create-example.up.sql"
        )
        files["migrations/20240101000001-create-example.down.sql"] = read_asset(
            "migrations/20240101000001-create-example.down.sql"
        )

    return files


def read_asset(relative_path: str) -> str:
    return (ASSETS / relative_path).read_text(encoding="utf-8")


def render_package_json(options: Options) -> str:
    scripts = {
        "start": "node --experimental-strip-types --env-file-if-exists=.env src/index.ts",
        "dev": "node --experimental-strip-types --env-file-if-exists=.env --watch src/index.ts",
        "typecheck": "tsc --noEmit",
        "test": 'node --test --experimental-strip-types "src/**/*.test.ts"',
        "lint": "biome lint ./src",
        "format": "biome format --write ./src",
        "check": "biome check ./src",
        "check:fix": "biome check --write ./src",
    }
    if options.with_migrations:
        scripts.update(
            {
                "migrate": "node --experimental-strip-types src/migrate.ts up",
                "migrate:down": "node --experimental-strip-types src/migrate.ts down",
                "migrate:pending": "node --experimental-strip-types src/migrate.ts pending",
            }
        )

    dependencies = {
        "pino": "latest",
        "pino-pretty": "latest",
        "zod": "latest",
        "zod-config": "latest",
    }
    if options.with_http:
        dependencies.update({"fastify": "latest", "@fastify/sensible": "latest"})
    if options.with_openapi:
        dependencies.update({"@fastify/swagger": "latest", "@fastify/swagger-ui": "latest"})
    if options.with_metrics:
        dependencies["prom-client"] = "latest"
    if options.with_db:
        dependencies.update({"sequelize": "latest", "pg": "latest", "pg-hstore": "latest"})
    if options.with_db and options.with_entra_id:
        dependencies["@azure/identity"] = "latest"
    if options.with_migrations:
        dependencies["umzug"] = "latest"

    dev_dependencies = {
        "@biomejs/biome": "latest",
        "@types/node": "latest",
        "typescript": "latest",
    }
    if options.with_db:
        dev_dependencies["@types/pg"] = "latest"

    package = {
        "name": options.project_name,
        "version": "0.1.0",
        "private": True,
        "type": "module",
        "engines": {"node": ">=24.0.0"},
        "scripts": scripts,
        "dependencies": dict(sorted(dependencies.items())),
        "devDependencies": dict(sorted(dev_dependencies.items())),
    }
    return json.dumps(package, indent=4) + "\n"


def render_config_yaml(options: Options) -> str:
    lines = [
        "# Base configuration - safe to commit, no secrets.",
        "# Copy to config.yaml and adjust for your environment.",
        "",
        "env: development",
        "log:",
        "  level: info",
        "  type: pretty",
    ]
    if options.with_http:
        lines.extend(["port: 3000"])
    if options.with_openapi:
        lines.extend(
            [
                "openapi:",
                "  title: My API",
                "  version: 1.0.0",
                '  description: ""',
            ]
        )
    return "\n".join(lines) + "\n"


def render_env_example(options: Options) -> str:
    lines = [
        "# Runtime secrets and overrides - never commit this file.",
        "# Copy to .env and fill in your values.",
        "",
    ]
    if options.with_db:
        lines.append(f"{screaming_snake(options.project_name)}_DATABASE__URL=postgres://user:pass@localhost:5432/mydb")
    return "\n".join(lines).rstrip() + "\n"


def render_index(options: Options) -> str:
    if options.with_http:
        return read_asset("src/index.http.ts")
    if options.with_db:
        return read_asset("src/index.worker.with-db.ts")
    return read_asset("src/index.worker.no-db.ts")


def render_config_ts(options: Options) -> str:
    fields = [
        '    env: z.enum(["development", "production", "test"]).default("development"),',
        "    log: z.object({",
        '        level: z.enum(["fatal", "error", "warn", "info", "debug", "trace"]).default("info"),',
        '        type: z.enum(["json", "pretty"]).default("pretty"),',
        '    }).default({ level: "info", type: "pretty" }),',
    ]
    if options.with_http:
        fields.append("    port: z.coerce.number().int().min(1).max(65535).default(3000),")
    if options.with_openapi:
        fields.extend(
            [
                "    openapi: z.object({",
                '        title: z.string().default("My API"),',
                '        version: z.string().default("1.0.0"),',
                '        description: z.string().default(""),',
                '    }).default({ title: "My API", version: "1.0.0", description: "" }),',
            ]
        )
    if options.with_db:
        fields.extend(
            [
                "    database: z.object({",
                '        url: z.url("DATABASE__URL must be a valid connection URL"),',
                '        dialect: z.enum(["postgres", "mariadb"]).default("postgres"),',
                "        dialectOptions: z.record(z.string(), z.unknown()).default({}),",
                "        retry: z",
                "            .object({",
                "                max: z.coerce.number().int().min(0).default(5),",
                "                timeout: z.coerce.number().int().min(0).default(10_000),",
                "            })",
                "            .default({ max: 5, timeout: 10_000 }),",
                "        pool: z",
                "            .object({",
                "                min: z.coerce.number().int().min(0).default(2),",
                "                max: z.coerce.number().int().min(1).default(10),",
                "                acquire: z.coerce.number().int().min(0).default(30_000),",
                "                idle: z.coerce.number().int().min(0).default(10_000),",
                "            })",
                "            .default({ max: 10, min: 2, acquire: 30_000, idle: 10_000 }),",
            ]
        )
        if options.with_entra_id:
            fields.append("        useEntraId: z.boolean().default(true),")
        fields.append("    }),")

    return f'''import path from "node:path";
import {{ fileURLToPath }} from "node:url";
import {{ z }} from "zod";
import {{ loadConfig }} from "zod-config";
import {{ envAdapter }} from "zod-config/env-adapter";
import {{ yamlAdapter }} from "zod-config/yaml-adapter";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const schema = z.object({{
{chr(10).join(fields)}
}});

export type Config = z.infer<typeof schema>;

// Top-level await is valid in ESM. The process exits with a clear Zod
// validation error if any required value is missing or malformed.
export const config: Config = await loadConfig({{
    schema,
    adapters: [
        // Base defaults from the YAML file - safe to commit, no secrets.
        // Path is resolved from src/ up one level to the project root.
        yamlAdapter({{ path: path.join(__dirname, "..", "config.yaml") }}),
        // Environment variables override YAML - use for secrets and per-env values.
        // Reads only vars prefixed with {screaming_snake(options.project_name)}_ and strips that prefix before
        // mapping to schema keys. Double-underscore (__) is the nesting separator.
        envAdapter({{
            keyMatching: "lenient",
            regex: /^{screaming_snake(options.project_name)}_/,
            transform: ({{ key, value }}) => ({{
                key: key.replace(/^{screaming_snake(options.project_name)}_/, ""),
                value,
            }}),
            nestingSeparator: "__",
        }}),
    ],
}});
'''


def render_database_ts(options: Options) -> str:
    entra_import = 'import { DefaultAzureCredential } from "@azure/identity";\n' if options.with_entra_id else ""
    entra_helpers = (
        '''
const AZURE_POSTGRES_SCOPE = "https://ossrdbms-aad.database.windows.net/.default";
const TOKEN_REFRESH_BUFFER_MS = 5 * 60 * 1000;

type TokenInfo = {
    token: string;
    expiresAtMs: number;
};

async function getAzurePgToken(credential: DefaultAzureCredential): Promise<TokenInfo> {
    logger.info("Acquiring Azure Entra token for PostgreSQL...");
    const accessToken = await credential.getToken(AZURE_POSTGRES_SCOPE);
    if (!accessToken?.token || !accessToken.expiresOnTimestamp) {
        throw new Error("Failed to acquire Azure Entra token for PostgreSQL");
    }

    return {
        token: accessToken.token,
        expiresAtMs: accessToken.expiresOnTimestamp,
    };
}
'''
        if options.with_entra_id
        else ""
    )
    entra_hook = (
        '''
if (config.database.dialect === "postgres" && config.database.useEntraId) {
    const credential = new DefaultAzureCredential({
        managedIdentityClientId: process.env.AZURE_CLIENT_ID,
    });
    let cachedToken: TokenInfo | null = null;

    sequelize.addHook("beforeConnect", async (cfg: Record<string, unknown>) => {
        if (!cachedToken || cachedToken.expiresAtMs - Date.now() < TOKEN_REFRESH_BUFFER_MS) {
            cachedToken = await getAzurePgToken(credential);
        }
        cfg.password = cachedToken.token;
    });
}
'''
        if options.with_entra_id
        else ""
    )
    return f'''{entra_import}import {{ Sequelize }} from "sequelize";
import {{ config }} from "./config.ts";
import {{ logger }} from "./logger.ts";
{entra_helpers}
export const sequelize = new Sequelize(config.database.url, {{
    dialect: config.database.dialect,
    dialectOptions: config.database.dialectOptions,
    logging: msg => logger.debug(msg),
    pool: config.database.pool,
    retry: config.database.retry,
}});
{entra_hook}
export async function connectDatabase(): Promise<void> {{
    logger.info(`Connecting to "${{config.database.dialect}}" database...`);
    await sequelize.authenticate();
    logger.info("Database connection established");
}}

export async function closeDatabase(): Promise<void> {{
    logger.info("Closing database connection...");
    await sequelize.close();
    logger.info("Database connection closed");
}}
'''


def render_metrics_ts(options: Options) -> str:
    histogram = (
        '''
export const httpRequestDuration = new Histogram({
    name: "http_request_duration_seconds",
    help: "HTTP request duration in seconds",
    labelNames: ["method", "route", "status"],
    registers: [registry],
    buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
});
'''
        if options.with_http
        else ""
    )
    return f'''import {{ performance }} from "node:perf_hooks";
import {{ collectDefaultMetrics, Gauge, Histogram, Registry }} from "prom-client";

export const registry = new Registry();

collectDefaultMetrics({{ register: registry }});

let prevELU = performance.eventLoopUtilization();

const eluGauge = new Gauge({{
    name: "nodejs_event_loop_utilization_ratio",
    help: "Event loop utilisation ratio between 0 (idle) and 1 (saturated)",
    registers: [registry],
    collect() {{
        const current = performance.eventLoopUtilization();
        const delta = performance.eventLoopUtilization(current, prevELU);
        prevELU = current;
        this.set(delta.utilization);
    }},
}});

void eluGauge;
{histogram}
export async function getMetrics(): Promise<string> {{
    return registry.metrics();
}}

export function getContentType(): string {{
    return registry.contentType;
}}
'''


def render_server_ts(options: Options) -> str:
    imports = [
        'import sensible from "@fastify/sensible";',
        'import Fastify from "fastify";',
    ]
    if options.with_openapi:
        imports.extend(
            [
                'import fastifySwagger from "@fastify/swagger";',
                'import fastifySwaggerUi from "@fastify/swagger-ui";',
            ]
        )
    imports.extend(
        [
            'import { config } from "./config.ts";',
        ]
    )
    if options.with_db:
        imports.append('import { closeDatabase, connectDatabase } from "./database.ts";')
    imports.append('import { healthRoutes } from "./endpoints/health/health.route.ts";')
    if options.with_metrics:
        imports.append('import { metricsRoutes } from "./endpoints/metrics/metrics.route.ts";')
        imports.append('import { httpRequestDuration } from "./metrics.ts";')
    imports.append('import { logger } from "./logger.ts";')

    metrics_hook = (
        '''
    app.addHook("onResponse", async (request, reply) => {
        httpRequestDuration.observe(
            {
                method: request.method,
                route: request.routeOptions.url ?? request.url,
                status: String(reply.statusCode),
            },
            reply.elapsedTime / 1000,
        );
    });
'''
        if options.with_metrics
        else ""
    )
    openapi_registration = (
        '''
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
'''
        if options.with_openapi
        else ""
    )
    connect = "    await connectDatabase();\n" if options.with_db else ""
    close = "            await closeDatabase();\n" if options.with_db else ""
    metrics_route = '    await app.register(metricsRoutes, { prefix: "/-" });\n' if options.with_metrics else ""
    return f'''{chr(10).join(imports)}

let isShuttingDown = false;

export async function buildServer() {{
    const app = Fastify({{ loggerInstance: logger, trustProxy: true }});

    await app.register(sensible);

    app.addHook("onRequest", async (_request, reply) => {{
        if (isShuttingDown) {{
            return reply.code(503).send({{ error: "Service shutting down" }});
        }}
    }});
{metrics_hook}{openapi_registration}
    await app.register(healthRoutes, {{ prefix: "/-" }});
{metrics_route}
    return app;
}}

export async function startServer(): Promise<void> {{
{connect}    const app = await buildServer();
    await app.listen({{ port: config.port, host: "0.0.0.0" }});

    const shutdown = async () => {{
        try {{
            isShuttingDown = true;
            await app.close();
{close}            logger.info("Graceful shutdown complete");
            process.exit(0);
        }} catch (err) {{
            logger.error({{ err }}, "Error during shutdown");
            process.exit(1);
        }}
    }};

    process.on("SIGTERM", shutdown);
    process.on("SIGINT", shutdown);
}}
'''


def render_health_endpoint(options: Options) -> dict[str, str]:
    repository = (
        '''import { sequelize } from "../../database.ts";

export async function checkDatabase(): Promise<boolean> {
    try {
        await sequelize.authenticate();
        return true;
    } catch {
        return false;
    }
}
'''
        if options.with_db
        else "export {};\n"
    )
    db_import = 'import { checkDatabase } from "./health.repository.ts";\n\n' if options.with_db else ""
    if options.with_db:
        readiness_declaration = """export async function getReadiness(
    checkDatabaseStatus: () => Promise<boolean> = checkDatabase,
): Promise<HealthStatus> {"""
    else:
        readiness_declaration = "export async function getReadiness(): Promise<HealthStatus> {"
    readiness = (
        '''    const databaseOk = await checkDatabaseStatus();
    return {
        status: databaseOk ? "ok" : "degraded",
        checks: {
            database: databaseOk ? "ok" : "error",
        },
    };
'''
        if options.with_db
        else '    return { status: "ok", checks: {} };\n'
    )
    service = f'''{db_import}export type HealthStatus = {{
    status: "ok" | "degraded";
    checks: Record<string, "ok" | "error">;
}};

export function getLiveness(): {{ status: "ok"; ts: string }} {{
    return {{ status: "ok", ts: new Date().toISOString() }};
}}

{readiness_declaration}
{readiness}}}
'''
    controller = '''import type { FastifyReply, FastifyRequest } from "fastify";
import { getLiveness, getReadiness } from "./health.service.ts";

export async function handleLive(_request: FastifyRequest, reply: FastifyReply): Promise<void> {
    reply.code(200).send(getLiveness());
}

export async function handleReady(_request: FastifyRequest, reply: FastifyReply): Promise<void> {
    const readiness = await getReadiness();
    reply.code(readiness.status === "ok" ? 200 : 503).send(readiness);
}
'''
    live_schema = (
        '''
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
'''
        if options.with_openapi
        else ""
    )
    ready_schema = (
        '''
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
                        description: "Service is not ready",
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
'''
        if options.with_openapi
        else ""
    )
    route = f'''import type {{ FastifyInstance }} from "fastify";
import {{ handleLive, handleReady }} from "./health.controller.ts";

export async function healthRoutes(app: FastifyInstance): Promise<void> {{
    app.get(
        "/health/live",
        {{{live_schema}        }},
        handleLive,
    );

    app.get(
        "/health/ready",
        {{{ready_schema}        }},
        handleReady,
    );
}}
'''
    test = (
        '''import assert from "node:assert/strict";
import { test } from "node:test";
import { getLiveness, getReadiness } from "./health.service.ts";

test("getLiveness returns ok", () => {
    assert.equal(getLiveness().status, "ok");
});

test("getReadiness returns ok", async () => {
    const readiness = await getReadiness();
    assert.equal(readiness.status, "ok");
});
'''
        if not options.with_db
        else '''import assert from "node:assert/strict";
import { test } from "node:test";
import { getLiveness, getReadiness } from "./health.service.ts";

test("getLiveness returns ok", () => {
    assert.equal(getLiveness().status, "ok");
});

test("getReadiness returns ok when the database check succeeds", async () => {
    const readiness = await getReadiness(async () => true);
    assert.equal(readiness.status, "ok");
    assert.deepEqual(readiness.checks, { database: "ok" });
});

test("getReadiness returns degraded when the database check fails", async () => {
    const readiness = await getReadiness(async () => false);
    assert.equal(readiness.status, "degraded");
    assert.deepEqual(readiness.checks, { database: "error" });
});
'''
    )
    return {
        "src/endpoints/health/health.repository.ts": repository,
        "src/endpoints/health/health.service.ts": service,
        "src/endpoints/health/health.controller.ts": controller,
        "src/endpoints/health/health.route.ts": route,
        "src/endpoints/health/health.test.ts": test,
    }


def render_metrics_endpoint(options: Options) -> dict[str, str]:
    service = '''import { getContentType, getMetrics } from "../../metrics.ts";

export async function scrape(): Promise<{ body: string; contentType: string }> {
    return {
        body: await getMetrics(),
        contentType: getContentType(),
    };
}
'''
    controller = '''import type { FastifyReply, FastifyRequest } from "fastify";
import { scrape } from "./metrics.service.ts";

export async function handleMetrics(_request: FastifyRequest, reply: FastifyReply): Promise<void> {
    const metrics = await scrape();
    reply.header("Content-Type", metrics.contentType).code(200).send(metrics.body);
}
'''
    schema = (
        '''
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
'''
        if options.with_openapi
        else ""
    )
    route = f'''import type {{ FastifyInstance }} from "fastify";
import {{ handleMetrics }} from "./metrics.controller.ts";

export async function metricsRoutes(app: FastifyInstance): Promise<void> {{
    app.get(
        "/metrics",
        {{{schema}        }},
        handleMetrics,
    );
}}
'''
    test = '''import assert from "node:assert/strict";
import { test } from "node:test";
import { scrape } from "./metrics.service.ts";

test("scrape returns metrics body and content type", async () => {
    const metrics = await scrape();
    assert.ok(metrics.body.length > 0);
    assert.ok(metrics.contentType.length > 0);
});
'''
    return {
        "src/endpoints/metrics/metrics.service.ts": service,
        "src/endpoints/metrics/metrics.controller.ts": controller,
        "src/endpoints/metrics/metrics.route.ts": route,
        "src/endpoints/metrics/metrics.test.ts": test,
    }


def render_dockerfile(options: Options) -> str:
    dockerfile = read_asset("Dockerfile")
    if not options.with_migrations:
        dockerfile = "\n".join(
            line for line in dockerfile.splitlines() if "COPY --chown=appuser:nodejs migrations ./migrations" not in line
        )
        return dockerfile.rstrip() + "\n"
    return dockerfile


def render_devcontainer(options: Options) -> str:
    config = json.loads(read_asset("devcontainer/devcontainer.json"))
    if not options.with_http:
        config.pop("forwardPorts", None)
        config.pop("portsAttributes", None)
    return json.dumps(config, indent=4) + "\n"


def print_post_generation_message(options: Options) -> None:
    print(f"Project {options.project_name} scaffolded.")
    print(f"Output path: {options.target_root}")
    print()
    print("Next steps:")
    if options.target_root != Path.cwd().resolve():
        print(f"  cd {options.target_root}")
    print("  cp config.yaml.example config.yaml   # Tune base config")
    print("  cp .env.example .env                 # Add secrets")
    print("  npm install")
    print("  npm update --save                    # Resolve dependencies versions")
    print("  npm run dev                          # Node 24 runs TypeScript directly")
    if options.with_http:
        print()
        print("Endpoints:")
        print("  GET /-/health/live                   Kubernetes liveness probe")
        print("  GET /-/health/ready                  Kubernetes readiness probe")
        if options.with_metrics:
            print("  GET /-/metrics                       Prometheus scrape endpoint")
        if options.with_openapi:
            print("  GET /documentation                   Swagger UI")
    if options.with_migrations:
        print()
        print("Migrations:")
        print("  npm run migrate                      Apply all pending migrations")
        print("  npm run migrate:down                 Revert last migration")
        print("  npm run migrate:pending              List unapplied migrations")
    print()
    print("Useful scripts:")
    print("  npm test                             Run tests with Node 24 type-stripping")
    print("  npm run check                        Biome lint + format")
    print("  npm run typecheck                    Type-check without running")
    if options.with_docker:
        print()
        print("Docker:")
        print(f"  docker build -t {options.project_name} .")
        print(f"  docker run --rm --env-file .env -p 3000:3000 {options.project_name}")


if __name__ == "__main__":
    raise SystemExit(main())

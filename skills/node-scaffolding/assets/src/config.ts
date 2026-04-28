import path from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";
import { loadConfig } from "zod-config";
import { envAdapter } from "zod-config/env-adapter";
import { yamlAdapter } from "zod-config/yaml-adapter";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Omit fields that are not relevant to the enabled options:
//   port   — only when withHttp=yes
//   database — only when withDb=yes
//   database.useEntraId — only when withEntraId=yes
const schema = z.object({
    env: z.enum(["development", "production", "test"]).default("development"),
    log: z.object({
        level: z.enum(["fatal", "error", "warn", "info", "debug", "trace"]).default("info"),
        type: z.enum(["json", "pretty"]).default("pretty"),
    }).default({ level: "info", type: "pretty" }),
    port: z.coerce.number().int().min(1).max(65535).default(3000),
    database: z.object({
        url: z.url("DATABASE__URL must be a valid connection URL"),
        dialect: z.enum(["postgres", "mariadb"]).default("postgres"),
        dialectOptions: z.record(z.string(), z.unknown()).default({}),
        retry: z
            .object({
                max: z.coerce.number().int().min(0).default(5),
                timeout: z.coerce.number().int().min(0).default(10_000),
            })
            .default({ max: 5, timeout: 10_000 }),
        pool: z
            .object({
                min: z.coerce.number().int().min(0).default(2),
                max: z.coerce.number().int().min(1).default(10),
                acquire: z.coerce.number().int().min(0).default(30_000),
                idle: z.coerce.number().int().min(0).default(10_000),
            })
            .default({ max: 10, min: 2, acquire: 30_000, idle: 10_000 }),
        useEntraId: z.boolean().default(true),
    }),
});

export type Config = z.infer<typeof schema>;

// Top-level await is valid in ESM. The process exits with a clear Zod
// validation error if any required value is missing or malformed.
export const config: Config = await loadConfig({
    schema,
    adapters: [
        // Base defaults from the YAML file — safe to commit, no secrets.
        // Path is resolved from src/ up one level to the project root.
        yamlAdapter({ path: path.join(__dirname, "..", "config.yaml") }),
        // Environment variables override YAML — use for secrets and per-env values.
        // Reads only vars prefixed with <PROJECT_NAME>_ and strips that prefix before
        // mapping to schema keys. Double-underscore (__) is the nesting separator.
        envAdapter({
            keyMatching: "lenient",
            regex: /^<PROJECT_NAME>_/,
            transform: ({ key, value }) => ({
                key: key.replace(/^<PROJECT_NAME>_/, ""),
                // Coerce boolean-like strings so z.boolean() works without z.coerce on every field.
                value: value === "true" || value === "1" ? true : value === "false" || value === "0" ? false : value,
            }),
            nestingSeparator: "__",
        }),
    ],
});

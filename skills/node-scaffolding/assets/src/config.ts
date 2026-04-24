import path from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";
import { loadConfig } from "zod-config";
import { envAdapter } from "zod-config/env-adapter";
import { yamlAdapter } from "zod-config/yaml-adapter";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Omit fields that are not relevant to the enabled options:
//   port   — only when withHttp=yes
//   dbUrl  — only when withDb=yes
const schema = z.object({
    env: z.enum(["development", "production", "test"]).default("development"),
    log: z.object({
        level: z.enum(["fatal", "error", "warn", "info", "debug", "trace"]).default("info"),
        type: z.enum(["json", "pretty"]).default("pretty"),
    }).default({ level: "info", type: "pretty" }),
    port: z.coerce.number().int().min(1).max(65535).default(3000),
    dbUrl: z.url("DB_URL must be a valid connection URL"),
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
                value,
            }),
            nestingSeparator: "__",
        }),
    ],
});

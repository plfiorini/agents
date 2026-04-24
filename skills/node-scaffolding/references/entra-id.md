# Entra ID Database Authentication

Use this reference only when `withDb=yes` and `withEntraId=yes`.

## Config

In `src/config.ts`, include `database.useEntraId`:

```typescript
database: z.object({
    url: z.url("DATABASE__URL must be a valid connection URL"),
    dialect: z.enum(["postgres", "mariadb"]).default("postgres"),
    dialectOptions: z.record(z.string(), z.unknown()).default({}),
    useEntraId: z.boolean().default(true),
}),
```

Add `@azure/identity` to production dependencies.

## `src/database.ts`

Import `DefaultAzureCredential`:

```typescript
import { DefaultAzureCredential } from "@azure/identity";
```

Add token constants and helper near the top of the module:

```typescript
const AZURE_POSTGRES_SCOPE = "https://ossrdbms-aad.database.windows.net/.default";
const TOKEN_REFRESH_BUFFER_MS = 5 * 60 * 1000;

type TokenInfo = {
    token: string;
    expiresAtMs: number;
};

async function getAzurePgToken(credential: DefaultAzureCredential): Promise<TokenInfo> {
    const accessToken = await credential.getToken(AZURE_POSTGRES_SCOPE);
    if (!accessToken?.token || !accessToken.expiresOnTimestamp) {
        throw new Error("Failed to acquire Azure Entra token for PostgreSQL");
    }

    return {
        token: accessToken.token,
        expiresAtMs: accessToken.expiresOnTimestamp,
    };
}
```

After creating the exported `sequelize` instance, add a `beforeConnect` hook. Gate it on PostgreSQL and `config.database.useEntraId` so other dialects still use the configured password normally.

```typescript
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
```

# Migrations Module Spec

## Overview

When `withMigrations=yes`, the project uses [Umzug](https://github.com/sequelize/umzug) as a
programmatic migration runner on top of Sequelize. Umzug works natively with TypeScript and ES
Modules — no separate CLI binary or `sequelize-cli` is needed.

The migration runner supports three file types in the same `migrations/` directory:

| File pattern | Resolver |
|---|---|
| `*.ts` | `Umzug.defaultResolver` — imports the module and calls its exported `up`/`down` functions |
| `*.up.sql` | Custom resolver — reads the file and runs it via `sequelize.query()`; the matching `*.down.sql` is used for rollback |

Files execute in filename order, so the timestamp prefix (`YYYYMMDDHHMMSS-`) determines sequence
regardless of file type.

---

## `src/migrate.ts` *(withMigrations only)*

Copy verbatim from `assets/src/migrate.ts`. This is the entry point invoked by the npm scripts:

```
node --experimental-strip-types src/migrate.ts <command>
```

Supported commands:

| Command | Effect |
|---|---|
| `up` | Apply all pending migrations |
| `down` | Revert the most recently applied migration |
| `pending` | List migrations not yet applied |

Key implementation details:
- The glob `"migrations/*.{ts,up.sql}"` is resolved from the **project root** (the working
  directory when running npm scripts), so always invoke migrate scripts from the project root.
- The custom resolver only activates for `.sql` files; `.ts` files delegate to
  `Umzug.defaultResolver`.
- SQL rollback relies on a paired `*.down.sql` file with the same timestamp prefix and slug.
  If the down file is missing, `migrate:down` will throw — document this convention for the user.
- Authenticate the Sequelize connection before running any migration.
- Always call `sequelize.close()` in the `finally` block so the process exits cleanly.
- Wire Umzug's logger to pino so all migration output flows through the same structured log stream.

---

## Example migration files

### TypeScript: `migrations/20240101000000-create-example.ts`

Copy from `assets/migrations/20240101000000-create-example.ts`. Shows the required structure for
TS/JS migrations:
- Export `up: MigrationFn<QueryInterface>` and `down: MigrationFn<QueryInterface>`.
- Import `DataTypes` from `sequelize` for column type definitions.
- Import `MigrationFn` and `QueryInterface` as type-only imports.

### SQL: `migrations/20240101000001-create-example.up.sql` + `.down.sql`

Copy from `assets/migrations/20240101000001-create-example.up.sql` and
`assets/migrations/20240101000001-create-example.down.sql`. Shows the SQL migration convention:
- The `.up.sql` file contains the forward migration.
- A matching `.down.sql` file (same name, `.up.sql` → `.down.sql`) must exist for rollback.
- The glob only matches `*.up.sql`; the down file is loaded by the resolver at rollback time.

Inform the user that both example migrations are starters to replace or remove once they have their
own schema.

---

## npm scripts *(withMigrations only)*

Add these scripts to `package.json`:

| Script | Command |
|---|---|
| `migrate` | `node --experimental-strip-types src/migrate.ts up` |
| `migrate:down` | `node --experimental-strip-types src/migrate.ts down` |
| `migrate:pending` | `node --experimental-strip-types src/migrate.ts pending` |

---

## Dependencies *(withMigrations only)*

| Package | Type |
|---|---|
| `umzug` | dependency |

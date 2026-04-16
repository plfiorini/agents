import { readFileSync } from "node:fs";
import { Umzug, SequelizeStorage } from "umzug";
import { sequelize } from "./database.ts";
import { logger } from "./logger.ts";

const umzug = new Umzug({
    migrations: {
        glob: "migrations/*.{ts,up.sql}",
        resolve: params => {
            // SQL migrations are resolved manually; JS/TS use Umzug's built-in loader.
            if (!params.path.endsWith(".sql")) {
                return Umzug.defaultResolver(params);
            }
            const { context: queryInterface } = params;
            return {
                name: params.name,
                up: async () => {
                    const sql = readFileSync(params.path).toString();
                    return queryInterface.sequelize.query(sql);
                },
                down: async () => {
                    const sql = readFileSync(params.path.replace(".up.sql", ".down.sql")).toString();
                    return queryInterface.sequelize.query(sql);
                },
            };
        },
    },
    context: sequelize.getQueryInterface(),
    storage: new SequelizeStorage({ sequelize }),
    logger: {
        info: (msg: Record<string, unknown>) => logger.info(msg),
        warn: (msg: Record<string, unknown>) => logger.warn(msg),
        error: (msg: Record<string, unknown>) => logger.error(msg),
        debug: (msg: Record<string, unknown>) => logger.debug(msg),
    },
});

const command = process.argv[2];

try {
    await sequelize.authenticate();

    if (command === "up") {
        await umzug.up();
        logger.info("All pending migrations applied");
    } else if (command === "down") {
        await umzug.down();
        logger.info("Last migration reverted");
    } else if (command === "pending") {
        const pending = await umzug.pending();
        if (pending.length === 0) {
            logger.info("No pending migrations");
        } else {
            logger.info({ migrations: pending.map(m => m.name) }, `${pending.length} pending migration(s)`);
        }
    } else {
        logger.error(`Unknown command: ${command ?? "(none)"}. Usage: up | down | pending`);
        process.exit(1);
    }

    process.exit(0);
} catch (err) {
    logger.fatal({ err }, "Migration failed");
    process.exit(1);
} finally {
    await sequelize.close();
}

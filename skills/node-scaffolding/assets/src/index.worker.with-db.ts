import { logger } from "./logger.ts";
import { connectDatabase, closeDatabase } from "./database.ts";

try {
    await connectDatabase();
} catch (err) {
    logger.fatal({ err }, "Fatal startup error");
    process.exit(1);
}

const shutdown = async () => {
    try {
        await closeDatabase();
        logger.info("Graceful shutdown complete");
        process.exit(0);
    } catch (err) {
        logger.error({ err }, "Error during shutdown");
        process.exit(1);
    }
};

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);

logger.info("Worker started");

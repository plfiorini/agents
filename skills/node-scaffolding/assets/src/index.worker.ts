import { logger } from "./logger.ts";
import { connectDatabase, closeDatabase } from "./database.ts"; // omit when withDb=no

try {
    await connectDatabase(); // omit when withDb=no
} catch (err) {
    logger.fatal({ err }, "Fatal startup error");
    process.exit(1);
}

// When withDb=no: remove `async`, remove the try/catch body, keep only the process.exit(0) call.
const shutdown = async () => {
    try {
        await closeDatabase(); // omit when withDb=no
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

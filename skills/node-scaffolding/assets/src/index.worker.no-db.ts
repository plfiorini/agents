import { logger } from "./logger.ts";

const shutdown = () => {
    logger.info("Graceful shutdown complete");
    process.exit(0);
};

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);

logger.info("Worker started");

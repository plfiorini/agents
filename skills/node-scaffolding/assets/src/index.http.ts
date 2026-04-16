import { logger } from "./logger.js";
import { startServer } from "./server.js";

try {
    await startServer();
} catch (err) {
    logger.fatal({ err }, "Fatal startup error");
    process.exit(1);
}

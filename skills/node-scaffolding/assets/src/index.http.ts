import { logger } from "./logger.ts";
import { startServer } from "./server.ts";

try {
    await startServer();
} catch (err) {
    logger.fatal({ err }, "Fatal startup error");
    process.exit(1);
}

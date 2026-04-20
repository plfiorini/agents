import pino from "pino";
import { config } from "./config.ts";

const lokiLogLevelMapping: Record<number, string> = {
    10: "trace",
    20: "debug",
    30: "info",
    40: "warn",
    50: "error",
    60: "fatal",
};

export const logger = pino({
    level: config.log.level,
    ...(config.log.type === "pretty"
        ? { transport: { target: "pino-pretty", options: { colorize: true } } }
        : {
              formatters: {
                  // Map Pino log levels to Loki log levels for better compatibility with Loki's expected log level labels
                  // See https://github.com/Julien-R44/pino-loki?tab=readme-ov-file#levelmap
                  level: (label: string, number: number) => ({
                      level: lokiLogLevelMapping[number] || label,
                      log_level: number,
                  }),
              },
          }),
});

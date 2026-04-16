# Stage 1: production dependencies
FROM node:24-alpine AS deps
WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

# Stage 2: runtime image
FROM node:24-alpine AS runtime
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup -S -g 1001 nodejs \
 && adduser  -S -u 1001 -G nodejs appuser

COPY --chown=appuser:nodejs --from=deps /app/node_modules ./node_modules
COPY --chown=appuser:nodejs src ./src
COPY --chown=appuser:nodejs package.json ./

USER appuser

CMD ["node", "--experimental-strip-types", "src/index.ts"]

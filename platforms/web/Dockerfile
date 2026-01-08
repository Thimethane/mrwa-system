# ============================================================================
# Frontend Dockerfile - MRWA Next.js (Docker-first, no local Node needed)
# ============================================================================

# ----------------------------
# Stage 1: Builder
# ----------------------------
# Docker automatically pulls this image
FROM node:18-alpine AS builder

WORKDIR /app

# Environment
ENV NODE_ENV=development \
    NEXT_TELEMETRY_DISABLED=1

# System dependencies
RUN apk add --no-cache bash curl git

# Copy dependency files first (cache layer)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build application
RUN npm run build


# ----------------------------
# Stage 2: Production
# ----------------------------
# Docker automatically pulls this image
FROM node:18-alpine

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# System dependencies
RUN apk add --no-cache bash curl

# Copy runtime files
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./next.config.js

# Entrypoint
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/docker-entrypoint.sh"]

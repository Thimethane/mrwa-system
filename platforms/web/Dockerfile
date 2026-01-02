# ============================================================================ 
# platforms/web/Dockerfile - Frontend Container (Production-ready)
# ============================================================================

# Use a stable Node 18 LTS Alpine image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Set environment variables to avoid warnings
ENV NODE_ENV=production \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    NEXT_TELEMETRY_DISABLED=1

# Install system dependencies (if needed)
RUN apk add --no-cache bash curl git

# Copy package files first to leverage Docker cache
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production

# Copy the rest of the app code
COPY . .

# Build Next.js for production
RUN npm run build

# Expose port 3000
EXPOSE 3000

# Use a lightweight shell script to handle signals properly
# This avoids the "ERR_INVALID_ARG_TYPE: 'SIGINT'" error
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]

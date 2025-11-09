# Frontend Dockerfile for The Hive
# Multi-stage build for development and production

# Development stage
FROM node:20-alpine AS development

WORKDIR /app

# Copy package files first
COPY package*.json ./

# Install dependencies during build
RUN npm install

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Install dependencies on startup to handle volume mounts
# Then start dev server with host exposed for Docker
CMD ["sh", "-c", "npm install && npm run dev -- --host"]

# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine AS production

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

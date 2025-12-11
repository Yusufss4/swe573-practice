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

# Accept build arguments for Vite environment variables
ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ARG VITE_MAP_DEFAULT_LAT=41.0082
ARG VITE_MAP_DEFAULT_LNG=28.9784
ARG VITE_MAP_DEFAULT_ZOOM=12

# Set as environment variables for Vite build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_MAP_DEFAULT_LAT=$VITE_MAP_DEFAULT_LAT
ENV VITE_MAP_DEFAULT_LNG=$VITE_MAP_DEFAULT_LNG
ENV VITE_MAP_DEFAULT_ZOOM=$VITE_MAP_DEFAULT_ZOOM

# Copy package files
COPY package*.json ./

# Install all dependencies (including devDependencies needed for build)
RUN npm ci

# Copy source code
COPY . .

# Build application (Vite will use the environment variables)
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

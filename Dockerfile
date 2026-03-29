FROM node:22-alpine
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@10.33.0 --activate
EXPOSE 5173
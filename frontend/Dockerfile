# PlantCare frontend — multi-stage: build with Node, serve with nginx
FROM docker.io/library/node:22-slim AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
# VITE_API_URL is baked at build time; default targets the compose service.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

FROM docker.io/library/nginx:1.27-alpine AS runtime

# SPA fallback so /plants, /dashboard, etc. resolve to index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

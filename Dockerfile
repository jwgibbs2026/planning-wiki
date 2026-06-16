# syntax=docker/dockerfile:1
#
# One image that serves the whole site (Toolkit Guide + Planning Wiki + Map).
#
#   Stage 1 (Node)  — build the Quartz wiki from wiki-src/ into static HTML.
#   Stage 2 (Python)— run the FastAPI app, which serves the guide, the built
#                     wiki, and the map/API from a single port.

# ---- Stage 1: build the Quartz wiki -----------------------------------------
FROM node:22-slim AS wiki
WORKDIR /wiki

# Install deps first (better layer caching), mirroring Quartz's own Dockerfile.
COPY wiki-src/package.json wiki-src/package-lock.json* wiki-src/quartz.lock.json ./
COPY wiki-src/quartz/ ./quartz/
RUN npm ci && npx quartz plugin install

# Bring in the rest (content, configs) and build to /wiki/public.
COPY wiki-src/ ./
RUN npx quartz build

# ---- Stage 2: the Python app ------------------------------------------------
FROM python:3.12-slim AS app
WORKDIR /app

COPY dashboard/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code (+ seed planning.sqlite that ships inside dashboard/data/).
COPY dashboard/ ./dashboard/

# The wiki built in stage 1.
COPY --from=wiki /wiki/public ./wiki_public
ENV PLANNING_WIKI_PUBLIC_DIR=/app/wiki_public

# Render provides $PORT; default to 8000 for local `docker run`.
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn planning_dashboard.api:app --app-dir /app/dashboard --host 0.0.0.0 --port ${PORT}"]

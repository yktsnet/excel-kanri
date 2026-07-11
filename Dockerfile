# --- frontend build stage ---
FROM node:26-slim AS frontend-builder
WORKDIR /build

COPY package.json package-lock.json ./
RUN npm ci

COPY tsconfig.json vite.config.ts tailwind.config.js postcss.config.js ./
COPY frontend/ frontend/
RUN npm run build

# --- backend runtime stage ---
FROM python:3.13-slim AS backend
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY packages/ packages/
COPY examples/ examples/
COPY --from=frontend-builder /build/frontend/dist frontend/dist

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

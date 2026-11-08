# Estágio 1: build estático do front-end (Vite + React)
FROM node:22-alpine AS front
WORKDIR /app/web/app
COPY web/app/package.json web/app/package-lock.json ./
RUN npm ci
COPY web/app/ ./
RUN npm run build

# Estágio 2: runtime Python (FastAPI serve a API e o build estático)
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements-web.txt ./
RUN pip install --no-cache-dir -r requirements-web.txt

COPY compilador/ ./compilador/
COPY web/__init__.py ./web/__init__.py
COPY web/api/ ./web/api/
COPY examples/ ./examples/
COPY --from=front /app/web/app/dist ./web/app/dist

RUN useradd --system --uid 10001 --no-create-home tupa
USER tupa

EXPOSE 8000
CMD ["uvicorn", "web.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

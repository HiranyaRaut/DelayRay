#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "   DelayRay: AI Early Warning System Demo Launcher"
echo "=========================================================="

echo "[1/4] Checking environment..."
if ! command -v docker &> /dev/null; then
    echo "Error: docker is not installed or not in PATH."
    exit 1
fi

echo "[2/4] Starting multi-container stack via Docker Compose..."
docker compose up --build -d

echo "[3/4] Waiting for backend API to be healthy..."
until curl -s http://localhost:8000/health | grep -q "healthy"; do
    echo "Waiting for DelayRay API (http://localhost:8000/health)..."
    sleep 3
done

echo "[4/4] DelayRay is live!"
echo "=========================================================="
echo "   Dashboard Web UI:   http://localhost:8080"
echo "   FastAPI Swagger:    http://localhost:8000/docs"
echo "   API Health Check:   http://localhost:8000/health"
echo "   Demo Credentials:   viewer@demo / demo123"
echo "                       analyst@demo / demo123"
echo "                       admin@demo / demo123"
echo "=========================================================="

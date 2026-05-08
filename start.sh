#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Starting App services..."

# Démarrer postgres et backend avec docker compose
docker compose up --build -d

# Démarrer le frontend en parallèle (Vite dev server)
cd frontend
npm run dev &
#!/bin/bash

cd "$(dirname "$0")"

echo "Stopping App services..."

# Stop frontend (Vite on port 1420)
VITE_PIDS=$(lsof -ti:1420 2>/dev/null | grep -v "^$$\$")
if [ -n "$VITE_PIDS" ]; then
  echo "$VITE_PIDS" | xargs kill -TERM 2>/dev/null
  echo "✓ Frontend stopped"
else
  echo "- Frontend not running"
fi

# Stop postgres and backend
docker compose down
echo "✓ Docker services stopped"

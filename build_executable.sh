#!/bin/bash
set -e

echo "Building frontend..."
cd frontend
pnpm install
pnpm build
cd ..

echo "Copying frontend dist to backend..."
mkdir -p backend/app/static/dist
cp -r frontend/dist/* backend/app/static/dist/

echo "Packaging backend with PyInstaller..."
cd backend
uv run pyinstaller --onefile --name MiroFish --add-data "app/static/dist:app/static/dist" run.py
cd ..

echo "Build complete. Executable is at backend/dist/MiroFish"

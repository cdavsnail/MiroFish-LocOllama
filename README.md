<div align="center">

<img src="./static/image/MiroFish_logo_compressed.jpeg" alt="MiroFish Logo" width="75%"/>

<a href="https://trendshift.io/repositories/16144" target="_blank"><img src="https://trendshift.io/api/badge/repositories/16144" alt="666ghj%2FMiroFish | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

简洁通用的群体智能引擎，预测万物 (Local-First Edition)
</br>
<em>A Simple and Universal Swarm Intelligence Engine, Predicting Anything</em>

<a href="https://www.shanda.com/" target="_blank"><img src="./static/image/shanda_logo.png" alt="666ghj%2MiroFish | Shanda" height="40"/></a>

[![GitHub Stars](https://img.shields.io/github/stars/666ghj/MiroFish?style=flat-square&color=DAA520)](https://github.com/666ghj/MiroFish/stargazers)
[![GitHub Watchers](https://img.shields.io/github/watchers/666ghj/MiroFish?style=flat-square)](https://github.com/666ghj/MiroFish/watchers)
[![Docker](https://img.shields.io/badge/Docker-Build-2496ED?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/)

[English](./README.md) | [中文文档](./README-ZH.md)

</div>

## ⚡ Overview

**MiroFish** is a next-generation AI prediction engine powered by multi-agent technology.
This version has been **refactored for true local-first, zero-cost operation**. We have removed external cloud dependencies (like Zep Cloud) and made it seamless to run locally using [Ollama](https://ollama.com).

## 🚀 Quick Start (Local-First Ollama)

We have decoupled the project from paid cloud services. Everything now runs locally by default!

### Prerequisites

| Tool | Description | Check |
|------|-------------|-------|
| **Node.js** | Frontend runtime | `node -v` |
| **Python** | Backend runtime (3.11/3.12) | `python --version` |
| **uv** | Python package manager | `uv --version` |
| **Ollama** | Local LLM engine | `ollama -v` |

### 1. Setup Ollama

First, install [Ollama](https://ollama.com/) on your machine. Start Ollama and pull your preferred model (we recommend `llama3` or `qwen2`).
```bash
ollama run llama3 &
```

### 2. Configure the Environment

Copy the environment example file. It is already pre-configured to use Ollama!

```bash
cp .env.example .env
```

Your `.env` should look like this:
```env
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL_NAME=llama3
```

### 3. Install Dependencies & Start Services

You can install all dependencies and start the backend and frontend easily.

```bash
# One-click installation
npm run setup:all

# Start both frontend and backend
npm run dev &
```

**Service URLs:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

**Backend-Only Mode:**
You can also run just the backend if you prefer not to start the frontend:
```bash
npm run backend &
```

## 🏗️ Deployment Notes (Vercel)

- **Frontend (Vue/Vite)**: Fully compatible with Vercel! You can deploy the contents of the `frontend/` folder directly to Vercel.
- **Backend (Flask/Python)**: **NOT recommended for Vercel.** The backend performs long-running background tasks, stateful local file system writes, and parallel Agent loops (via OASIS). Vercel's serverless functions are a poor fit for this. For production, we recommend hosting the backend on a VPS or via Docker (see `docker-compose.yml`), and connecting your Vercel-deployed frontend to that URL.

## 📄 Acknowledgments

MiroFish's simulation engine is powered by **[OASIS (Open Agent Social Interaction Simulations)](https://github.com/camel-ai/oasis)**.

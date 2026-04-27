# MiroFish Refactor - Audit Summary & Technical Notes

## 1. Audit Summary

### Identified Constraints & Blockers
*   **Model providers:** Previously forced the use of paid OpenAI-compatible APIs (defaulted to Ali Qwen-plus).
*   **Cloud/hosted dependencies:** Heavily dependent on `zep-cloud` for Knowledge Graph, Entity Extraction, and Simulation History Storage.
*   **Paid dependencies:** `zep-cloud` (requires API key) and hosted LLMs.
*   **Required services:** Frontend (Node.js/Vue) and Backend (Python/Flask).

### What made the repo hard to use?
*   Requiring users to register for Zep Cloud and obtain API keys just to run a basic demo.
*   No clear path to run completely zero-cost.
*   High cost of LLM tokens for full graph processing if using paid models.

## 2. Refactor Implementation & Changes Made

*   **Zep Cloud Decoupling:** We completely removed the `zep-cloud` dependency from `requirements.txt` and `pyproject.toml`.
*   **Local Graph Mock:** Created a `LocalGraph` mock (`backend/app/services/local_memory/`) to replace Zep. It simulates the Graph API by persisting data locally in JSON format to `backend/uploads/graphs/`.
*   **Local Entity Extraction:** The Zep Mock automatically intercepts batch insertion and triggers an internal entity extraction using the user's defined `LLM_MODEL_NAME` (Ollama by default).
*   **Ollama Defaults:** Updated `.env.example` and instructions to default to `http://localhost:11434/v1` and `llama3`.
*   **Optional Frontend:** The Flask backend will successfully boot and run API simulations completely independently of the frontend.

## 3. Vercel Evaluation Verdict

*   **Frontend:** The `frontend/` (Vue/Vite) directory can be cleanly separated and pushed to Vercel without modifications. It acts purely as a REST client.
*   **Backend:** The `backend/` directory **cannot and should not be run on Vercel**.
    *   **Why?** The backend relies heavily on `threading.Thread` for parallel execution of Agent simulations (via `camel-oasis`). Vercel Serverless Functions have strict timeouts (usually 10-60s) and do not support long-running daemon processes.
    *   Additionally, the backend creates stateful directories (`backend/uploads/simulations/` and `backend/uploads/graphs/`) and uses an embedded SQLite database for agent messages, which violates Vercel's ephemeral file system constraints.
    *   **Realistic Split Architecture:** Host the frontend on Vercel, but host the backend as a standard Docker container on a VPS, configuring CORS appropriately.

## 4. Remaining Limitations
*   The `LocalGraph` mock is a simplistic drop-in replacement. Complex semantic search capabilities of Zep have been downgraded to basic substring keyword searches over the local JSON edges/nodes.
*   Simulations might take significantly longer locally if your hardware runs Ollama slowly, as the `camel-oasis` multi-agent loop is highly talkative.

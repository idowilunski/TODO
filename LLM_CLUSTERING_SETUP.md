# LLM Task Clustering Setup

## Quick Start

### 1. Install Dependencies
```bash
cd apps/server
pip install -r requirements.txt
```

### 2. Get OpenAI API Key
1. Go to https://platform.openai.com/api/keys
2. Create a new API key
3. Set environment variable:
   ```bash
   # Windows (bash)
   export OPENAI_API_KEY="sk-your-api-key-here"
   
   # Or create a .env file in apps/server/
   echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
   ```

### 3. Run the Server
```bash
cd apps/server
source venv/Scripts/activate  # if using venv
python run.py
```

### 4. Start the Frontend
```bash
cd apps/front
npm start
```

### 5. Load Mock Data & Test Clustering
1. Open http://localhost:3000
2. Click **"Load 70 Mock Tasks"** to populate test data
3. Click **"Cluster Tasks with AI"** to see LLM-generated categories

---

## Architecture: LLM Provider Switching

The app uses an abstraction layer to support multiple LLM providers with minimal code changes.

### Current Providers

**OpenAI (Default)**
- Fast, high quality
- Costs ~$0.001–0.01 per call
- No setup beyond API key

**Ollama (Local, Free)**
- Runs entirely locally
- No API key needed
- Slower but free

### Switching to Ollama

**Step 1:** Install Ollama
```bash
# Download from https://ollama.ai
# Then download a model:
ollama pull llama2  # ~4GB
ollama serve  # Keeps running on http://localhost:11434
```

**Step 2:** Set Environment Variables
```bash
export LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama2
```

**Step 3:** Restart the backend
```bash
python run.py
```

That's it! No code changes needed. The abstraction handles provider switching.

---

## How It Works

### Backend Flow
1. **Frontend calls:** `POST /api/tasks/cluster`
2. **Backend:**
   - Gets all tasks from DB
   - Calls `TaskClusteringService.cluster_tasks(tasks)`
   - `TaskClusteringService` gets LLM provider via `LLMServiceFactory.get_provider()`
   - Provider (OpenAI or Ollama) clusters the tasks
   - Returns: `{ clusters: { "Work": [...], "Home": [...] } }`
3. **Frontend displays** clustered tasks grouped by category

### Provider Interface (Abstract)
All providers inherit from `LLMProvider` and implement:
```python
def cluster_tasks(self, task_descriptions: List[str], task_titles: List[str]) -> Dict[str, List[str]]
```

This ensures swapping providers requires only 1 line change (`LLM_PROVIDER` env var).

---

## Troubleshooting

**Error: `OPENAI_API_KEY environment variable not set`**
- Set the API key:
  ```bash
  export OPENAI_API_KEY="sk-..."
  ```

**Error: `Cannot connect to Ollama`**
- Make sure Ollama is running:
  ```bash
  ollama serve
  ```
- Verify it's accessible:
  ```bash
  curl http://localhost:11434/api/tags
  ```

**Error: `Invalid JSON from LLM`**
- The LLM sometimes returns malformed JSON. If it happens frequently, try:
  - Adjusting the `temperature` (currently 0.5) in `llm_service.py`
  - Using a more recent model
  - Improving the prompt

**Clustering takes a long time**
- OpenAI is usually <5 seconds
- Ollama on CPU can take 30–60 seconds
- If using Ollama, consider GPU acceleration

---

## Cost Estimate (OpenAI)

- ~50 tasks: $0.0005 per call
- ~500 tasks: $0.003 per call
- ~5000 tasks: $0.02 per call

At typical usage (<10 clusters/day), cost is negligible (<$1/month).

---

## Next Steps

- Add UI to edit/refine cluster assignments
- Cache clustering results to avoid repeated LLM calls
- Add support for custom category names
- Implement incremental clustering (only re-cluster new tasks)
- Add task count and estimated cost display

---

## Files Modified

- **Backend:**
  - `apps/server/app/services/llm_service.py` (NEW) — LLM abstraction
  - `apps/server/app/routes/tasks.py` — Added `/seed` and `/cluster` endpoints
  - `apps/server/requirements.txt` — Added `openai` and `requests`

- **Frontend:**
  - `apps/front/src/services/api.ts` — Added `seedMockTasks()`, `clusterTasks()`
  - `apps/front/src/App.tsx` — Added clustering UI, state, and handlers

---

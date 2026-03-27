# TODO

Quick start (Windows bash)

- Backend (Flask):
	- Copy env template then edit keys as needed.
		- What: Provide app secrets and LLM provider config
		- Why: `apps/server/run.py` loads `.env` on startup

```
cp apps/server/.env.example apps/server/.env
nano apps/server/.env
```

	- Create/activate venv and install dependencies.
		- What: Isolate Python packages per-project
		- Why: Avoid global conflicts and ensure reproducibility

```
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r apps/server/requirements.txt
```

	- Run the server (port 5001).
		- What: Starts Flask API and creates SQLite DB under `apps/server/instance`
		- Why: Backend for tasks CRUD and clustering endpoints

```
python apps/server/run.py
```

- Frontend (React):
	- Install and start.
		- What: Installs Node deps and starts CRA dev server
		- Why: UI to interact with the backend

```
cd apps/front
npm ci
npm start
```

Notes
- Backend env file lives at `apps/server/.env`. Do not commit it; use `apps/server/.env.example` as a template.
- Default frontend calls the API at `http://localhost:5001`. If you change the backend port, update `apps/front/src/services/api.ts`.
- To avoid CORS in dev, you can add `"proxy": "http://localhost:5001"` to `apps/front/package.json` and restart `npm start`.
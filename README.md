# Monopoly-backend

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Deploy on Render

Use the included `render.yaml`, or configure the service with:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Do not use `pipenv install --deploy` on Render. The Pipfile is for local development;
Render should install from `requirements.txt` directly.

The frontend should connect to the deployed service with a secure WebSocket URL:
`wss://<your-render-service>.onrender.com/ws/<room-id>`.
# Real-Time Chat Application

A room-based browser chat built with Flask and Flask-SocketIO. Connected clients in the same room receive messages in real time.

## Requirements

- Python 3.10+
- Flask 3.x
- Flask-SocketIO 5.x

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in two browser tabs, choose a display name, join the same room, and send a message.

## Configuration

| Variable | Purpose |
| --- | --- |
| `CHAT_SECRET_KEY` | Strong random secret used to sign session cookies. Required when `APP_ENV=production`. |
| `APP_ENV` | Set to `production` to reject the built-in development secret. |
| `CHAT_ALLOWED_ORIGINS` | Optional comma-separated allowlist for trusted cross-origin browser origins. Without it, the Socket.IO server uses its same-origin default. |
| `COOKIE_SECURE` | Set to `1` when served over HTTPS so session cookies use the Secure attribute. |
| `HOST` | Bind address; defaults to `127.0.0.1` for local development. |
| `PORT` | Listening port; defaults to `5000`. |

Example production environment (use your platform's secret manager; do not commit secrets):

```bash
APP_ENV=production
CHAT_SECRET_KEY=<generate-a-long-random-secret>
COOKIE_SECURE=1
CHAT_ALLOWED_ORIGINS=https://chat.example.com
HOST=0.0.0.0
PORT=5000
```

## Security controls in this demo

- Session cookies are HttpOnly and SameSite=Lax; Secure cookies can be enabled for HTTPS.
- Production startup refuses the built-in development secret.
- Cross-origin access is not opened by default; trusted origins can be explicitly allowlisted.
- Socket.IO incoming payload size is capped, room names are validated, and names/messages have strict length and type checks.
- Chat content is rendered with DOM `textContent`, not inserted as HTML.

## Limitations and production deployment

This remains a learning/demo application, **not a production-ready public chat service**. It does not provide user authentication or identity verification, authorization/ownership for rooms, rate limiting, moderation/reporting, message persistence, audit logging, monitoring/alerting, or a multi-worker message queue. Display names are user supplied and can be impersonated.

Before exposing it publicly, add those controls, run a deployment-specific security review, configure HTTPS and trusted origins, and deploy with a supported production WSGI/Socket.IO stack. Do not use Flask's development server for production. The included CI checks unit behavior on Python 3.10, 3.11, and 3.12; a passing CI run is not a production security certification.

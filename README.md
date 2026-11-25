# Real-Time Chat Application

A room-based browser chat using Flask-SocketIO. Connected clients in the same room receive messages live.

## Requirements
- Python 3.10+
- Flask
- Flask-SocketIO

## Local development
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 in two browser tabs, join the same room, and send a message.

## Configuration
- Set `CHAT_SECRET_KEY` to a long random secret before deployment.
- Set `APP_ENV=production` to reject the development secret.
- Set `CHAT_ALLOWED_ORIGINS` to a comma-separated allowlist of trusted browser origins.
- Set `COOKIE_SECURE=1` when served over HTTPS.
- Set `HOST` and `PORT` for the deployment platform.

## Security and limitations
This is a learning/demo service, not a fully production-hardened public chat platform. It has no user authentication, identity verification, moderation, persistence, abuse throttling, or horizontal scaling adapter. Display names are user supplied and can be impersonated. Deploy behind HTTPS and a production WSGI/Socket.IO deployment stack; add authentication, rate limits, moderation, monitoring, and persistent storage before public use. Do not use the Flask development server for production.

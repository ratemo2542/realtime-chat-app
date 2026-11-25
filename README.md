# Real-Time Chat Application

A small browser-based room chat built with Flask-SocketIO. Messages are broadcast live to connected clients in the same room.

## Requirements
- Python 3.10+
- Flask
- Flask-SocketIO
- Eventlet

## Run
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 in two browser tabs, enter the same room and send messages.

## Important limitations
This is a learning demo. It has no authentication, message persistence, moderation, or production security hardening. Do not expose it publicly without adding those controls.

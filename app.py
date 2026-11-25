""""A minimal room-based real-time chat demo with conservative defaults."""
import os
import re

from flask import Flask, render_template_string, session
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("CHAT_SECRET_KEY", "development-only-change-me"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    MAX_CONTENT_LENGTH=16 * 1024,
)

if (
    app.config["SECRET_KEY"] == "development-only-change-me"
    and os.environ.get("APP_ENV", "").lower() == "production"
):
    raise RuntimeError("Set CHAT_SECRET_KEY to a strong secret in production.")

allowed_origins = [
    origin.strip()
    for origin in os.environ.get("CHAT_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
# None keeps the default same-origin policy. Cross-origin access must be
# explicitly enabled with CHAT_ALLOWED_ORIGINS.
socketio = SocketIO(
    app,
    async_mode="threading",
    cors_allowed_origins=allowed_origins or None,
    max_http_buffer_size=16 * 1024,
)

PAGE = """<!doctype html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'><title>Room Chat</title>
<style>body{font:16px system-ui;background:#10121b;color:#eee;max-width:720px;margin:35px auto;padding:0 16px}main{background:#1b2030;padding:24px;border-radius:16px}#messages{height:360px;overflow:auto;background:#101522;padding:14px;border-radius:10px;list-style:none}input{padding:12px;border-radius:8px;border:0}#name,#room{width:28%}#message{width:58%}button{padding:12px;background:#9b8cff;border:0;border-radius:8px}</style></head><body><main><h1>Room Chat</h1>
<p><input id='name' placeholder='Your name' maxlength='24'><input id='room' placeholder='Room' value='general' maxlength='32'><button id='join'>Join</button></p>
<ul id='messages'></ul><form id='form'><input id='message' placeholder='Write a message...' maxlength='500' required><button>Send</button></form><p id='status'>Not connected to a room.</p></main>
<script src='https://cdn.socket.io/4.7.5/socket.io.min.js'></script><script>
const socket=io();let activeRoom='';
const messages=document.getElementById('messages');
function addLine(text){const li=document.createElement('li');li.textContent=text;messages.appendChild(li);messages.scrollTop=messages.scrollHeight;}
document.getElementById('join').onclick=()=>{const name=document.getElementById('name').value.trim();activeRoom=document.getElementById('room').value.trim();if(!name||!activeRoom)return alert('Enter a name and room.');socket.emit('join',{name,room:activeRoom});messages.replaceChildren();document.getElementById('status').textContent='Joining '+activeRoom;};
document.getElementById('form').onsubmit=e=>{e.preventDefault();const input=document.getElementById('message');if(activeRoom&&input.value.trim()){socket.emit('message',{text:input.value.trim()});input.value='';}};
socket.on('connect',()=>document.getElementById('status').textContent='Connected');
socket.on('message',data=>addLine(data.name+': '+data.text));
socket.on('notice',data=>addLine(data.text));
socket.on('error_message',data=>document.getElementById('status').textContent=data.text);
</script></body></html>"""


def valid_room(value):
    return isinstance(value, str) and bool(
        re.fullmatch(r"[A-Za-z0-9_-]{1,32}", value)
    )


@app.get("/")
def index():
    return render_template_string(PAGE)


@socketio.on("join")
def on_join(data):
    if not isinstance(data, dict):
        emit("error_message", {"text": "Invalid join request."})
        return

    name = data.get("name", "Guest")
    room = data.get("room", "general")
    if not isinstance(name, str) or not isinstance(room, str):
        emit("error_message", {"text": "Name and room must be text."})
        return

    name = name.strip()
    room = room.strip()
    if not name or len(name) > 24:
        emit("error_message", {"text": "Names must contain 1–24 characters."})
        return
    if not valid_room(room):
        emit(
            "error_message",
            {"text": "Room names may contain letters, numbers, _ and - only (up to 32 characters)."},
        )
        return

    session["chat_name"] = name
    session["chat_room"] = room
    join_room(room)
    emit("notice", {"text": f"{name} joined #{room}."}, to=room)


@socketio.on("message")
def on_message(data):
    if not isinstance(data, dict):
        emit("error_message", {"text": "Invalid message request."})
        return

    text = data.get("text", "")
    room = session.get("chat_room")
    name = session.get("chat_name", "Guest")
    if not isinstance(text, str):
        emit("error_message", {"text": "Messages must be text."})
        return

    text = text.strip()
    if not text:
        return
    if len(text) > 500:
        emit("error_message", {"text": "Messages must be 500 characters or fewer."})
        return
    if not room:
        emit("error_message", {"text": "Join a room before sending messages."})
        return

    emit("message", {"name": name, "text": text}, to=room)


if __name__ == "__main__":
    socketio.run(
        app,
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
    )

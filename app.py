"""A minimal room-based real-time chat demo."""
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, join_room, emit

app=Flask(__name__)
app.config["SECRET_KEY"]="change-this-development-secret"
socketio=SocketIO(app, cors_allowed_origins=[])

PAGE="""<!doctype html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'><title>Room Chat</title>
<style>body{font:16px system-ui;background:#10121b;color:#eee;max-width:720px;margin:35px auto;padding:0 16px}main{background:#1b2030;padding:24px;border-radius:16px}#messages{height:360px;overflow:auto;background:#101522;padding:14px;border-radius:10px;list-style:none}input{padding:12px;border-radius:8px;border:0}#name,#room{width:28%}#message{width:58%}button{padding:12px;background:#9b8cff;border:0;border-radius:8px}</style></head><body><main><h1>Room Chat</h1>
<p><input id='name' placeholder='Your name' maxlength='24'><input id='room' placeholder='Room' value='general' maxlength='32'><button id='join'>Join</button></p>
<ul id='messages'></ul><form id='form'><input id='message' placeholder='Write a message...' maxlength='500' required><button>Send</button></form><p id='status'>Not connected to a room.</p></main>
<script src='https://cdn.socket.io/4.7.5/socket.io.min.js'></script><script>
const socket=io();let activeRoom='';
const messages=document.getElementById('messages');
document.getElementById('join').onclick=()=>{const name=document.getElementById('name').value.trim();activeRoom=document.getElementById('room').value.trim();if(!name||!activeRoom)return alert('Enter a name and room.');socket.emit('join',{name,room:activeRoom});messages.innerHTML='';document.getElementById('status').textContent='Joined '+activeRoom;};
document.getElementById('form').onsubmit=e=>{e.preventDefault();const input=document.getElementById('message');if(activeRoom&&input.value.trim()){socket.emit('message',{text:input.value.trim()});input.value='';}};
socket.on('message',data=>{const li=document.createElement('li');li.textContent=data.name+': '+data.text;messages.appendChild(li);messages.scrollTop=messages.scrollHeight;});
socket.on('notice',data=>{const li=document.createElement('li');li.textContent=data.text;messages.appendChild(li);});
</script></body></html>"""

@app.get("/")
def index(): return render_template_string(PAGE)

@socketio.on("join")
def on_join(data):
    name=str(data.get("name","Guest")).strip()[:24] or "Guest"
    room=str(data.get("room","general")).strip()[:32] or "general"
    join_room(room)
    emit("notice",{"text":f"{name} joined #{room}."},to=room)

@socketio.on("message")
def on_message(data):
    text=str(data.get("text","")).strip()[:500]
    if not text: return
    # Room is kept in the socket session after joining.
    from flask import session
    # Socket.IO room membership is not directly exposed; require room in payload and validate length.
    room=str(data.get("room","general")).strip()[:32] or "general"
    emit("message",{"name":"Guest","text":text},to=room)

if __name__=="__main__": socketio.run(app,host="127.0.0.1",port=5000,debug=True)

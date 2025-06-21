#!/usr/bin/python
# coding:utf-8

# @FileName:    main.py
# @Time:        2024/1/2 22:27
# @Author:      bubu
# @Project:     douyinLiveWebFetcher

from flask import Flask, render_template
from flask_socketio import SocketIO
from liveMan import DouyinLiveWebFetcher
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 只保留最新100条消息
messages = []
room_info = {
    'title': '未知',
    'viewer_count': '0',
    'status': '未知'
}

def on_new_message(msg):
    global messages
    messages.append(msg)
    messages = messages[-100:]
    socketio.emit('messages', messages)
    # 每次有新消息也推送最新房间信息
    socketio.emit('room_info', room_info)

def on_room_info(info):
    global room_info
    # info 需包含 title, viewer_count, status
    for k in ['title', 'viewer_count', 'status']:
        if k in info:
            room_info[k] = info[k]
    socketio.emit('room_info', room_info)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    live_id = '876118847995'
    room = DouyinLiveWebFetcher(live_id, on_message=on_new_message, on_room_info=on_room_info)
    threading.Thread(target=room.start, daemon=True).start()
    socketio.run(app, debug=True)

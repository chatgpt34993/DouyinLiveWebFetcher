#!/usr/bin/python
# coding:utf-8

# @FileName:    main.py
# @Time:        2024/1/2 22:27
# @Author:      bubu
# @Project:     douyinLiveWebFetcher

from flask import Flask, render_template, send_file, request
from flask_socketio import SocketIO
from liveMan import DouyinLiveWebFetcher
import threading
import time
import pandas as pd
import os

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

rank_list = []
rank_list_update_time = 0
rank_history = []

def on_new_message(msg):
    global messages
    print("on_new_message 被调用", msg)
    messages.append(msg)
    messages = messages[-100:]
    socketio.emit('messages', messages)
    socketio.emit('room_info', room_info)

def on_room_info(info):
    global room_info
    print("on_room_info 被调用", info)
    for k in ['title', 'viewer_count', 'status']:
        if k in info:
            room_info[k] = info[k]
    socketio.emit('room_info', room_info)

def on_rank_list(fans):
    global rank_list, rank_list_update_time, rank_history
    rank_list = fans
    rank_list_update_time = int(time.time())
    if fans:
        for fan in fans:
            fan['update_time'] = rank_list_update_time
        rank_history.extend(fans)
    socketio.emit('rank_list', {'fans': rank_list, 'update_time': rank_list_update_time})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/export_rank_list')
def export_rank_list():
    global rank_list
    if not rank_list:
        return '暂无数据', 404
    # 增加粉丝号（id），格式化update_time
    export_data = []
    for fan in rank_list[:100]:
        fan_copy = fan.copy()
        # 假设fan中有'id'字段，如果没有则补充
        if 'id' not in fan_copy:
            fan_copy['id'] = ''
        # 格式化update_time
        if 'update_time' in fan_copy:
            import datetime
            fan_copy['update_time'] = datetime.datetime.fromtimestamp(fan_copy['update_time']).strftime('%Y-%m-%d %H:%M:%S')
        export_data.append(fan_copy)
    df = pd.DataFrame(export_data)
    # 字段顺序：昵称、粉丝号、头像、更新时间
    columns = ['nick_name', 'id', 'avatar', 'update_time']
    df = df.reindex(columns=columns)
    file_path = 'rank_list_export.xlsx'
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    live_id = '147937241190'
    room = DouyinLiveWebFetcher(live_id, on_message=on_new_message, on_room_info=on_room_info)
    setattr(room, 'on_rank_list', on_rank_list)
    threading.Thread(target=room.start, daemon=True).start()
    socketio.run(app, debug=True)

import sys
sys.path.append("..")  # 让app_test能import到主目录的liveMan.py
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO
import threading
import time
import pandas as pd
import os
import zipfile
from datetime import datetime
from liveMan import DouyinLiveWebFetcher
import webbrowser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

fetcher = None
is_monitoring = False

# 存储最新数据
latest_comments = []
latest_fans = []
room_info = {
    'title': '未知',
    'viewer_count': '0',
    'status': '未知'
}

# 弹幕回调
def on_new_message(msg):
    global latest_comments
    print("on_new_message 被调用", msg)
    latest_comments.append(msg)
    latest_comments = latest_comments[-100:]
    socketio.emit('comments', msg)

# 房间信息回调
def on_room_info(info):
    global room_info
    print("on_room_info 被调用", info)
    print("更新前的room_info:", room_info)
    for k in ['title', 'viewer_count', 'status']:
        if k in info:
            room_info[k] = info[k]
    print("更新后的room_info:", room_info)
    print("发送room_info到前端:", room_info)
    socketio.emit('room_info', room_info)

# 粉丝榜回调
def on_rank_list(fans):
    global latest_fans
    print("on_rank_list 被调用, 粉丝榜数量:", len(fans))
    print("粉丝榜数据详情:", fans)
    latest_fans = fans
    socketio.emit('fans', fans)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_monitor', methods=['POST'])
def start_monitor():
    global fetcher
    live_id = request.form.get('live_id')
    if not live_id:
        return jsonify({'status': 'error', 'message': '请输入直播间ID'})
    if fetcher:
        return jsonify({'status': 'error', 'message': '已有采集任务'})
    
    print(f"开始监控直播间: {live_id}")
    # 启动监控
    fetcher = DouyinLiveWebFetcher(
        live_id=live_id,
        on_message=on_new_message,
        on_room_info=on_room_info
    )
    
    # 设置粉丝榜回调
    fetcher.on_rank_list = on_rank_list
    
    def start_monitoring():
        try:
            # 临时修改generateSignature函数的默认路径
            import sys
            sys.path.append("..")
            from liveMan import generateSignature
            
            # 修改generateSignature函数的默认script_file路径
            import types
            def new_generate_signature(wss, script_file='../sign.js'):
                return generateSignature(wss, script_file)
            
            # 替换liveMan模块中的generateSignature函数
            import liveMan
            liveMan.generateSignature = new_generate_signature
            
            fetcher.start()
        except Exception as e:
            print(f"监控启动失败: {e}")
            socketio.emit('error', {'message': f'监控启动失败: {e}'})
    
    thread = threading.Thread(target=start_monitoring)
    thread.daemon = True
    thread.start()
    return jsonify({'status': 'success', 'message': f'已开始监控直播间 {live_id}'})

@app.route('/stop_monitor', methods=['POST'])
def stop_monitor():
    global fetcher, latest_comments, latest_fans, room_info
    try:
        if fetcher:
            print(f"正在停止监控直播间: {fetcher.live_id}")
            
            # 尝试停止fetcher
            try:
                fetcher.stop()
                print("【√】fetcher.stop() 执行成功")
            except Exception as e:
                print(f"【X】fetcher.stop() 执行失败: {e}")
            
            # 清理fetcher对象
            fetcher = None
            
            # 清理数据
            latest_comments = []
            latest_fans = []
            room_info = {
                'title': '未知',
                'viewer_count': '0',
                'status': '未知'
            }
            
            # 发送停止通知到前端
            socketio.emit('monitor_stopped', {'message': '监控已停止'})
            
            print("【√】监控已完全停止")
            return jsonify({'status': 'success', 'message': '已停止监控'})
        else:
            return jsonify({'status': 'error', 'message': '没有正在运行的采集任务'})
    except Exception as e:
        print(f"停止监控时发生错误: {e}")
        # 即使出错也要清理fetcher
        fetcher = None
        return jsonify({'status': 'error', 'message': f'停止监控时发生错误: {str(e)}'})

@app.route('/get_monitoring_status', methods=['GET'])
def get_monitoring_status():
    return jsonify({
        'monitoring': [fetcher.live_id] if fetcher else [],
        'available_data': [fetcher.live_id] if fetcher else []
    })

@app.route('/export_data', methods=['POST'])
def export_data():
    global latest_comments, latest_fans
    print(f"导出数据 - 弹幕数量: {len(latest_comments)}, 粉丝榜数量: {len(latest_fans)}")
    
    if not latest_comments and not latest_fans:
        print("没有可导出的数据")
        return jsonify({'status': 'error', 'message': '没有可导出的数据'})
    
    try:
        # 创建临时文件夹
        temp_dir = os.path.join(os.getcwd(), 'temp_data')
        os.makedirs(temp_dir, exist_ok=True)
        
        # 处理弹幕数据
        comments_data = []
        for comment in latest_comments:
            if isinstance(comment, dict):
                comments_data.append(comment)
            else:
                comments_data.append({'raw': str(comment)})
        
        # 处理粉丝榜数据
        fans_data = []
        for fan in latest_fans:
            if isinstance(fan, dict):
                fans_data.append(fan)
            else:
                fans_data.append({'raw': str(fan)})
        
        print(f"处理后的数据 - 弹幕: {len(comments_data)}条, 粉丝榜: {len(fans_data)}条")
        
        # 创建弹幕数据文件
        comments_file = os.path.join(temp_dir, 'comments.csv')
        if comments_data:
            pd.DataFrame(comments_data).to_csv(comments_file, index=False, encoding='utf-8-sig')
            print(f"弹幕数据已保存到: {comments_file}")
        
        # 创建粉丝榜数据文件
        fans_file = os.path.join(temp_dir, 'fans.csv')
        if fans_data:
            pd.DataFrame(fans_data).to_csv(fans_file, index=False, encoding='utf-8-sig')
            print(f"粉丝榜数据已保存到: {fans_file}")
        
        # 创建压缩包
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_file = os.path.join(temp_dir, f'douyin_data_{timestamp}.zip')
        
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if comments_data:
                zipf.write(comments_file, 'comments.csv')
                print("comments.csv 已添加到压缩包")
            if fans_data:
                zipf.write(fans_file, 'fans.csv')
                print("fans.csv 已添加到压缩包")
        
        print(f"压缩包已创建: {zip_file}")
        
        # 清理临时CSV文件
        if os.path.exists(comments_file):
            os.remove(comments_file)
        if os.path.exists(fans_file):
            os.remove(fans_file)
        
        return send_file(
            zip_file, 
            as_attachment=True,
            download_name=f'douyin_data_{timestamp}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        print(f"导出数据失败: {e}")
        return jsonify({'status': 'error', 'message': f'导出失败: {str(e)}'})

@app.route('/check_data', methods=['GET'])
def check_data():
    """检查当前数据状态"""
    global latest_comments, latest_fans
    return jsonify({
        'comments_count': len(latest_comments),
        'fans_count': len(latest_fans),
        'comments_sample': latest_comments[:3] if latest_comments else [],
        'fans_sample': latest_fans[:3] if latest_fans else []
    })

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)  # 等待服务器启动
    try:
        webbrowser.open('http://localhost:5001')
        print("浏览器已自动打开")
    except Exception as e:
        print(f"无法自动打开浏览器: {e}")
        print("请手动访问: http://localhost:5001")

if __name__ == '__main__':
    print("=== 抖音直播监控程序 ===")
    print("正在启动服务器...")
    print("服务器启动后会自动打开浏览器")
    print("如果没有自动打开，请手动访问: http://localhost:5001")
    print()
    
    # 启动自动打开浏览器的线程
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动Flask服务器
    socketio.run(app, debug=False, port=5001, host='127.0.0.1')

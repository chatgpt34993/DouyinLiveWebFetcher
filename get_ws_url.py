import requests
import re
import random
import string
import urllib.parse
import hashlib
import subprocess
import os

def generate_ms_token(length=107):
    base_str = string.ascii_letters + string.digits + '=_'
    return ''.join(random.choice(base_str) for _ in range(length))

def get_ttwid_and_roomid(live_url):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    # 1. 直接从URL提取room_id
    match = re.search(r'live.douyin.com/(\d+)', live_url)
    room_id = match.group(1) if match else ''
    # 2. 访问主页获取ttwid
    resp = session.get(live_url, headers=headers, allow_redirects=True)
    ttwid = resp.cookies.get('ttwid', '')
    # 有时需要多访问一次
    if not ttwid:
        resp = session.get(live_url, headers=headers, allow_redirects=True)
        ttwid = resp.cookies.get('ttwid', '')
    return ttwid, room_id

def build_md5_param(wss_url):
    params = ("live_id,aid,version_code,webcast_sdk_version,"
              "room_id,sub_room_id,sub_channel_id,did_rule,"
              "user_unique_id,device_platform,device_type,ac,"
              "identity").split(',')
    wss_params = urllib.parse.urlparse(wss_url).query.split('&')
    wss_maps = {i.split('=')[0]: i.split('=')[-1] for i in wss_params}
    tpl_params = [f"{i}={wss_maps.get(i, '')}" for i in params]
    param = ','.join(tpl_params)
    md5 = hashlib.md5()
    md5.update(param.encode())
    return md5.hexdigest()

def get_signature(md5_param):
    # 切换到node_sign目录调用gen_signature.js
    node_dir = os.path.join(os.path.dirname(__file__), 'node_sign')
    result = subprocess.run(['node', 'gen_signature.js', md5_param], cwd=node_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print("Node.js 生成 signature 失败:", result.stderr)
        return ''
    return result.stdout.strip()

def build_ws_url(live_url):
    ttwid, room_id = get_ttwid_and_roomid(live_url)
    ms_token = generate_ms_token()
    params = {
        "app_name": "douyin_web",
        "version_code": "180800",
        "webcast_sdk_version": "1.0.14-beta.0",
        "update_version_code": "1.0.14-beta.0",
        "compress": "gzip",
        "device_platform": "web",
        "cookie_enabled": "true",
        "screen_width": "1536",
        "screen_height": "864",
        "browser_language": "zh-CN",
        "browser_platform": "Win32",
        "browser_name": "Mozilla",
        "browser_version": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "browser_online": "true",
        "tz_name": "Asia/Shanghai",
        "host": "https://live.douyin.com",
        "aid": "6383",
        "live_id": "1",
        "did_rule": "3",
        "endpoint": "live_pc",
        "support_wrds": "1",
        "user_unique_id": "7319483754668557238",  # 可自定义
        "im_path": "/webcast/im/fetch/",
        "identity": "audience",
        "need_persist_msg_count": "15",
        "room_id": room_id,
        "msToken": ms_token,
        "ttwid": ttwid,
    }
    base_ws = "wss://webcast5-ws-web-hl.douyin.com/webcast/im/push/v2/"
    ws_url = base_ws + "?" + urllib.parse.urlencode(params)
    md5_param = build_md5_param(ws_url)
    signature = get_signature(md5_param)
    ws_url += f"&signature={signature}"
    print("完整WebSocket地址：")
    print(ws_url)
    print("\nttwid:", ttwid)
    print("msToken:", ms_token)
    print("room_id:", room_id)
    print("signature:", signature)

if __name__ == '__main__':
    live_url = input("请输入抖音直播间URL（如 https://live.douyin.com/xxxxxxx ）: ").strip()
    build_ws_url(live_url) 
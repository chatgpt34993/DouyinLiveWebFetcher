#!/usr/bin/python
# coding:utf-8

# @FileName:    liveMan.py
# @Time:        2024/1/2 21:51
# @Author:      bubu
# @Project:     douyinLiveWebFetcher

import codecs
import gzip
import hashlib
import random
import re
import string
import subprocess
import threading
import time
import urllib.parse
from contextlib import contextmanager
from unittest.mock import patch

import requests
import websocket
from py_mini_racer import MiniRacer

from protobuf.douyin import *


@contextmanager
def patched_popen_encoding(encoding='utf-8'):
    original_popen_init = subprocess.Popen.__init__
    
    def new_popen_init(self, *args, **kwargs):
        kwargs['encoding'] = encoding
        original_popen_init(self, *args, **kwargs)
    
    with patch.object(subprocess.Popen, '__init__', new_popen_init):
        yield


def generateSignature(wss, script_file='../sign.js'):
    """
    出现gbk编码问题则修改 python模块subprocess.py的源码中Popen类的__init__函数参数encoding值为 "utf-8"
    """
    params = ("live_id,aid,version_code,webcast_sdk_version,"
              "room_id,sub_room_id,sub_channel_id,did_rule,"
              "user_unique_id,device_platform,device_type,ac,"
              "identity").split(',')
    wss_params = urllib.parse.urlparse(wss).query.split('&')
    wss_maps = {i.split('=')[0]: i.split("=")[-1] for i in wss_params}
    tpl_params = [f"{i}={wss_maps.get(i, '')}" for i in params]
    param = ','.join(tpl_params)
    md5 = hashlib.md5()
    md5.update(param.encode())
    md5_param = md5.hexdigest()
    
    with codecs.open(script_file, 'r', encoding='utf8') as f:
        script = f.read()
    
    ctx = MiniRacer()
    ctx.eval(script)
    
    try:
        signature = ctx.call("get_sign", md5_param)
        return signature
    except Exception as e:
        print(e)
    
    # 以下代码对应js脚本为sign_v0.js
    # context = execjs.compile(script)
    # with patched_popen_encoding(encoding='utf-8'):
    #     ret = context.call('getSign', {'X-MS-STUB': md5_param})
    # return ret.get('X-Bogus')


def generateMsToken(length=107):
    """
    产生请求头部cookie中的msToken字段，其实为随机的107位字符
    :param length:字符位数
    :return:msToken
    """
    random_str = ''
    base_str = string.ascii_letters + string.digits + '=_'
    _len = len(base_str) - 1
    for _ in range(length):
        random_str += base_str[random.randint(0, _len)]
    return random_str


class DouyinLiveWebFetcher:
    
    def __init__(self, live_id, on_message=None, on_room_info=None):
        """
        直播间弹幕抓取对象
        :param live_id: 直播间的直播id，打开直播间web首页的链接如：https://live.douyin.com/261378947940，
                        其中的261378947940即是live_id
        """
        self.live_id = live_id
        self.on_message = on_message
        self.on_room_info = on_room_info
        self.on_rank_list = None  # 新增，推送粉丝榜
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        self.live_url = "https://live.douyin.com/"
        self.__ttwid = None
        self.__room_id = None
        self.room_title = "直播间"
        self.room_status = None
        self.viewer_count = "0"
        self.ws = None
        self._running = True  # 添加运行状态标志
    
    def start(self):
        # 启动时主动获取一次房间状态
        self.get_room_status()
        self._connectWebSocket()
    
    def stop(self):
        """停止监控，关闭WebSocket连接和清理资源"""
        try:
            # 设置停止标志
            self._running = False
            
            # 关闭WebSocket连接
            if hasattr(self, 'ws') and self.ws:
                self.ws.close()
                print("【√】WebSocket连接已关闭")
            
            # 清理资源
            self.__ttwid = None
            self.__room_id = None
            self.room_status = None
            
            print("【√】监控已停止")
        except Exception as e:
            print(f"【X】停止监控时出错: {e}")
    
    @property
    def ttwid(self):
        """
        产生请求头部cookie中的ttwid字段，访问抖音网页版直播间首页可以获取到响应cookie中的ttwid
        :return: ttwid
        """
        if self.__ttwid:
            return self.__ttwid
        headers = {
            "User-Agent": self.user_agent,
        }
        try:
            response = requests.get(self.live_url, headers=headers)
            response.raise_for_status()
        except Exception as err:
            print("【X】Request the live url error: ", err)
        else:
            self.__ttwid = response.cookies.get('ttwid')
            return self.__ttwid
    
    @property
    def room_id(self):
        """
        根据直播间的地址获取到真正的直播间roomId，有时会有错误，可以重试请求解决
        :return:room_id
        """
        if self.__room_id:
            return self.__room_id
        url = self.live_url + self.live_id
        headers = {
            "User-Agent": self.user_agent,
            "cookie": f"ttwid={self.ttwid}&msToken={generateMsToken()}; __ac_nonce=0123407cc00a9e438deb4",
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except Exception as err:
            print("【X】Request the live room url error: ", err)
            return None
        else:
            match = re.search(r'roomId\\":\\"(\d+)\\"', response.text)
            if match is None or len(match.groups()) < 1:
                print("【X】No match found for roomId")
                return None
            self.__room_id = match.group(1)
            return self.__room_id
    
    def get_room_status(self):
        """
        获取直播间开播状态:
        room_status: 2 直播已结束
        room_status: 0 直播进行中
        """
        url = ('https://live.douyin.com/webcast/room/web/enter/?aid=6383'
               '&app_name=douyin_web&live_id=1&device_platform=web&language=zh-CN&enter_from=web_live'
               '&cookie_enabled=true&screen_width=1536&screen_height=864&browser_language=zh-CN&browser_platform=Win32'
               '&browser_name=Edge&browser_version=133.0.0.0'
               f'&web_rid={self.live_id}'
               f'&room_id_str={self.room_id}'
               '&enter_source=&is_need_double_stream=false&insert_task_id=&live_reason='
               '&msToken=&a_bogus=')
        resp = requests.get(url, headers={
            'User-Agent': self.user_agent,
            'Cookie': f'ttwid={self.ttwid};'
        })
        data = resp.json().get('data')
        if data:
            room_status = data.get('room_status')
            # 0=直播中, 2=已结束, 1=准备中
            if room_status == 0:
                self.room_status = "直播中"
            elif room_status == 2:
                self.room_status = "已结束"
            elif room_status == 1:
                self.room_status = "准备中"
            else:
                self.room_status = str(room_status)
            user = data.get('user')
            user_id = user.get('id_str') if user else ''
            nickname = user.get('nickname') if user else ''
            print(f"【{nickname}】[{user_id}]直播间：{self.room_status}.")
        else:
            self.room_status = "未知"
    
    def _connectWebSocket(self):
        """
        连接抖音直播间websocket服务器，请求直播间数据
        """
        wss = ("wss://webcast5-ws-web-hl.douyin.com/webcast/im/push/v2/?app_name=douyin_web"
               "&version_code=180800&webcast_sdk_version=1.0.14-beta.0"
               "&update_version_code=1.0.14-beta.0&compress=gzip&device_platform=web&cookie_enabled=true"
               "&screen_width=1536&screen_height=864&browser_language=zh-CN&browser_platform=Win32"
               "&browser_name=Mozilla"
               "&browser_version=5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,"
               "%20like%20Gecko)%20Chrome/126.0.0.0%20Safari/537.36"
               "&browser_online=true&tz_name=Asia/Shanghai"
               "&cursor=d-1_u-1_fh-7392091211001140287_t-1721106114633_r-1"
               f"&internal_ext=internal_src:dim|wss_push_room_id:{self.room_id}|wss_push_did:7319483754668557238"
               f"|first_req_ms:1721106114541|fetch_time:1721106114633|seq:1|wss_info:0-1721106114633-0-0|"
               f"wrds_v:7392094459690748497"
               f"&host=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&endpoint=live_pc&support_wrds=1"
               f"&user_unique_id=7319483754668557238&im_path=/webcast/im/fetch/&identity=audience"
               f"&need_persist_msg_count=15&insert_task_id=&live_reason=&room_id={self.room_id}&heartbeatDuration=0")
        
        signature = generateSignature(wss)
        wss += f"&signature={signature}"
        
        headers = {
            "cookie": f"ttwid={self.ttwid}",
            'user-agent': self.user_agent,
        }
        self.ws = websocket.WebSocketApp(wss,
                                         header=headers,
                                         on_open=self._wsOnOpen,
                                         on_message=self._wsOnMessage,
                                         on_error=self._wsOnError,
                                         on_close=self._wsOnClose)
        try:
            self.ws.run_forever()
        except Exception:
            self.stop()
            raise
    
    def _sendHeartbeat(self):
        """
        发送心跳包
        """
        while self._running:
            try:
                if not self._running:
                    break
                heartbeat = PushFrame(payload_type='hb').SerializeToString()
                self.ws.send(heartbeat, websocket.ABNF.OPCODE_PING)
                print("【√】发送心跳包")
            except Exception as e:
                print("【X】心跳包检测错误: ", e)
                break
            else:
                # 使用更短的睡眠时间，以便更快响应停止信号
                for _ in range(50):  # 5秒分成50次，每次0.1秒
                    if not self._running:
                        break
                    time.sleep(0.1)
    
    def _wsOnOpen(self, ws):
        """
        连接建立成功
        """
        print("【√】WebSocket连接成功.")
        threading.Thread(target=self._sendHeartbeat).start()
    
    def _wsOnMessage(self, ws, message):
        """
        接收到数据
        :param ws: websocket实例
        :param message: 数据
        """
        
        # 根据proto结构体解析对象
        package = PushFrame().parse(message)
        response = Response().parse(gzip.decompress(package.payload))
        
        # 返回直播间服务器链接存活确认消息，便于持续获取数据
        if response.need_ack:
            ack = PushFrame(log_id=package.log_id,
                            payload_type='ack',
                            payload=response.internal_ext.encode('utf-8')
                            ).SerializeToString()
            ws.send(ack, websocket.ABNF.OPCODE_BINARY)
        
        # 根据消息类别解析消息体
        for msg in response.messages_list:
            method = msg.method
            handler = {
                'WebcastChatMessage': self._parseChatMsg,  # 聊天消息
                'WebcastGiftMessage': self._parseGiftMsg,  # 礼物消息
                'WebcastLikeMessage': self._parseLikeMsg,  # 点赞消息
                'WebcastMemberMessage': self._parseMemberMsg,  # 进入直播间消息
                'WebcastSocialMessage': self._parseSocialMsg,  # 关注消息
                'WebcastRoomUserSeqMessage': self._parseRoomUserSeqMsg,  # 直播间统计
                'WebcastFansclubMessage': self._parseFansclubMsg,  # 粉丝团消息
                'WebcastControlMessage': self._parseControlMsg,  # 直播间状态消息
                'WebcastEmojiChatMessage': self._parseEmojiChatMsg,  # 聊天表情包消息
                'WebcastRoomStatsMessage': self._parseRoomStatsMsg,  # 直播间统计信息
                'WebcastRoomMessage': self._parseRoomMsg,  # 直播间信息
                'WebcastRoomRankMessage': self._parseRankMsg,  # 直播间排行榜信息
                'WebcastRoomStreamAdaptationMessage': self._parseRoomStreamAdaptationMsg,  # 直播间流配置
            }.get(method)
            if handler:
                try:
                    handler(msg.payload)
                except Exception:
                    pass
    
    def _wsOnError(self, ws, error):
        print("WebSocket error: ", error)
    
    def _wsOnClose(self, ws, *args):
        self.get_room_status()
        print("WebSocket connection closed.")
    
    def _parseChatMsg(self, payload):
        """聊天消息"""
        message = ChatMessage().parse(payload)
        user_name = message.user.nick_name
        user_id = message.user.id
        content = message.content
        msg = f"【聊天msg】[{user_id}]{user_name}: {content}"
        print(msg)
        if self.on_message:
            self.on_message({"raw": msg})
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })
    
    def _parseGiftMsg(self, payload):
        """礼物消息"""
        message = GiftMessage().parse(payload)
        user_name = message.user.nick_name
        gift_name = message.gift.name
        gift_cnt = message.combo_count
        msg = f"【礼物msg】{user_name} 送出了 {gift_name}x{gift_cnt}"
        print(msg)
        if self.on_message:
            self.on_message({"raw": msg})
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })
    
    def _parseLikeMsg(self, payload):
        '''点赞消息'''
        message = LikeMessage().parse(payload)
        user_name = message.user.nick_name
        count = message.count
        msg = f"【点赞msg】{user_name} 点了{count}个赞"
        print(msg)
        if self.on_message:
            self.on_message({"raw": msg})
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })
    
    def _parseMemberMsg(self, payload):
        '''进入直播间消息'''
        message = MemberMessage().parse(payload)
        user_name = message.user.nick_name
        user_id = message.user.id
        gender = ["女", "男"][message.user.gender]
        msg = f"【进场msg】[{user_id}][{gender}]{user_name} 进入了直播间"
        print(msg)
        if self.on_message:
            self.on_message({"raw": msg})
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })
    
    def _parseSocialMsg(self, payload):
        '''关注消息'''
        message = SocialMessage().parse(payload)
        user_name = message.user.nick_name
        user_id = message.user.id
        msg = f"【关注msg】[{user_id}]{user_name} 关注了主播"
        print(msg)
        if self.on_message:
            self.on_message({"raw": msg})
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })
    
    def _parseRoomUserSeqMsg(self, payload):
        '''直播间统计'''
        message = RoomUserSeqMessage().parse(payload)
        current = message.total
        total = message.total_pv_for_anchor
        msg = f"【统计msg】当前观看人数: {current}, 累计观看人数: {total}"
        print(msg)
        if self.on_message:
            self.on_message({"raw": msg})
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })
    
    def _parseFansclubMsg(self, payload):
        '''粉丝团消息'''
        message = FansclubMessage().parse(payload)
        content = message.content
        msg = f"【粉丝团msg】 {content}"
        print(msg)
        if self.on_message:
            self.on_message({"raw": msg})
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })
    
    def _parseEmojiChatMsg(self, payload):
        '''聊天表情包消息'''
        message = EmojiChatMessage().parse(payload)
        emoji_id = message.emoji_id
        user = message.user
        common = message.common
        default_content = message.default_content
        msg = f"【聊天表情包id】 {emoji_id},user：{user},common:{common},default_content:{default_content}"
        print(msg)
        if self.on_message:
            self.on_message({"raw": msg})
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })
    
    def _parseRoomMsg(self, payload):
        message = RoomMessage().parse(payload)
        print("RoomMessage内容：", message)
        print("RoomMessage属性：", dir(message))
        for attr in dir(message):
            if not attr.startswith('_'):
                print(f"{attr}: {getattr(message, attr, None)}")
        # 优先用 owner.nick_name 作为标题
        title = None
        owner = getattr(message, 'owner', None)
        if owner:
            nick_name = getattr(owner, 'nick_name', None)
            if nick_name:
                title = nick_name
        # 其次尝试 common.title
        if not title:
            common = getattr(message, 'common', None)
            if common:
                common_title = getattr(common, 'title', None)
                if common_title:
                    title = common_title
        if title:
            self.room_title = title
        # 也可打印 self.room_title 便于调试
        print("当前room_title:", self.room_title)
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })
    
    def _parseRoomStatsMsg(self, payload):
        message = RoomStatsMessage().parse(payload)
        display_long = getattr(message, 'display_long', None)
        if display_long:
            # 尝试从 display_long 提取在线人数
            import re
            m = re.search(r'(\d+[\u4e00-\u9fa5]*)在线观众', display_long)
            if m:
                self.viewer_count = m.group(1)
        msg = f"【直播间统计msg】{display_long}"
        print(msg)
        if self.on_message:
            self.on_message({"raw": msg})
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })
    
    def _parseRankMsg(self, payload):
        message = RoomRankMessage().parse(payload)
        ranks_list = message.ranks_list
        print("收到排行榜 ranks_list:", ranks_list)
        print("ranks_list长度:", len(ranks_list) if ranks_list else 0)
        msg = f"【直播间排行榜msg】{ranks_list}"
        print(msg)
        if self.on_message:
            self.on_message({"raw": msg})
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })
        
        # 新增：推送粉丝榜到前端（先用WebSocket榜单）
        fans = []
        for rank in ranks_list:
            user = getattr(rank, 'user', None)
            print("rank user:", user)  # 增加日志
            if user:
                avatar = ""
                avatar_thumb = getattr(user, "avatar_thumb", None)
                if avatar_thumb:
                    url_list = getattr(avatar_thumb, "url_list_list", [])
                    if url_list:
                        avatar = url_list[0]
                fans.append({
                    "nick_name": getattr(user, "nick_name", ""),
                    "avatar": avatar,
                    "id": getattr(user, "id", ""),         # 数字ID
                    "idStr": getattr(user, "id_str", "")   # 字符串ID
                })
        print("推送到前端的fans(WebSocket):", fans)  # 增加日志

        # 新增：补全HTTP粉丝榜
        try:
            print(f"尝试获取HTTP粉丝榜，room_id: {self.room_id}")
            http_fans = self.get_full_fans_rank(self.room_id)
            if http_fans and len(http_fans) > len(fans):
                print(f"HTTP粉丝榜获取成功，共{len(http_fans)}条，替换WebSocket榜单")
                fans = http_fans
            else:
                print(f"HTTP粉丝榜获取失败或数据不足，保留WebSocket榜单({len(fans)}条)")
        except Exception as e:
            print(f"HTTP粉丝榜采集异常: {e}")
        
        print("最终推送到前端的fans:", fans)
        print("fans长度:", len(fans))
        
        if hasattr(self, 'on_rank_list') and callable(self.on_rank_list):
            print("调用on_rank_list回调函数")
            self.on_rank_list(fans)
        else:
            print("on_rank_list回调函数不存在或不可调用")
    
    def _parseControlMsg(self, payload):
        message = ControlMessage().parse(payload)
        print("ControlMessage内容：", message)
        print("ControlMessage属性：", dir(message))
        for attr in dir(message):
            if not attr.startswith('_'):
                print(f"{attr}: {getattr(message, attr, None)}")
        status_found = False
        if hasattr(message, 'status'):
            status_found = True
            if message.status == 3:
                self.room_status = "已结束"
            elif message.status == 2:
                self.room_status = "准备中"
            elif message.status == 1:
                self.room_status = "直播中"
            else:
                self.room_status = str(message.status)
        # 如果没有推送 status，主动查一次
        if not status_found or self.room_status == "未知":
            self.get_room_status()
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })
    
    def _parseRoomStreamAdaptationMsg(self, payload):
        message = RoomStreamAdaptationMessage().parse(payload)
        adaptationType = message.adaptation_type
        msg = f'直播间adaptation: {adaptationType}'
        print(msg)
        if self.on_message:
            self.on_message({"raw": msg})
        if self.on_room_info:
            self.on_room_info({
                "title": self.room_title,
                "viewer_count": self.viewer_count,
                "status": self.room_status
            })

    def get_full_fans_rank(self, room_id):
        url = f"https://webcast.amemv.com/webcast/ranklist/fans/?room_id={room_id}&type=1&count=100"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Referer": f"https://live.douyin.com/{room_id}",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            print("HTTP粉丝榜原始返回：", resp.text[:500])  # 只打印前500字符
            if resp.status_code != 200:
                print(f"HTTP粉丝榜请求失败，状态码: {resp.status_code}")
                return []
            
            data = resp.json()
            fans = []
            for item in data.get("data", {}).get("ranks", []):
                user = item.get("user", {})
                fans.append({
                    "user_id": user.get("id_str"),
                    "nickname": user.get("nickname"),
                    "score": item.get("score"),
                    "avatar": user.get("avatar_thumb", {}).get("url_list", [""])[0] if user.get("avatar_thumb") else "",
                    "rank": item.get("rank"),
                })
            print(f"HTTP粉丝榜获取成功，共{len(fans)}条")
            return fans
        except Exception as e:
            print("HTTP粉丝榜获取失败：", e)
            return []

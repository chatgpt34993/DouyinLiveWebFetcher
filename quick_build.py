#!/usr/bin/env python3
"""
快速打包脚本 - 抖音直播监控程序
"""

import os
import sys
import subprocess

def main():
    print("=== 抖音直播监控程序快速打包 ===")
    print()
    
    # 检查是否在正确的目录
    if not os.path.exists('app_test/app.py'):
        print("错误：请在项目根目录运行此脚本")
        return
    
    try:
        # 安装 PyInstaller
        print("正在安装 PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("PyInstaller 安装完成")
        
        # 直接使用 PyInstaller 命令打包
        print("开始打包...")
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",  # 打包成单个文件
            "--add-data", "app_test/templates:templates",  # 添加模板文件
            "--add-data", "sign.js:.",
            "--add-data", "liveMan.py:.",
            "--add-data", "protobuf:protobuf",
            "--add-data", "node_sign:node_sign",
            "--hidden-import", "flask",
            "--hidden-import", "flask_socketio",
            "--hidden-import", "engineio",
            "--hidden-import", "socketio",
            "--hidden-import", "requests",
            "--hidden-import", "betterproto",
            "--hidden-import", "websocket",
            "--hidden-import", "websocket_client",
            "--hidden-import", "PyExecJS",
            "--hidden-import", "mini_racer",
            "--hidden-import", "pandas",
            "--hidden-import", "openpyxl",
            "--hidden-import", "webbrowser",
            "--name", "DouyinLiveMonitor",
            "app_test/app.py"
        ]
        
        subprocess.run(cmd, check=True)
        
        print()
        print("=== 打包完成！ ===")
        print("可执行文件位置：dist/DouyinLiveMonitor")
        print()
        print("使用方法：")
        print("1. 将 dist/DouyinLiveMonitor 文件复制给其他用户")
        print("2. 其他用户双击运行即可（无需安装Python）")
        print("3. 程序会自动打开浏览器显示监控界面")
        
    except Exception as e:
        print(f"打包失败：{e}")
        return

if __name__ == "__main__":
    main() 
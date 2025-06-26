#!/usr/bin/env python3
"""
使用Docker进行Windows交叉编译的脚本
注意：需要安装Docker
"""

import os
import sys
import subprocess

def check_docker():
    """检查Docker是否安装"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def build_windows_with_docker():
    """使用Docker构建Windows版本"""
    print("=== 使用Docker构建Windows版本 ===")
    print()
    
    # 检查Docker
    if not check_docker():
        print("错误：Docker未安装或未运行")
        print("请先安装Docker Desktop")
        return False
    
    # 检查是否在正确的目录
    if not os.path.exists('app_test/app_windows.py'):
        print("错误：请在项目根目录运行此脚本")
        print("确保app_test/app_windows.py文件存在")
        return False
    
    try:
        print("正在使用Docker构建Windows版本...")
        
        # 使用PyInstaller Windows Docker镜像
        cmd = [
            "docker", "run", "--rm", "-v", f"{os.getcwd()}:/src", "-w", "/src",
            "cdrx/pyinstaller-windows:python3",
            "pyinstaller",
            "--onefile",
            "--windowed",  # 添加窗口模式，避免控制台窗口
            "--add-data", "app_test/templates;templates",
            "--add-data", "sign.js;.",
            "--add-data", "liveMan.py;.",
            "--add-data", "protobuf;protobuf",
            "--add-data", "node_sign;node_sign",
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
            "--hidden-import", "threading",
            "--hidden-import", "time",
            "--hidden-import", "os",
            "--hidden-import", "sys",
            "--hidden-import", "zipfile",
            "--hidden-import", "datetime",
            "--hidden-import", "json",
            "--hidden-import", "jinja2",
            "--hidden-import", "werkzeug",
            "--hidden-import", "eventlet",
            "--hidden-import", "dns",
            "--hidden-import", "dns.resolver",
            "--hidden-import", "dns.exception",
            "--collect-all", "flask",
            "--collect-all", "flask_socketio",
            "--collect-all", "engineio",
            "--collect-all", "socketio",
            "--name", "DouyinLiveMonitor",
            "app_test/app_windows.py"
        ]
        
        subprocess.run(cmd, check=True)
        
        print()
        print("=== Docker构建完成！ ===")
        print("Windows版本位置：dist/DouyinLiveMonitor.exe")
        print()
        print("注意：")
        print("1. 如果构建失败，可能需要先拉取Docker镜像")
        print("2. 运行：docker pull cdrx/pyinstaller-windows:python3")
        print("3. 生成的exe文件双击后会自动打开浏览器")
        
        return True
        
    except Exception as e:
        print(f"Docker构建失败：{e}")
        return False

def main():
    """主函数"""
    print("=== Windows版本Docker交叉编译 ===")
    print()
    print("此脚本将使用Docker在macOS上构建Windows版本")
    print("需要安装Docker Desktop")
    print()
    
    success = build_windows_with_docker()
    
    if success:
        print()
        print("✅ 构建成功！")
        print("现在可以将 dist/DouyinLiveMonitor.exe 分发给Windows用户")
        print("双击exe文件会自动启动服务器并打开浏览器")
    else:
        print()
        print("❌ 构建失败！")
        print("请检查Docker是否正确安装和运行")

if __name__ == "__main__":
    main() 
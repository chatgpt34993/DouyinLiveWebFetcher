#!/usr/bin/env python3
"""
Windows版本打包脚本 - 抖音直播监控程序
注意：此脚本需要在Windows系统上运行，或者使用交叉编译
"""

import os
import sys
import subprocess

def main():
    print("=== Windows版本抖音直播监控程序打包 ===")
    print()
    print("注意：此脚本需要在Windows系统上运行")
    print("如果在macOS/Linux上运行，将生成macOS/Linux版本")
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
        
        # 检测操作系统
        import platform
        system = platform.system()
        print(f"当前操作系统: {system}")
        
        # 根据操作系统调整打包参数
        if system == "Windows":
            exe_name = "DouyinLiveMonitor.exe"
            print("检测到Windows系统，将生成.exe文件")
        else:
            exe_name = "DouyinLiveMonitor"
            print("检测到非Windows系统，将生成可执行文件")
        
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
            "--name", exe_name,
            "app_test/app.py"
        ]
        
        subprocess.run(cmd, check=True)
        
        print()
        print("=== 打包完成！ ===")
        print(f"可执行文件位置：dist/{exe_name}")
        print()
        
        if system == "Windows":
            print("Windows版本使用方法：")
            print("1. 将 dist/DouyinLiveMonitor.exe 文件复制给其他Windows用户")
            print("2. 其他用户双击 DouyinLiveMonitor.exe 即可运行")
            print("3. 程序会自动打开浏览器显示监控界面")
            print("4. 如果杀毒软件报警，请添加信任")
        else:
            print("当前系统版本使用方法：")
            print("1. 将 dist/DouyinLiveMonitor 文件复制给其他用户")
            print("2. 其他用户运行 ./DouyinLiveMonitor 即可")
            print("3. 程序会自动打开浏览器显示监控界面")
        
        print()
        print("注意事项：")
        print("- 首次运行可能需要等待几秒钟启动")
        print("- 确保网络连接正常")
        print("- 如果端口5001被占用，请关闭其他程序")
        
    except Exception as e:
        print(f"打包失败：{e}")
        return

if __name__ == "__main__":
    main() 
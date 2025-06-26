#!/usr/bin/env python3
"""
Windows版本打包脚本 - 抖音直播监控程序
支持多种打包方式：
1. 在Windows系统上直接打包
2. 使用Docker交叉编译（推荐）
3. 在macOS/Linux上打包当前平台版本
"""

import os
import sys
import subprocess
import platform

def check_docker():
    """检查Docker是否安装"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    try:
        print("正在安装 PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("PyInstaller 安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller 安装失败: {e}")
        return False

def build_current_platform():
    """构建当前平台版本"""
    print("=== 构建当前平台版本 ===")
    
    if not install_pyinstaller():
        return False
    
    # 检测操作系统
    system = platform.system()
    if system == "Windows":
        exe_name = "DouyinLiveMonitor.exe"
        print("检测到Windows系统，将生成.exe文件")
        script_file = "app_test/app_windows.py"
    else:
        exe_name = "DouyinLiveMonitor"
        print(f"检测到{system}系统，将生成可执行文件")
        script_file = "app_test/app_windows.py"
    
    try:
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
            script_file
        ]
        
        subprocess.run(cmd, check=True)
        
        print()
        print("=== 打包完成！ ===")
        print(f"可执行文件位置：dist/{exe_name}")
        
        if system == "Windows":
            print("\nWindows版本使用方法：")
            print("1. 将 dist/DouyinLiveMonitor.exe 文件复制给其他Windows用户")
            print("2. 其他用户双击 DouyinLiveMonitor.exe 即可运行")
            print("3. 程序会自动打开浏览器显示监控界面")
            print("4. 如果杀毒软件报警，请添加信任")
        else:
            print(f"\n{system}版本使用方法：")
            print("1. 将 dist/DouyinLiveMonitor 文件复制给其他用户")
            print("2. 其他用户运行 ./DouyinLiveMonitor 即可")
            print("3. 程序会自动打开浏览器显示监控界面")
        
        return True
        
    except Exception as e:
        print(f"打包失败：{e}")
        return False

def build_windows_with_docker():
    """使用Docker构建Windows版本"""
    print("=== 使用Docker构建Windows版本 ===")
    
    if not check_docker():
        print("错误：Docker未安装或未运行")
        print("请先安装Docker Desktop")
        return False
    
    # 检查Windows专用文件
    if not os.path.exists('app_test/app_windows.py'):
        print("错误：app_test/app_windows.py文件不存在")
        print("请确保Windows专用文件已创建")
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
            "-n", "DouyinLiveMonitor",
            "app_test/app_windows.py"
        ]
        
        subprocess.run(cmd, check=True)
        
        print()
        print("=== Docker构建完成！ ===")
        print("Windows版本位置：dist/DouyinLiveMonitor.exe")
        print("\n使用方法：")
        print("1. 将 dist/DouyinLiveMonitor.exe 分发给Windows用户")
        print("2. 双击exe文件会自动启动服务器并打开浏览器")
        print("3. 如果杀毒软件报警，请添加信任")
        
        return True
        
    except Exception as e:
        print(f"Docker构建失败：{e}")
        print("\n可能的解决方案：")
        print("1. 确保Docker Desktop正在运行")
        print("2. 运行：docker pull cdrx/pyinstaller-windows:python3")
        print("3. 检查网络连接")
        return False

def main():
    print("=== Windows版本抖音直播监控程序打包 ===")
    print()
    
    # 检查是否在正确的目录
    if not os.path.exists('app_test/app.py'):
        print("错误：请在项目根目录运行此脚本")
        return
    
    # 检测操作系统
    system = platform.system()
    print(f"当前操作系统: {system}")
    print()
    
    if system == "Windows":
        print("检测到Windows系统，将直接构建Windows版本...")
        success = build_current_platform()
    else:
        print("检测到非Windows系统，请选择打包方式：")
        print("1. 构建当前平台版本（macOS/Linux）")
        print("2. 使用Docker构建Windows版本（推荐）")
        print("3. 退出")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            success = build_current_platform()
        elif choice == "2":
            success = build_windows_with_docker()
        elif choice == "3":
            print("退出打包")
            return
        else:
            print("无效选择，退出")
            return
    
    if success:
        print("\n✅ 打包成功！")
        print("\n注意事项：")
        print("- 首次运行可能需要等待几秒钟启动")
        print("- 确保网络连接正常")
        print("- 如果端口5001被占用，请关闭其他程序")
        print("- 生成的exe文件可以直接分发给其他用户使用")
    else:
        print("\n❌ 打包失败！")
        print("请检查错误信息并重试")

if __name__ == "__main__":
    main() 
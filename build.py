#!/usr/bin/env python3
"""
抖音直播监控程序打包脚本
使用 PyInstaller 将 Flask 应用打包成可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def install_pyinstaller():
    """安装 PyInstaller"""
    print("正在安装 PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    print("PyInstaller 安装完成")

def create_spec_file():
    """创建 PyInstaller 配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 收集所有需要的数据文件
datas = [
    ('app_test/templates', 'templates'),
    ('sign.js', '.'),
    ('liveMan.py', '.'),
    ('protobuf', 'protobuf'),
    ('node_sign', 'node_sign'),
]

# 收集所有需要隐藏导入的模块
hiddenimports = [
    'flask',
    'flask_socketio',
    'engineio',
    'socketio',
    'requests',
    'betterproto',
    'websocket',
    'websocket_client',
    'PyExecJS',
    'mini_racer',
    'pandas',
    'openpyxl',
    'zipfile',
    'json',
    'threading',
    'multiprocessing',
    'subprocess',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'protobuf',
    'google.protobuf',
]

a = Analysis(
    ['app_test/app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DouyinLiveMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('DouyinLiveMonitor.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("PyInstaller 配置文件创建完成")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 使用 spec 文件构建
    subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "DouyinLiveMonitor.spec"
    ], check=True)
    
    print("可执行文件构建完成！")

def create_readme():
    """创建使用说明"""
    readme_content = '''# 抖音直播监控程序

## 使用说明

### Windows 用户
1. 双击运行 `DouyinLiveMonitor.exe`
2. 程序会自动启动浏览器并打开监控界面
3. 如果没有自动打开浏览器，请手动访问：http://localhost:5001

### macOS/Linux 用户
1. 在终端中运行：`./DouyinLiveMonitor`
2. 程序会自动启动浏览器并打开监控界面
3. 如果没有自动打开浏览器，请手动访问：http://localhost:5001

## 功能说明

1. **开始监控**：输入直播间ID，点击"开始监控"
2. **实时数据**：查看实时评论、在线观众、粉丝排行等数据
3. **导出数据**：点击"导出数据"下载Excel文件
4. **停止监控**：点击"停止监控"结束数据收集

## 注意事项

- 首次运行可能需要等待几秒钟程序启动
- 确保网络连接正常
- 如果端口5001被占用，请关闭其他占用该端口的程序
- 程序会自动处理签名验证和数据解析

## 技术支持

如有问题，请检查：
1. 网络连接是否正常
2. 直播间ID是否正确
3. 防火墙是否阻止了程序运行
'''
    
    with open('dist/README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("使用说明创建完成")

def create_batch_file():
    """创建 Windows 批处理文件"""
    batch_content = '''@echo off
echo 正在启动抖音直播监控程序...
echo.
echo 程序启动后会自动打开浏览器
echo 如果没有自动打开，请手动访问：http://localhost:5001
echo.
echo 按任意键退出...
DouyinLiveMonitor.exe
pause
'''
    
    with open('dist/启动监控程序.bat', 'w', encoding='gbk') as f:
        f.write(batch_content)
    print("Windows 启动脚本创建完成")

def create_shell_script():
    """创建 Linux/macOS 启动脚本"""
    shell_content = '''#!/bin/bash
echo "正在启动抖音直播监控程序..."
echo ""
echo "程序启动后会自动打开浏览器"
echo "如果没有自动打开，请手动访问：http://localhost:5001"
echo ""
echo "按 Ctrl+C 退出程序"
echo ""
./DouyinLiveMonitor
'''
    
    with open('dist/start_monitor.sh', 'w', encoding='utf-8') as f:
        f.write(shell_content)
    
    # 设置执行权限
    os.chmod('dist/start_monitor.sh', 0o755)
    print("Linux/macOS 启动脚本创建完成")

def main():
    """主函数"""
    print("=== 抖音直播监控程序打包工具 ===")
    print()
    
    # 检查是否在正确的目录
    if not os.path.exists('app_test/app.py'):
        print("错误：请在项目根目录运行此脚本")
        return
    
    try:
        # 安装 PyInstaller
        install_pyinstaller()
        
        # 创建配置文件
        create_spec_file()
        
        # 构建可执行文件
        build_executable()
        
        # 创建使用说明和启动脚本
        create_readme()
        create_batch_file()
        create_shell_script()
        
        print()
        print("=== 打包完成！ ===")
        print("可执行文件位置：dist/DouyinLiveMonitor")
        print("Windows 用户：双击 启动监控程序.bat")
        print("Linux/macOS 用户：运行 ./start_monitor.sh")
        print()
        print("注意：")
        print("1. 将 dist 文件夹中的所有文件复制给其他用户")
        print("2. 其他用户无需安装 Python 即可运行")
        print("3. 首次运行可能需要等待几秒钟启动")
        
    except Exception as e:
        print(f"打包过程中出现错误：{e}")
        return

if __name__ == "__main__":
    main() 
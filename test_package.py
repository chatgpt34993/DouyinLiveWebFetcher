#!/usr/bin/env python3
"""
测试打包程序的脚本
"""

import os
import subprocess
import time
import requests
import signal
import sys

def test_packaged_app():
    """测试打包后的应用程序"""
    print("=== 测试打包后的抖音直播监控程序 ===")
    print()
    
    # 检查可执行文件是否存在
    exe_path = "dist/DouyinLiveMonitor"
    if not os.path.exists(exe_path):
        print(f"错误：找不到可执行文件 {exe_path}")
        print("请先运行打包脚本：python build_windows.py")
        return False
    
    print(f"找到可执行文件：{exe_path}")
    print("文件大小：{:.1f} MB".format(os.path.getsize(exe_path) / (1024*1024)))
    print()
    
    # 启动程序
    print("正在启动程序...")
    try:
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # 等待程序启动
        print("等待程序启动...")
        time.sleep(5)
        
        # 检查程序是否还在运行
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print("程序启动失败！")
            print("标准输出：", stdout)
            print("错误输出：", stderr)
            return False
        
        # 测试Web服务器是否响应
        print("测试Web服务器...")
        try:
            response = requests.get("http://localhost:5001", timeout=10)
            if response.status_code == 200:
                print("✓ Web服务器正常运行")
                print("✓ 程序启动成功！")
                
                # 停止程序
                print("正在停止程序...")
                process.terminate()
                process.wait(timeout=10)
                print("✓ 程序已正常停止")
                return True
            else:
                print(f"✗ Web服务器响应异常：{response.status_code}")
                process.terminate()
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ 无法连接到Web服务器：{e}")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"✗ 启动程序时发生错误：{e}")
        return False

def main():
    """主函数"""
    try:
        success = test_packaged_app()
        if success:
            print()
            print("=== 测试通过！ ===")
            print("打包的程序可以正常运行")
            print("可以分发给其他用户使用")
        else:
            print()
            print("=== 测试失败！ ===")
            print("请检查打包过程是否有问题")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"测试过程中发生错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
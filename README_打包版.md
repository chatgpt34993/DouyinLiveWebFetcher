# 抖音直播监控程序 - 打包版本

## 🎯 项目概述

这是一个抖音直播监控程序，可以实时获取直播间的评论、在线观众、粉丝排行等数据，并支持导出为Excel文件。

## 📦 打包说明

### 已完成的打包

✅ **macOS版本**：`dist/DouyinLiveMonitor` (25MB)
- 适用于 macOS 系统
- 双击即可运行
- 自动打开浏览器显示监控界面

### 如何为Windows用户打包

由于你使用的是macOS系统，无法直接生成Windows的.exe文件。有以下几种解决方案：

#### 方案一：在Windows系统上打包（推荐）

1. 将整个项目文件夹复制到Windows系统
2. 在Windows上安装Python 3.9+
3. 运行：`python build_windows.py`
4. 生成：`dist/DouyinLiveMonitor.exe`

#### 方案二：使用虚拟机

1. 在macOS上安装Windows虚拟机
2. 在虚拟机中运行打包脚本
3. 生成Windows版本

#### 方案三：使用Docker交叉编译

```bash
# 使用Docker进行交叉编译（需要配置Docker环境）
docker run --rm -v "$PWD:/src" cdrx/pyinstaller-windows:python3
```

## 🚀 使用方法

### macOS用户

1. **下载文件**：接收 `DouyinLiveMonitor` 文件
2. **设置权限**：`chmod +x DouyinLiveMonitor`
3. **运行程序**：双击文件或在终端运行 `./DouyinLiveMonitor`
4. **开始监控**：在浏览器中输入直播间ID，点击"开始监控"

### Windows用户

1. **下载文件**：接收 `DouyinLiveMonitor.exe` 文件
2. **运行程序**：双击 `DouyinLiveMonitor.exe`
3. **开始监控**：程序会自动打开浏览器，输入直播间ID开始监控

## ✨ 主要功能

- 🔴 **实时监控**：获取直播间实时数据
- 💬 **评论收集**：收集直播间评论信息
- 👥 **在线观众**：显示实时在线观众数量
- 🏆 **粉丝排行**：获取粉丝排行榜数据
- 📊 **数据导出**：导出数据为Excel/ZIP文件
- 🎯 **简单易用**：图形化界面，操作简单

## 📋 系统要求

### 最低要求
- **操作系统**：Windows 10+ / macOS 10.14+ / Linux
- **内存**：4GB RAM
- **存储**：100MB 可用空间
- **网络**：稳定的互联网连接

### 推荐配置
- **操作系统**：Windows 11 / macOS 12+ / Ubuntu 20.04+
- **内存**：8GB RAM
- **存储**：1GB 可用空间
- **网络**：高速互联网连接

## 🔧 技术特性

- **单文件部署**：一个文件包含所有依赖
- **跨平台支持**：支持Windows、macOS、Linux
- **自动启动**：程序启动后自动打开浏览器
- **实时更新**：WebSocket实时数据推送
- **数据导出**：支持CSV和ZIP格式导出

## 📁 文件结构

```
DouyinLiveWebFetcher/
├── dist/                          # 打包输出目录
│   └── DouyinLiveMonitor         # macOS可执行文件
├── app_test/                      # 源代码目录
│   ├── app.py                    # Flask主程序
│   └── templates/                # 前端模板
├── liveMan.py                    # 直播监控核心
├── sign.js                       # 签名生成脚本
├── protobuf/                     # 协议缓冲区文件
├── node_sign/                    # Node.js签名模块
├── quick_build.py               # 快速打包脚本
├── build_windows.py             # Windows打包脚本
├── test_package.py              # 测试脚本
└── 打包说明.md                   # 详细打包说明
```

## 🛠️ 开发信息

### 依赖库
- Flask (Web框架)
- Flask-SocketIO (WebSocket支持)
- requests (HTTP请求)
- websocket-client (WebSocket客户端)
- pandas (数据处理)
- openpyxl (Excel处理)
- PyExecJS (JavaScript执行)
- mini_racer (V8引擎)

### 打包工具
- PyInstaller 6.14.1
- 单文件模式 (--onefile)
- 自动依赖检测

## ⚠️ 注意事项

### 安全提示
1. **杀毒软件**：Windows杀毒软件可能误报，请添加信任
2. **权限控制**：程序只需要网络访问权限
3. **数据安全**：导出的数据注意隐私保护

### 使用限制
1. **网络要求**：需要稳定的网络连接
2. **端口占用**：程序使用5001端口，确保端口未被占用
3. **浏览器支持**：需要现代浏览器支持

### 故障排除
1. **程序无法启动**：检查系统权限和端口占用
2. **浏览器未打开**：手动访问 http://localhost:5001
3. **网络连接失败**：检查防火墙和代理设置

## 📞 技术支持

### 常见问题

**Q: 程序启动后浏览器没有自动打开？**
A: 手动访问 http://localhost:5001

**Q: Windows杀毒软件报警怎么办？**
A: 添加程序到杀毒软件信任列表

**Q: 端口5001被占用怎么办？**
A: 关闭占用该端口的其他程序

**Q: 程序启动很慢？**
A: 这是正常现象，首次启动需要解压依赖文件

### 获取帮助

如果遇到问题，请提供以下信息：
1. 操作系统版本
2. 错误信息截图
3. 程序输出日志
4. 网络连接状态

## 📄 许可证

本项目仅用于学习和研究目的，请遵守相关法律法规和平台使用条款。

---

**版本**：v1.0  
**更新时间**：2025年6月26日  
**开发者**：AI Assistant 
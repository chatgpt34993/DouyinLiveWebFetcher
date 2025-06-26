# 抖音直播监控程序 - 打包版本

## 快速开始

### 打包Windows版本

#### 方式一：在Windows上直接打包（推荐）
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行打包脚本
python build_windows.py

# 3. 生成文件：dist/DouyinLiveMonitor.exe
```

#### 方式二：在macOS/Linux上使用Docker交叉编译
```bash
# 1. 安装Docker Desktop
# 2. 运行打包脚本
python build_windows.py
# 选择选项2：使用Docker构建Windows版本

# 3. 生成文件：dist/DouyinLiveMonitor.exe
```

### 使用打包版本

1. **Windows用户**：
   - 双击 `DouyinLiveMonitor.exe`
   - 程序会自动打开浏览器显示监控界面
   - 无需安装Python或其他依赖

2. **macOS/Linux用户**：
   - 运行 `./DouyinLiveMonitor`
   - 程序会自动打开浏览器显示监控界面

## 功能特性

- ✅ 实时监控抖音直播间
- ✅ 接收弹幕、礼物、进场消息
- ✅ 显示在线观众数量
- ✅ 导出数据到Excel
- ✅ 支持多直播间监控
- ✅ 一键启动，无需配置

## 系统要求

### Windows版本
- Windows 7/8/10/11
- 无需安装Python
- 需要网络连接

### macOS/Linux版本
- macOS 10.12+ 或 Linux
- 无需安装Python
- 需要网络连接

## 使用说明

1. **启动程序**：双击exe文件或运行可执行文件
2. **输入直播间ID**：在网页界面输入抖音直播间ID
3. **开始监控**：点击"开始监控"按钮
4. **查看数据**：实时查看弹幕、礼物、观众数等信息
5. **导出数据**：点击"导出数据"按钮下载Excel文件

## 注意事项

- 首次启动可能需要几秒钟
- 确保端口5001未被占用
- Windows版本可能被杀毒软件误报，请添加信任
- 生成的exe文件较大（100-200MB），这是正常的

## 故障排除

### 程序无法启动
- 检查端口5001是否被占用
- 关闭杀毒软件或添加信任
- 确保网络连接正常

### 无法监控直播间
- 检查直播间ID是否正确
- 确保直播间正在直播
- 检查网络连接

### 导出失败
- 确保有足够的磁盘空间
- 检查是否有监控数据
- 尝试重新启动程序

## 技术支持

如果遇到问题，请：
1. 查看程序日志输出
2. 检查网络连接
3. 重启程序
4. 联系技术支持

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的直播间监控功能
- 支持数据导出功能
- 提供Windows和macOS/Linux版本 
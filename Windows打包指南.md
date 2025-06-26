# Windows版本打包指南

## 问题说明

由于你使用的是macOS系统，无法直接生成Windows的.exe文件。PyInstaller只能在目标平台上生成对应平台的可执行文件。

## 解决方案

### 方案一：在Windows系统上打包（推荐）

#### 步骤1：准备文件
1. 将整个项目文件夹复制到Windows系统
2. 确保包含以下文件：
   ```
   DouyinLiveWebFetcher/
   ├── app_test/
   │   ├── app.py
   │   └── templates/
   ├── liveMan.py
   ├── sign.js
   ├── protobuf/
   ├── node_sign/
   ├── build_windows.py
   └── requirements.txt
   ```

#### 步骤2：安装Python
1. 下载并安装Python 3.9+：https://www.python.org/downloads/
2. 确保勾选"Add Python to PATH"
3. 打开命令提示符，验证安装：
   ```cmd
   python --version
   ```

#### 步骤3：安装依赖
```cmd
cd DouyinLiveWebFetcher
pip install -r requirements.txt
```

#### 步骤4：运行打包脚本
```cmd
python build_windows.py
```

#### 步骤5：获取结果
打包完成后，在 `dist` 目录下会生成：
- `DouyinLiveMonitor.exe` (Windows可执行文件)

### 方案二：使用Docker交叉编译

如果你有Docker环境，可以在macOS上使用Docker进行交叉编译：

#### 步骤1：安装Docker Desktop
1. 下载Docker Desktop：https://www.docker.com/products/docker-desktop
2. 安装并启动Docker

#### 步骤2：运行Docker打包脚本
```bash
python build_windows_docker.py
```

### 方案三：使用虚拟机

#### 步骤1：安装Windows虚拟机
1. 在macOS上安装Parallels Desktop或VMware Fusion
2. 创建Windows 10/11虚拟机

#### 步骤2：在虚拟机中打包
1. 将项目文件复制到虚拟机
2. 按照方案一的步骤在虚拟机中打包

## 详细操作步骤（方案一）

### 1. 环境准备

**Windows 10/11系统要求：**
- 至少4GB内存
- 至少2GB可用磁盘空间
- 网络连接

**Python环境：**
```cmd
# 检查Python版本
python --version

# 如果未安装，下载：https://www.python.org/downloads/
# 安装时勾选"Add Python to PATH"
```

### 2. 项目设置

```cmd
# 创建项目目录
mkdir DouyinLiveWebFetcher
cd DouyinLiveWebFetcher

# 复制项目文件（从macOS复制过来）
# 确保包含所有必要文件
```

### 3. 安装依赖

```cmd
# 升级pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 如果requirements.txt不存在，手动安装：
pip install flask flask-socketio requests betterproto websocket-client PyExecJS mini_racer pandas openpyxl
```

### 4. 运行打包

```cmd
# 运行Windows打包脚本
python build_windows.py
```

### 5. 验证结果

```cmd
# 检查生成的文件
dir dist

# 应该看到：
# DouyinLiveMonitor.exe
```

## 常见问题

### Q1: 打包过程中出现错误
**解决方案：**
1. 确保所有依赖都已正确安装
2. 检查Python版本是否为3.9+
3. 确保项目文件完整

### Q2: 生成的exe文件无法运行
**解决方案：**
1. 检查杀毒软件是否拦截
2. 以管理员身份运行
3. 检查Windows Defender设置

### Q3: 缺少某些模块
**解决方案：**
1. 重新安装依赖：`pip install -r requirements.txt`
2. 手动安装缺失的模块
3. 检查PyInstaller的hidden-import设置

### Q4: 文件太大
**解决方案：**
1. 使用UPX压缩（需要额外配置）
2. 排除不必要的模块
3. 使用文件夹模式而不是单文件模式

## 测试打包结果

### 1. 基本测试
```cmd
# 双击运行exe文件
# 或命令行运行：
DouyinLiveMonitor.exe
```

### 2. 功能测试
1. 程序启动后自动打开浏览器
2. 访问 http://localhost:5001
3. 输入直播间ID测试监控功能
4. 测试数据导出功能

### 3. 分发测试
1. 将exe文件复制到其他Windows电脑
2. 确保目标电脑没有Python环境
3. 测试程序是否能正常运行

## 优化建议

### 1. 文件大小优化
```cmd
# 使用UPX压缩（可选）
pip install upx
# 在打包命令中添加 --upx-dir 参数
```

### 2. 启动速度优化
```cmd
# 使用文件夹模式而不是单文件模式
# 去掉 --onefile 参数
```

### 3. 兼容性优化
```cmd
# 添加更多hidden-import
# 确保所有依赖都被正确包含
```

## 最终分发

打包成功后，你可以：

1. **直接分发exe文件**：将 `DouyinLiveMonitor.exe` 发送给Windows用户
2. **创建安装包**：使用NSIS等工具创建安装程序
3. **压缩分发**：将exe文件压缩后分发

## 注意事项

1. **杀毒软件**：Windows杀毒软件可能误报，需要添加信任
2. **权限问题**：某些功能可能需要管理员权限
3. **网络访问**：确保防火墙允许程序访问网络
4. **端口占用**：确保5001端口未被占用

---

**总结**：最简单的方法是直接将项目文件夹复制到Windows系统，然后运行 `python build_windows.py` 即可生成Windows版本。 
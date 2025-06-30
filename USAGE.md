# 🚀 Platform Agent 使用指南

## 快速开始

### 一键启动（推荐）
```bash
./run.sh
```

这个增强版脚本会自动：
- ✅ 检测操作系统（macOS/Ubuntu）
- ✅ 检查 Python 3.11 环境
- ✅ 安装 uv 包管理器（如果需要）
- ✅ 创建/验证虚拟环境
- ✅ 检查环境配置（.env 文件）
- ✅ 安装项目依赖
- ✅ 🆕 预加载 MCP 工具缓存（提升用户体验）
- ✅ 启动 Platform Agent

## 高级用法

### 环境检查
```bash
./run.sh --check-only
```
只检查环境是否就绪，不启动程序。现在包含工具缓存状态检查。

### 强制重装依赖
```bash
./run.sh --force-reinstall
```
强制重新安装所有 Python 依赖包。

### 🆕 强制刷新工具缓存
```bash
./run.sh --refresh-tools
```
强制刷新 MCP 工具缓存，用于：
- 首次运行时预加载工具
- 工具列表有更新时刷新缓存
- 缓存损坏时重建

### 显示帮助
```bash
./run.sh --help
```

## 🆕 工具缓存管理

### 自动管理（推荐）
启动脚本会自动管理工具缓存：
- **首次运行**：自动发现和缓存所有可用的 MCP 工具
- **日常使用**：检查缓存是否过期（24小时），必要时自动刷新
- **用户体验**：进入主程序时工具已就绪，无需等待

### 手动管理
使用 `tool_inspector.py` 进行精细化管理：
```bash
# 检查缓存状态
python src/tool_inspector.py --check

# 列出所有缓存的工具
python src/tool_inspector.py --list

# 强制刷新缓存
python src/tool_inspector.py --refresh
```

## 环境配置

### 1. 配置 API Key
首次运行时，脚本会自动创建 `.env` 模板文件。

你需要编辑 `.env` 文件：
```bash
# 编辑配置文件
nano .env

# 或者使用你喜欢的编辑器
code .env
```

### 2. 获取 OpenRouter API Key
1. 访问 [OpenRouter](https://openrouter.ai/keys)
2. 注册账户并获取 API Key
3. 将 API Key 填入 `.env` 文件

### 3. 可选配置
参考 `.env.example` 文件了解更多配置选项。

## 系统要求

### macOS
- Python 3.11.x（推荐通过 Homebrew 安装）
- 命令行工具：`xcode-select --install`

```bash
# 安装 Python 3.11
brew install python@3.11
```

### Ubuntu
- Python 3.11.x

```bash
# Ubuntu 20.04+
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip

# 或者使用 deadsnakes PPA (推荐)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip
```

## 🆕 用户体验优化

### 启动流程优化
1. **智能缓存**：工具在后台预加载，用户无需等待
2. **一键启动**：所有环境准备工作自动完成
3. **清晰反馈**：彩色日志清楚显示每个步骤的状态
4. **错误恢复**：提供明确的错误信息和修复建议

### 性能指标
- **首次启动**：约 30-60 秒（包含工具发现）
- **日常启动**：约 5-10 秒（缓存有效时）
- **工具可用性**：9+ MCP 工具立即可用

## 故障排除

### 常见问题

**1. Python 版本问题**
```bash
# 检查 Python 版本
python --version

# 如果不是 3.11.x，安装正确版本
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
```

**2. 工具缓存问题**
```bash
# 强制刷新工具缓存
./run.sh --refresh-tools

# 或者手动重建
rm tools_cache.json
./run.sh
```

**3. 虚拟环境问题**
```bash
# 删除并重建虚拟环境
rm -rf .venv
./run.sh
```

**4. 依赖安装失败**
```bash
# 强制重新安装依赖
./run.sh --force-reinstall
```

### 获取帮助

如果遇到问题：
1. 运行 `./run.sh --check-only` 检查环境状态
2. 查看错误日志中的具体错误信息
3. 参考上述故障排除步骤
4. 查看项目文档：`doc/` 目录

## 企业使用建议

### 开发环境
- 使用 Python 3.11.x（稳定性最佳）
- 定期运行 `./run.sh --check-only` 检查环境健康度
- 在 CI/CD 中使用 `python src/tool_inspector.py --refresh` 预构建工具缓存

### 生产部署
- 锁定依赖版本（已通过 `requirements.txt` 实现）
- 预构建工具缓存以减少启动时间
- 配置监控和日志收集

## 版本历史

### v2.0.0 🆕
- **新增**：智能工具缓存预加载
- **新增**：`--refresh-tools` 选项
- **优化**：启动流程用户体验
- **增强**：错误处理和恢复机制

### v1.0.0
- 基础启动脚本
- 环境检查和依赖管理
- 跨平台支持（macOS/Ubuntu） 
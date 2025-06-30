#!/bin/bash
#
# Platform Agent - 智能平台助手启动脚本
# 版本: 2.1 - 终极简化版
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/.venv"
PYTHON_VERSION="3.11"
FORCE_REINSTALL=false
REFRESH_TOOLS=false
VERIFY=false
CHECK_ONLY=false

# 显示帮助信息
show_help() {
    echo "=========================================="
    echo "    Platform Agent 启动脚本"
    echo "=========================================="
    echo
    echo "使用方法:"
    echo "  ./run.sh                    启动 Platform Agent"
    echo "  ./run.sh --force-reinstall  重新安装依赖"
    echo "  ./run.sh --refresh-tools    刷新工具缓存"
    echo "  ./run.sh --verify           系统验证"
    echo "  ./run.sh --check-only       仅检查环境"
    echo "  ./run.sh --help             显示帮助"
    echo
    echo "支持: macOS, Ubuntu | Python 3.11.x"
    echo "=========================================="
}

# 解析参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force-reinstall) FORCE_REINSTALL=true; shift ;;
            --refresh-tools) REFRESH_TOOLS=true; shift ;;
            --verify) VERIFY=true; shift ;;
            --check-only) CHECK_ONLY=true; shift ;;
            --help|-h) show_help; exit 0 ;;
            *) break ;;
        esac
    done
}

# 检测系统
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]] && command -v apt-get >/dev/null 2>&1; then
        echo "ubuntu"
    else
        echo "linux"
    fi
}

# 检查Python
check_python() {
    echo "[STEP] 检查 Python 环境..."
    
    local python_cmd=""
    for cmd in python${PYTHON_VERSION} python3.11 python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            local version=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
            if [[ "$version" == "$PYTHON_VERSION" ]]; then
                python_cmd="$cmd"
                echo "[SUCCESS] Python $($cmd --version 2>&1): $(command -v $cmd)"
                break
            fi
        fi
    done
    
    if [[ -z "$python_cmd" ]]; then
        echo "[ERROR] 未找到 Python $PYTHON_VERSION.x"
        echo
        echo "安装方法:"
        if [[ "$(detect_os)" == "ubuntu" ]]; then
            echo "  sudo apt update"
            echo "  sudo apt install python$PYTHON_VERSION python$PYTHON_VERSION-venv python$PYTHON_VERSION-pip"
        else
            echo "  访问 https://www.python.org/downloads/"
        fi
        exit 1
    fi
    
    echo "$python_cmd"
}

# 检查uv
check_uv() {
    echo "[STEP] 检查 uv 包管理器..."
    
    if ! command -v uv >/dev/null 2>&1; then
        echo "[WARNING] uv 未安装，正在安装..."
        if command -v curl >/dev/null 2>&1; then
            curl -LsSf https://astral.sh/uv/install.sh | sh
            export PATH="$HOME/.cargo/bin:$PATH"
        else
            echo "[ERROR] 需要curl命令来安装uv"
            exit 1
        fi
        
        if ! command -v uv >/dev/null 2>&1; then
            echo "[ERROR] uv 安装失败"
            exit 1
        fi
    fi
    
    echo "[SUCCESS] uv 已就绪: $(uv --version | cut -d' ' -f2)"
}

# 管理虚拟环境
manage_venv() {
    echo "[STEP] 管理虚拟环境..."
    
    local python_cmd=$1
    
    if [[ -d "$VENV_PATH" ]]; then
        local venv_python="$VENV_PATH/bin/python"
        if [[ -f "$venv_python" ]]; then
            local version=$($venv_python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
            if [[ "$version" == "$PYTHON_VERSION" ]]; then
                echo "[SUCCESS] 虚拟环境已存在: Python $($venv_python --version 2>&1)"
                return 0
            else
                echo "[WARNING] Python版本不匹配，重新创建..."
                rm -rf "$VENV_PATH"
            fi
        fi
    fi
    
    echo "[INFO] 创建虚拟环境..."
    $python_cmd -m venv "$VENV_PATH"
    
    if [[ ! -f "$VENV_PATH/bin/python" ]]; then
        echo "[ERROR] 虚拟环境创建失败"
        exit 1
    fi
    
    echo "[SUCCESS] 虚拟环境创建完成"
}

# 检查环境配置
check_env_config() {
    echo "[STEP] 检查环境配置..."
    
    if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
        echo "[WARNING] .env 文件不存在，创建模板..."
        cat > "$SCRIPT_DIR/.env" << 'EOF'
# OpenRouter API Key (必填)
OPENROUTER_API_KEY=your_api_key_here

# CrewAI 存储目录
CREWAI_STORAGE_DIR=./crew_memory
EOF
        echo "[INFO] 请编辑 .env 文件并配置 API Key"
        return 1
    fi
    
    if grep -q "your_api_key_here" "$SCRIPT_DIR/.env" 2>/dev/null; then
        echo "[WARNING] 请配置 .env 文件中的 API Key"
        return 1
    fi
    
    echo "[SUCCESS] 环境配置检查通过"
    return 0
}

# 安装依赖
install_dependencies() {
    echo "[STEP] 安装依赖..."
    
    cd "$SCRIPT_DIR"
    
    if [[ "$FORCE_REINSTALL" != "true" ]] && [[ -f "$VENV_PATH/pyvenv.cfg" ]]; then
        if $VENV_PATH/bin/python -c "import crewai, chromadb" 2>/dev/null; then
            echo "[SUCCESS] 依赖已安装"
            return 0
        fi
    fi
    
    source "$VENV_PATH/bin/activate"
    
    echo "[INFO] 安装依赖包..."
    $VENV_PATH/bin/python -m pip install --upgrade pip uv
    $VENV_PATH/bin/uv pip sync requirements.txt
    
    echo "[INFO] 验证依赖..."
    if ! $VENV_PATH/bin/python -c "import crewai, chromadb" 2>/dev/null; then
        echo "[ERROR] 关键依赖安装失败"
        exit 1
    fi
    
    echo "[SUCCESS] 依赖安装完成"
}

# 预加载工具缓存
preload_tools_cache() {
    echo "[STEP] 预加载工具缓存..."
    
    cd "$SCRIPT_DIR"
    source "$VENV_PATH/bin/activate"
    
    local cache_file="tools_cache.json"
    local need_refresh=false
    
    if [[ ! -f "$cache_file" ]] || [[ "$REFRESH_TOOLS" == "true" ]]; then
        need_refresh=true
    fi
    
    if [[ "$need_refresh" == "true" ]]; then
        echo "[INFO] 刷新工具缓存..."
        if $VENV_PATH/bin/python src/tool_inspector.py --refresh >/dev/null 2>&1; then
            echo "[SUCCESS] 工具缓存已更新"
        else
            echo "[WARNING] 工具缓存更新失败"
        fi
    else
        echo "[SUCCESS] 工具缓存已存在"
    fi
}

# 运行程序
run_program() {
    echo "[STEP] 启动 Platform Agent..."
    
    cd "$SCRIPT_DIR"
    source "$VENV_PATH/bin/activate"
    
    echo
    echo "Platform Agent - 智能平台助手 v2.1"
    echo "========================================="
    echo
    
    export PYTHONWARNINGS="ignore::pydantic.PydanticDeprecatedSince20"
    $VENV_PATH/bin/python -m src.main "$@"
}

# 清理
cleanup() {
    echo
    echo "[INFO] Platform Agent 会话结束"
    echo "========================================="
}

# 主函数
main() {
    trap cleanup EXIT
    
    echo "========================================="
    echo "    Platform Agent v2.1 - 启动中..."
    echo "========================================="
    echo
    
    parse_args "$@"
    
    echo "[INFO] 操作系统: $(detect_os)"
    
    local python_cmd=$(check_python)
    check_uv
    manage_venv "$python_cmd"
    
    if ! check_env_config && [[ "$CHECK_ONLY" == "true" ]]; then
        echo "[ERROR] 环境检查失败"
        exit 1
    fi
    
    install_dependencies
    preload_tools_cache
    
    if [[ "$VERIFY" == "true" ]]; then
        echo "[STEP] 运行系统验证..."
        $VENV_PATH/bin/python verify_setup.py
        exit $?
    fi
    
    if [[ "$CHECK_ONLY" == "true" ]]; then
        echo "[SUCCESS] 环境检查完成！"
        exit 0
    fi
    
    run_program "$@"
}

# 入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 
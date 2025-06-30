#!/bin/bash
#
# 🚀 Platform Agent - 智能平台助手启动脚本
# 支持 macOS 和 Ubuntu，自动检查环境、安装依赖、管理虚拟环境
#
# 使用方法:
#   ./run.sh                    # 正常启动
#   ./run.sh --force-reinstall  # 强制重新安装依赖
#   ./run.sh --check-only       # 只检查环境，不启动程序
#
# 作者: Platform Agent Team
# 版本: 2.0.0
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 全局变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/.venv"
PYTHON_VERSION="3.11"
FORCE_REINSTALL=false
REFRESH_TOOLS=false
VERIFY=false
CHECK_ONLY=false

# 工具函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo -e "${CYAN}🚀 Platform Agent 启动脚本${NC}"
    echo
    echo "使用方法:"
    echo "  ./run.sh                    正常启动 Platform Agent"
    echo "  ./run.sh --force-reinstall  强制重新安装所有依赖"
    echo "  ./run.sh --refresh-tools    强制刷新工具缓存"
    echo "  ./run.sh --verify           运行完整的系统验证"
    echo "  ./run.sh --check-only       只检查环境，不启动程序"
    echo "  ./run.sh --help             显示此帮助信息"
    echo
    echo "支持的操作系统: macOS, Ubuntu"
    echo "推荐 Python 版本: 3.11.x"
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force-reinstall)
                FORCE_REINSTALL=true
                shift
                ;;
            --refresh-tools)
                REFRESH_TOOLS=true
                shift
                ;;
            --verify)
                VERIFY=true
                shift
                ;;
            --check-only)
                CHECK_ONLY=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                # 其他参数传递给主程序
                break
                ;;
        esac
    done
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get >/dev/null 2>&1; then
            echo "ubuntu"
        else
            echo "linux"
        fi
    else
        echo "unknown"
    fi
}

# 检查和安装 Python
check_python() {
    log_step "检查 Python 环境..."
    
    local os_type=$(detect_os)
    local python_cmd=""
    
    # 尝试找到合适的 Python 版本
    for cmd in python${PYTHON_VERSION} python3.11 python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            local version=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
            local major_minor=$(echo "$version" | cut -d. -f1,2)
            
            if [[ "$major_minor" == "$PYTHON_VERSION" ]]; then
                python_cmd="$cmd"
                log_success "找到 Python $version: $(command -v $cmd)"
                break
            fi
        fi
    done
    
    if [[ -z "$python_cmd" ]]; then
        log_error "未找到 Python $PYTHON_VERSION.x"
        echo
        log_info "请安装 Python $PYTHON_VERSION.x:"
        
        case $os_type in
            "macos")
                echo "  brew install python@$PYTHON_VERSION"
                ;;
            "ubuntu")
                echo "  sudo apt update"
                echo "  sudo apt install python$PYTHON_VERSION python$PYTHON_VERSION-venv python$PYTHON_VERSION-pip"
                ;;
            *)
                echo "  请访问 https://www.python.org/downloads/ 下载安装"
                ;;
        esac
        exit 1
    fi
    
    echo "$python_cmd"
}

# 检查和安装 uv
check_uv() {
    log_step "检查 uv 包管理器..."
    
    if ! command -v uv >/dev/null 2>&1; then
        log_warning "uv 未安装，正在安装..."
        
        # 安装 uv
        if command -v curl >/dev/null 2>&1; then
            curl -LsSf https://astral.sh/uv/install.sh | sh
            source ~/.cargo/env 2>/dev/null || true
        elif command -v pip >/dev/null 2>&1; then
            pip install uv
        else
            log_error "无法安装 uv，请手动安装"
            echo "访问: https://docs.astral.sh/uv/getting-started/installation/"
            exit 1
        fi
        
        # 重新检查
        if ! command -v uv >/dev/null 2>&1; then
            log_error "uv 安装失败"
            exit 1
        fi
    fi
    
    local uv_version=$(uv --version | cut -d' ' -f2)
    log_success "uv 已就绪: v$uv_version"
}

# 管理虚拟环境
manage_venv() {
    log_step "管理 Python 虚拟环境..."
    
    local python_cmd=$1
    
    # 检查虚拟环境是否存在且使用正确的 Python 版本
    if [[ -d "$VENV_PATH" ]]; then
        local venv_python="$VENV_PATH/bin/python"
        if [[ -f "$venv_python" ]]; then
            local venv_version=$($venv_python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
            local venv_major_minor=$(echo "$venv_version" | cut -d. -f1,2)
            
            if [[ "$venv_major_minor" == "$PYTHON_VERSION" ]]; then
                log_success "虚拟环境已存在: Python $venv_version"
                return 0
            else
                log_warning "虚拟环境 Python 版本不匹配 ($venv_version != $PYTHON_VERSION.x)，重新创建..."
                rm -rf "$VENV_PATH"
            fi
        fi
    fi
    
    # 创建新的虚拟环境
    log_info "创建虚拟环境..."
    $python_cmd -m venv "$VENV_PATH"
    
    if [[ ! -f "$VENV_PATH/bin/python" ]]; then
        log_error "虚拟环境创建失败"
        exit 1
    fi
    
    local new_version=$($VENV_PATH/bin/python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    log_success "虚拟环境创建成功: Python $new_version"
}

# 检查环境配置
check_env_config() {
    log_step "检查环境配置..."
    
    if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
        log_warning ".env 文件不存在"
        log_info "请创建 .env 文件并配置以下变量:"
        echo "  OPENROUTER_API_KEY=your_api_key_here"
        echo "  CREWAI_STORAGE_DIR=./crew_memory"
        echo
        log_info "你可以复制 .env.example (如果存在) 或手动创建"
        
        # 创建基本的 .env 模板
        cat > "$SCRIPT_DIR/.env" << 'EOF'
# OpenRouter API Key (必填)
OPENROUTER_API_KEY=your_api_key_here

# CrewAI 记忆存储目录
CREWAI_STORAGE_DIR=./crew_memory

# 可选：调试模式
# DEBUG=true
EOF
        log_info "已创建 .env 模板文件，请编辑并填入正确的 API Key"
        return 1
    fi
    
    # 检查关键配置
    if ! grep -q "OPENROUTER_API_KEY" "$SCRIPT_DIR/.env" || grep -q "your_api_key_here" "$SCRIPT_DIR/.env"; then
        log_warning "请在 .env 文件中配置正确的 OPENROUTER_API_KEY"
        return 1
    fi
    
    log_success "环境配置检查通过"
    return 0
}

# 安装依赖
install_dependencies() {
    log_step "安装 Python 依赖..."
    
    cd "$SCRIPT_DIR"
    
    # 检查是否需要安装依赖
    if [[ ! $FORCE_REINSTALL == true ]] && [[ -f "$VENV_PATH/pyvenv.cfg" ]]; then
        # 检查依赖是否已安装
        if $VENV_PATH/bin/python -c "import crewai, chromadb" 2>/dev/null; then
            log_success "依赖已安装，跳过安装步骤"
            return 0
        fi
    fi
    
    if [[ $FORCE_REINSTALL == true ]]; then
        log_info "强制重新安装所有依赖..."
    fi
    
    # 激活虚拟环境并安装依赖
    source "$VENV_PATH/bin/activate"
    
    # 升级 pip 和 uv
    $VENV_PATH/bin/python -m pip install --upgrade pip uv
    
    # 使用 uv 安装依赖
    log_info "正在安装依赖包..."
    uv pip sync requirements.txt
    
    # 验证关键依赖
    log_info "验证关键依赖..."
    if ! $VENV_PATH/bin/python -c "import crewai; print('CrewAI:', crewai.__version__)" 2>/dev/null; then
        log_error "CrewAI 安装失败"
        exit 1
    fi
    
    if ! $VENV_PATH/bin/python -c "import chromadb; print('ChromaDB 安装成功')" 2>/dev/null; then
        log_error "ChromaDB 安装失败"
        exit 1
    fi
    
    log_success "所有依赖安装完成"
}

# 预加载工具缓存
preload_tools_cache() {
    log_step "预加载 MCP 工具缓存..."
    
    cd "$SCRIPT_DIR"
    source "$VENV_PATH/bin/activate"
    
    # 检查工具缓存是否存在和是否过期
    local cache_file="tools_cache.json"
    local should_refresh=false
    
    if [[ ! -f "$cache_file" ]]; then
        log_info "工具缓存不存在，正在创建..."
        should_refresh=true
    elif [[ $REFRESH_TOOLS == true ]]; then
        log_info "强制刷新工具缓存..."
        should_refresh=true
    else
        # 检查缓存是否过期（24小时）
        local cache_age=$(python3 -c "
import json
import os
from datetime import datetime, timedelta
try:
    if os.path.exists('$cache_file'):
        with open('$cache_file', 'r') as f:
            data = json.load(f)
        fetched_at = datetime.fromisoformat(data.get('fetched_at', ''))
        age = datetime.now() - fetched_at
        print('stale' if age > timedelta(hours=24) else 'fresh')
    else:
        print('missing')
except:
    print('error')
")
        
        if [[ "$cache_age" == "stale" ]]; then
            log_info "工具缓存已过期，正在刷新..."
            should_refresh=true
        elif [[ "$cache_age" == "error" ]]; then
            log_warning "工具缓存损坏，正在重建..."
            should_refresh=true
        else
            log_success "工具缓存最新，跳过刷新"
        fi
    fi
    
    # 如果需要刷新缓存
    if [[ "$should_refresh" == true ]]; then
        log_info "正在发现和缓存 MCP 工具..."
        
        # 使用 tool_inspector.py 刷新缓存
        if $VENV_PATH/bin/python src/tool_inspector.py --refresh >/dev/null 2>&1; then
            log_success "工具缓存已更新"
        else
            log_warning "工具缓存更新失败，将在运行时发现工具"
        fi
    fi
    
    # 显示缓存统计
    if [[ -f "$cache_file" ]]; then
        local tools_count=$(python3 -c "
import json
try:
    with open('$cache_file', 'r') as f:
        data = json.load(f)
    print(len(data.get('tools', [])))
except:
    print('0')
")
        log_success "工具缓存就绪：$tools_count 个工具可用"
    fi
}

# 运行主程序
run_main_program() {
    log_step "启动 Platform Agent..."
    
    cd "$SCRIPT_DIR"
    source "$VENV_PATH/bin/activate"
    
    echo
    echo -e "${CYAN}🚀 欢迎使用 Platform Agent - 智能平台助手${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # 设置环境变量以抑制 Pydantic 弃用警告
    export PYTHONWARNINGS="ignore::pydantic.PydanticDeprecatedSince20"
    
    # 运行主程序，传递所有参数
    $VENV_PATH/bin/python -m src.main "$@"
}

# 清理函数
cleanup() {
    echo
    log_info "Platform Agent 会话结束"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 主函数
main() {
    # 设置清理函数
    trap cleanup EXIT
    
    echo -e "${CYAN}"
    echo "██████╗ ██╗      █████╗ ████████╗███████╗ ██████╗ ██████╗ ███╗   ███╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗"
    echo "██╔══██╗██║     ██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗██╔══██╗████╗ ████║    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝"
    echo "██████╔╝██║     ███████║   ██║   █████╗  ██║   ██║██████╔╝██╔████╔██║    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   "
    echo "██╔═══╝ ██║     ██╔══██║   ██║   ██╔══╝  ██║   ██║██╔══██╗██║╚██╔╝██║    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   "
    echo "██║     ███████╗██║  ██║   ██║   ██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   "
    echo "╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   "
    echo -e "${NC}"
    echo -e "${CYAN}                    🤖 Platform Agent - 智能平台助手 v2.0                        ${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # 解析命令行参数
    parse_args "$@"
    
    # 检测操作系统
    local os_type=$(detect_os)
    log_info "操作系统: $os_type"
    
    # 环境检查和设置
    local python_cmd=$(check_python)
    check_uv
    manage_venv "$python_cmd"
    
    # 检查环境配置
    if ! check_env_config; then
        if [[ $CHECK_ONLY == true ]]; then
            log_error "环境检查失败"
            exit 1
        else
            log_warning "环境配置不完整，但继续运行..."
        fi
    fi
    
    # 安装依赖
    install_dependencies
    
    # 预加载工具缓存（提升用户体验）
    preload_tools_cache
    
    # 如果是验证模式，运行完整验证
    if [[ $VERIFY == true ]]; then
        log_step "运行完整系统验证..."
        echo
        $VENV_PATH/bin/python verify_setup.py
        exit $?
    fi
    
    # 如果只是检查模式，到这里就结束
    if [[ $CHECK_ONLY == true ]]; then
        log_success "环境检查完成，所有组件就绪！"
        exit 0
    fi
    
    # 运行主程序
    run_main_program "$@"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 
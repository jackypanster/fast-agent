#!/usr/bin/env python3
"""
Platform Agent 设置验证脚本

这个脚本验证 Platform Agent 的完整设置是否正确，包括：
- Python 环境
- 依赖包
- 环境配置
- 工具缓存
- 核心功能

使用方法:
    python verify_setup.py
"""

import sys
import json
import pathlib
import importlib
from datetime import datetime


def print_header(title):
    """打印格式化的标题"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")


def print_check(item, status, details=""):
    """打印检查结果"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {item}")
    if details:
        print(f"   {details}")


def check_python_version():
    """检查 Python 版本"""
    print_header("Python 环境检查")
    
    version = sys.version_info
    python_version = f"{version.major}.{version.minor}.{version.minor}"
    
    is_correct = version.major == 3 and version.minor == 11
    print_check(
        f"Python 版本: {python_version}",
        is_correct,
        "推荐使用 Python 3.11.x" if not is_correct else "版本正确"
    )
    
    return is_correct


def check_dependencies():
    """检查关键依赖"""
    print_header("依赖包检查")
    
    dependencies = [
        ("crewai", "CrewAI 核心框架"),
        ("chromadb", "向量数据库"),
        ("pydantic", "数据验证"),
        ("openai", "OpenAI 客户端"),
        ("requests", "HTTP 请求库"),
    ]
    
    all_ok = True
    for package, description in dependencies:
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', '未知版本')
            print_check(f"{description} ({package})", True, f"版本: {version}")
        except ImportError:
            print_check(f"{description} ({package})", False, "未安装")
            all_ok = False
    
    return all_ok


def check_environment_config():
    """检查环境配置"""
    print_header("环境配置检查")
    
    env_file = pathlib.Path(".env")
    if not env_file.exists():
        print_check(".env 文件", False, "文件不存在")
        return False
    
    print_check(".env 文件", True, "文件存在")
    
    # 读取环境变量
    env_content = env_file.read_text()
    has_api_key = "OPENROUTER_API_KEY" in env_content and "your_api_key_here" not in env_content
    
    print_check(
        "OpenRouter API Key",
        has_api_key,
        "已配置" if has_api_key else "需要配置真实的 API Key"
    )
    
    return has_api_key


def check_tools_cache():
    """检查工具缓存"""
    print_header("工具缓存检查")
    
    cache_file = pathlib.Path("tools_cache.json")
    if not cache_file.exists():
        print_check("工具缓存文件", False, "文件不存在")
        return False
    
    try:
        cache_data = json.loads(cache_file.read_text())
        
        # 检查缓存结构
        print_check("工具缓存文件", True, "文件存在且有效")
        
        # 检查工具数量
        tools = cache_data.get("tools", [])
        tools_count = len(tools)
        print_check(f"缓存的工具数量", tools_count > 0, f"{tools_count} 个工具")
        
        # 检查缓存时间
        fetched_at = cache_data.get("fetched_at")
        if fetched_at:
            fetch_time = datetime.fromisoformat(fetched_at)
            age = datetime.now() - fetch_time
            is_fresh = age.total_seconds() < 24 * 3600  # 24小时
            print_check(
                "缓存新鲜度",
                is_fresh,
                f"更新于 {fetch_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        
        # 显示工具类型统计
        if tools:
            tool_types = {}
            for tool in tools:
                name = tool.get("name", "unknown")
                prefix = name.split("_")[0] if "_" in name else "other"
                tool_types[prefix] = tool_types.get(prefix, 0) + 1
            
            print("\n📊 工具类型统计:")
            for tool_type, count in sorted(tool_types.items()):
                print(f"   • {tool_type}: {count} 个工具")
        
        return tools_count > 0
        
    except (json.JSONDecodeError, KeyError) as e:
        print_check("工具缓存文件", False, f"文件损坏: {e}")
        return False


def check_core_functionality():
    """检查核心功能"""
    print_header("核心功能检查")
    
    try:
        # 测试导入核心模块
        from src.ops_crew.crew import OpsCrew
        print_check("Platform Agent 核心模块", True, "导入成功")
        
        # 测试 CrewAI 基本功能
        from crewai import Agent, Task, Crew
        print_check("CrewAI 基本组件", True, "Agent, Task, Crew 可用")
        
        # 测试 LLM 配置
        try:
            from crewai import LLM
            print_check("LLM 组件", True, "LLM 类可用")
        except ImportError:
            print_check("LLM 组件", False, "导入失败")
        
        return True
        
    except ImportError as e:
        print_check("Platform Agent 核心模块", False, f"导入失败: {e}")
        return False


def generate_report(results):
    """生成验证报告"""
    print_header("验证结果总结")
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    print(f"📊 总体状态: {passed_checks}/{total_checks} 项检查通过")
    
    if passed_checks == total_checks:
        print("🎉 所有检查都通过了！Platform Agent 已准备就绪。")
        print("\n🚀 可以运行以下命令启动:")
        print("   ./run.sh")
        return True
    else:
        print("⚠️  存在一些问题需要解决:")
        
        for check_name, status in results.items():
            if not status:
                print(f"   • {check_name}")
        
        print("\n💡 建议的修复步骤:")
        
        if not results.get("Python 版本"):
            print("   1. 安装 Python 3.11.x")
        
        if not results.get("依赖包"):
            print("   2. 运行 ./run.sh --force-reinstall")
        
        if not results.get("环境配置"):
            print("   3. 编辑 .env 文件并配置 OPENROUTER_API_KEY")
        
        if not results.get("工具缓存"):
            print("   4. 运行 ./run.sh --refresh-tools")
        
        return False


def main():
    """主函数"""
    print("🤖 Platform Agent 设置验证工具")
    print("━" * 60)
    
    # 执行各项检查
    results = {
        "Python 版本": check_python_version(),
        "依赖包": check_dependencies(),
        "环境配置": check_environment_config(),
        "工具缓存": check_tools_cache(),
        "核心功能": check_core_functionality(),
    }
    
    # 生成报告
    success = generate_report(results)
    
    # 退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 
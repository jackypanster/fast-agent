#!/usr/bin/env python3
"""
MCP连接测试脚本
==============

使用公开的MCP服务器验证MCPServerAdapter的正确用法和工具加载功能。

测试目标：
- 验证MCPServerAdapter参数格式
- 确认工具加载逻辑
- 为修复本地MCP连接问题提供参考

测试服务器：
- URL: https://mcp.api-inference.modelscope.net/da81fcffd39044/sse
- 协议: SSE (与K8s MCP服务器相同)

使用方法：
    uv run test_mcp_connection.py
"""

import os
import sys
from typing import List, Dict, Any

# 添加src到路径以便导入模块
sys.path.insert(0, 'src')

def test_mcp_connection_method_1():
    """测试方法1: 使用字典参数"""
    print("🧪 测试方法1: MCPServerAdapter(dict参数)")
    
    try:
        from crewai_tools import MCPServerAdapter
        
        # 方法1: 字典参数 (当前使用的方式)
        server_params = {
            "url": "https://mcp.api-inference.modelscope.net/da81fcffd39044/sse",
            "transport": "sse"
        }
        
        print(f"   参数格式: {server_params}")
        mcp_adapter = MCPServerAdapter(server_params)
        tools = mcp_adapter.tools
        
        print(f"✅ 成功！加载了 {len(tools)} 个工具")
        
        # 显示工具详情
        for i, tool in enumerate(tools[:3]):  # 只显示前3个工具
            print(f"   工具{i+1}: {getattr(tool, 'name', 'Unknown')} - {getattr(tool, 'description', 'No description')[:50]}...")
        
        if len(tools) > 3:
            print(f"   ... 还有 {len(tools) - 3} 个工具")
            
        return True, tools
        
    except Exception as e:
        print(f"❌ 失败: {str(e)}")
        return False, None

def test_mcp_connection_method_2():
    """测试方法2: 使用关键字参数"""
    print("\n🧪 测试方法2: MCPServerAdapter(关键字参数)")
    
    try:
        from crewai_tools import MCPServerAdapter
        
        # 方法2: 关键字参数 (可能是之前工作的方式)
        mcp_adapter = MCPServerAdapter(
            url="https://mcp.api-inference.modelscope.net/da81fcffd39044/sse",
            transport="sse"
        )
        tools = mcp_adapter.tools
        
        print(f"✅ 成功！加载了 {len(tools)} 个工具")
        
        # 显示工具详情
        for i, tool in enumerate(tools[:3]):
            print(f"   工具{i+1}: {getattr(tool, 'name', 'Unknown')} - {getattr(tool, 'description', 'No description')[:50]}...")
        
        if len(tools) > 3:
            print(f"   ... 还有 {len(tools) - 3} 个工具")
            
        return True, tools
        
    except Exception as e:
        print(f"❌ 失败: {str(e)}")
        return False, None

def test_mcp_connection_method_3():
    """测试方法3: 使用位置参数"""
    print("\n🧪 测试方法3: MCPServerAdapter(位置参数)")
    
    try:
        from crewai_tools import MCPServerAdapter
        
        # 方法3: 位置参数
        server_params = {
            "url": "https://mcp.api-inference.modelscope.net/da81fcffd39044/sse",
            "transport": "sse"
        }
        mcp_adapter = MCPServerAdapter(server_params, )  # 可能需要额外参数
        tools = mcp_adapter.tools
        
        print(f"✅ 成功！加载了 {len(tools)} 个工具")
        return True, tools
        
    except Exception as e:
        print(f"❌ 失败: {str(e)}")
        return False, None

def test_our_current_implementation():
    """测试我们当前的实现"""
    print("\n🧪 测试当前Platform Agent实现")
    
    try:
        # 临时设置环境变量使用公开MCP服务器
        original_url = os.environ.get("K8S_MCP_URL", "")
        os.environ["K8S_MCP_URL"] = "https://mcp.api-inference.modelscope.net/da81fcffd39044/sse"
        
        from ops_crew.crew import OpsCrew
        
        crew_instance = OpsCrew()
        tools = crew_instance._load_mcp_tools_required()
        
        print(f"✅ 成功！Platform Agent加载了 {len(tools)} 个工具")
        
        # 恢复原始环境变量
        if original_url:
            os.environ["K8S_MCP_URL"] = original_url
        else:
            os.environ.pop("K8S_MCP_URL", None)
            
        return True, tools
        
    except Exception as e:
        print(f"❌ 失败: {str(e)}")
        
        # 恢复原始环境变量
        if original_url:
            os.environ["K8S_MCP_URL"] = original_url
        else:
            os.environ.pop("K8S_MCP_URL", None)
            
        return False, None

def analyze_tool_structure(tools: List[Any]):
    """分析工具结构"""
    print("\n🔍 工具结构分析:")
    
    if not tools:
        print("   没有工具可分析")
        return
    
    sample_tool = tools[0]
    print(f"   工具类型: {type(sample_tool)}")
    print(f"   工具属性: {dir(sample_tool)}")
    
    # 尝试获取工具的关键信息
    try:
        name = getattr(sample_tool, 'name', 'Unknown')
        description = getattr(sample_tool, 'description', 'No description')
        print(f"   示例工具名称: {name}")
        print(f"   示例工具描述: {description[:100]}...")
    except Exception as e:
        print(f"   获取工具信息失败: {e}")

def main():
    """主函数"""
    print("🚀 MCP连接测试开始")
    print("=" * 60)
    print("测试目标: https://mcp.api-inference.modelscope.net/da81fcffd39044/sse")
    print("协议: SSE")
    print()
    
    results = []
    
    # 测试不同的连接方法
    success1, tools1 = test_mcp_connection_method_1()
    results.append(("方法1 (字典参数)", success1))
    
    success2, tools2 = test_mcp_connection_method_2()
    results.append(("方法2 (关键字参数)", success2))
    
    success3, tools3 = test_mcp_connection_method_3()
    results.append(("方法3 (位置参数)", success3))
    
    success4, tools4 = test_our_current_implementation()
    results.append(("当前Platform Agent实现", success4))
    
    # 分析成功的工具
    successful_tools = None
    for tools in [tools1, tools2, tools3, tools4]:
        if tools:
            successful_tools = tools
            break
    
    if successful_tools:
        analyze_tool_structure(successful_tools)
    
    # 总结结果
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    
    for method, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"   {method}: {status}")
    
    # 提供建议
    successful_methods = [method for method, success in results if success]
    
    if successful_methods:
        print(f"\n💡 建议:")
        print(f"   成功的方法: {', '.join(successful_methods)}")
        print(f"   建议使用成功的方法修复Platform Agent")
    else:
        print(f"\n⚠️  所有方法都失败了")
        print(f"   可能需要检查:")
        print(f"   1. 网络连接")
        print(f"   2. MCPServerAdapter版本")
        print(f"   3. 依赖兼容性")
    
    return len(successful_methods) > 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生意外错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
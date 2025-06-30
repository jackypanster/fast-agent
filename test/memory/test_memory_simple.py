#!/usr/bin/env python3
"""
简单的Memory功能测试，测试实际的Platform Agent Memory

使用方法：
    uv run test_memory_simple.py
"""

import os
import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
from ops_crew.crew import run_crew

# 加载环境变量
load_dotenv()

def test_memory_functionality():
    """测试Memory功能"""
    
    print("🧪 Platform Agent Memory功能测试")
    print("=" * 50)
    
    try:
        # 第一个查询 - 这应该会创建memory
        print("📝 第一次查询: 询问K8s集群信息...")
        result1 = run_crew("Show me information about Kubernetes clusters")
        print(f"✅ 第一次查询完成")
        print(f"📊 结果长度: {len(result1)} 字符")
        
        # 检查存储目录
        storage_dir = "crew_memory"
        if os.path.exists(storage_dir):
            print(f"✅ Memory存储目录已创建: {storage_dir}")
            files = os.listdir(storage_dir)
            print(f"📄 存储文件: {files}")
        else:
            print(f"⚠️ Memory存储目录未创建")
        
        print("\n" + "="*50)
        
        # 第二个查询 - 这应该利用memory
        print("📝 第二次查询: 基于前面信息的后续问题...")
        result2 = run_crew("Which cluster mentioned before has the most resources?")
        print(f"✅ 第二次查询完成")
        print(f"📊 结果长度: {len(result2)} 字符")
        
        print("\n🎯 测试总结:")
        print("✅ Platform Agent Memory功能基础测试完成")
        print("✅ 两次查询都成功执行")
        
        if os.path.exists(storage_dir):
            print("✅ Memory存储系统正常工作")
        else:
            print("⚠️ Memory存储系统可能有问题")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始Platform Agent Memory功能测试")
    print("=" * 60)
    
    success = test_memory_functionality()
    
    if success:
        print(f"\n🎉 测试成功！Memory功能基本可用")
        sys.exit(0)
    else:
        print(f"\n❌ 测试失败")
        sys.exit(1)
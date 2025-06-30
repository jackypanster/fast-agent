#!/usr/bin/env python3
"""
临时测试文件：专门调试CrewAI Memory系统初始化问题
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加src到路径
sys.path.insert(0, 'src')

# 加载环境变量
load_dotenv()

print("=== CrewAI Memory系统调试 ===")
print()

# 测试1: 检查存储目录
print("=== 测试1: 存储目录检查 ===")
storage_dir = os.getenv("CREWAI_STORAGE_DIR", "./crew_memory")
print(f"配置的存储目录: {storage_dir}")
print(f"绝对路径: {Path(storage_dir).absolute()}")
print(f"目录是否存在: {Path(storage_dir).exists()}")

if not Path(storage_dir).exists():
    print("❌ 存储目录不存在 - 这是Memory系统没有初始化的证据")
else:
    print("✅ 存储目录存在")
    for item in Path(storage_dir).iterdir():
        print(f"   - {item.name}")

print()

# 测试2: 手动创建存储目录测试
print("=== 测试2: 手动创建存储目录 ===")
try:
    Path(storage_dir).mkdir(exist_ok=True)
    print(f"✅ 存储目录创建成功: {storage_dir}")
except Exception as e:
    print(f"❌ 存储目录创建失败: {e}")

print()

# 测试3: 导入CrewAI相关模块
print("=== 测试3: CrewAI模块导入 ===")
try:
    from crewai import Agent, Crew, Process, Task, LLM
    print("✅ CrewAI 核心模块导入成功")
except Exception as e:
    print(f"❌ CrewAI 核心模块导入失败: {e}")

try:
    import chromadb
    print("✅ ChromaDB 导入成功")
    print(f"   ChromaDB 版本: {chromadb.__version__}")
except Exception as e:
    print(f"❌ ChromaDB 导入失败: {e}")

print()

# 测试4: 创建最小的Memory-enabled Crew
print("=== 测试4: 最小Memory Crew测试 ===")
try:
    # 配置Qwen embedding
    qwen_embedder_config = {
        "provider": "openai",
        "config": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "api_base": os.getenv("QWEN_API_BASE"),
            "model": os.getenv("QWEN_EMBEDDING_MODEL")
        }
    }
    
    # 创建简单的LLM
    llm = LLM(
        model=os.getenv("MODEL", "openrouter/google/gemini-2.5-flash-preview-05-20"),
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.1
    )
    
    # 创建简单的Agent
    test_agent = Agent(
        role="Test Agent",
        goal="Test memory functionality",
        backstory="A simple test agent",
        llm=llm,
        verbose=True
    )
    
    # 创建简单的Task
    test_task = Task(
        description="Say hello and remember this conversation",
        expected_output="A greeting message",
        agent=test_agent
    )
    
    print("✅ Agent和Task创建成功")
    
    # 尝试创建带Memory的Crew
    print("   尝试创建带Memory的Crew...")
    test_crew = Crew(
        agents=[test_agent],
        tasks=[test_task],
        process=Process.sequential,
        verbose=True,
        memory=True,
        embedder=qwen_embedder_config
    )
    
    print("✅ 带Memory的Crew创建成功!")
    
    # 检查存储目录是否被创建
    if Path(storage_dir).exists():
        print(f"✅ Memory初始化后存储目录存在")
        files = list(Path(storage_dir).rglob("*"))
        if files:
            print(f"   发现 {len(files)} 个文件/目录:")
            for f in files[:10]:  # 只显示前10个
                print(f"     - {f.relative_to(storage_dir)}")
        else:
            print("   目录为空")
    else:
        print(f"❌ Memory初始化后存储目录仍不存在")
    
except Exception as e:
    print(f"❌ Memory Crew创建失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=== 调试完成 ===")
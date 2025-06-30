#!/usr/bin/env python3
"""
简化的CrewAI Memory测试，不使用MCP工具

测试目标：
1. 测试CrewAI + Qwen embedding的基本Memory功能
2. 验证存储目录创建和数据保存
3. 测试跨任务的记忆功能

使用方法：
    uv run test_crew_memory_simple.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_crew_memory_with_qwen():
    """测试CrewAI Memory功能与Qwen embedding"""
    
    print("🧪 CrewAI + Qwen Memory功能测试")
    print("=" * 50)
    
    try:
        from crewai import Agent, Crew, Task, LLM
        from langchain_openai import OpenAIEmbeddings
        
        print("✅ 成功导入CrewAI和LangChain")
        
        # 配置LLM
        llm = LLM(
            model=os.getenv("MODEL", "openrouter/google/gemini-2.5-flash-preview-05-20"),
            base_url=os.getenv("BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            temperature=0.1
        )
        print("✅ LLM配置成功")
        
        # 配置Qwen embeddings
        qwen_embeddings = OpenAIEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY"),  # 这是Qwen的key
            base_url=os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            model=os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v4"),
            show_progress_bar=False
        )
        print("✅ Qwen embeddings配置成功")
        
        # 创建Agent
        memory_agent = Agent(
            role='Memory Test Agent',
            goal='Test memory functionality and remember information across tasks',
            backstory='An intelligent agent designed to test memory capabilities',
            llm=llm,
            verbose=True
        )
        print("✅ Agent创建成功")
        
        # 第一个任务：记住信息
        task1 = Task(
            description="""
            Remember these facts:
            - The production cluster is called 'prod-cluster-1'
            - It has 5 nodes and 100 pods
            - It's running Kubernetes version 1.28
            - The main application is called 'web-service'
            
            Respond with: "I have memorized the production cluster information"
            """,
            agent=memory_agent,
            expected_output='Confirmation that production cluster information has been memorized'
        )
        
        # 创建第一个crew来执行第一个任务
        print("\n🧠 执行第一个任务：记忆信息...")
        crew1 = Crew(
            agents=[memory_agent],
            tasks=[task1],
            memory=True,
            embedder={
                "provider": "openai",
                "config": {
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "api_base": os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                    "model": os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v4")
                }
            },
            verbose=True
        )
        
        result1 = crew1.kickoff()
        print(f"📊 第一个任务结果: {result1}")
        
        # 检查存储目录
        storage_dir = Path(os.getenv("CREWAI_STORAGE_DIR", "./crew_memory"))
        print(f"\n📁 检查存储目录: {storage_dir}")
        
        if storage_dir.exists():
            print(f"✅ 存储目录已创建")
            files = list(storage_dir.iterdir())
            print(f"📄 存储文件: {[f.name for f in files]}")
            
            for file in files:
                if file.is_file():
                    size = file.stat().st_size
                    print(f"   {file.name}: {size} bytes")
        else:
            print(f"⚠️ 存储目录未创建")
        
        # 第二个任务：回忆信息
        print(f"\n🧠 执行第二个任务：回忆信息...")
        
        task2 = Task(
            description="""
            Based on what you remember about the production cluster:
            1. What is the name of the production cluster?
            2. How many nodes does it have?
            3. What application is running on it?
            
            Use your memory to answer these questions.
            """,
            agent=memory_agent,
            expected_output='Answers based on previously memorized information'
        )
        
        # 创建第二个crew（共享相同的存储）
        crew2 = Crew(
            agents=[memory_agent],
            tasks=[task2],
            memory=True,
            embedder={
                "provider": "openai",
                "config": {
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "api_base": os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                    "model": os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v4")
                }
            },
            verbose=True
        )
        
        result2 = crew2.kickoff()
        print(f"📊 第二个任务结果: {result2}")
        
        # 分析结果
        print(f"\n🎯 Memory功能分析:")
        
        # 检查第二个结果是否包含第一个任务中的信息
        if "prod-cluster-1" in str(result2):
            print("✅ Memory功能工作正常：能够回忆集群名称")
        else:
            print("⚠️ Memory功能可能有问题：无法回忆集群名称")
        
        if "5" in str(result2) and ("node" in str(result2).lower()):
            print("✅ Memory功能工作正常：能够回忆节点数量")
        else:
            print("⚠️ Memory功能可能有问题：无法回忆节点数量")
        
        if "web-service" in str(result2):
            print("✅ Memory功能工作正常：能够回忆应用名称")
        else:
            print("⚠️ Memory功能可能有问题：无法回忆应用名称")
        
        print(f"\n✅ CrewAI + Qwen Memory测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始CrewAI + Qwen Memory集成测试")
    print("=" * 60)
    
    success = test_crew_memory_with_qwen()
    
    if success:
        print(f"\n🎉 测试成功！Qwen embedding已成功集成到CrewAI Memory系统")
    else:
        print(f"\n❌ 测试失败，需要进一步调试")
    
    sys.exit(0 if success else 1)
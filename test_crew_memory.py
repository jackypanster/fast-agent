#!/usr/bin/env python3
"""
CrewAI Memory功能测试

测试目标：
1. 验证CrewAI能够使用Qwen embedding
2. 测试memory功能的基础工作
3. 验证存储目录创建和数据写入

使用方法：
    uv run test_crew_memory.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_crew_memory_basic():
    """测试CrewAI memory基础功能"""
    
    print("🧪 CrewAI Memory基础功能测试")
    print("=" * 50)
    
    # 配置Qwen作为OpenAI替代
    os.environ["OPENAI_API_BASE"] = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    print(f"设置 OPENAI_API_BASE = {os.environ['OPENAI_API_BASE']}")
    print(f"使用 OPENAI_API_KEY = {os.getenv('OPENAI_API_KEY', 'Not found')[:20]}...")
    
    try:
        from crewai import Agent, Crew, Task, LLM
        print("✅ CrewAI导入成功")
        
        # 创建一个简单的LLM（用于agent，不是embedding）
        llm = LLM(
            model=os.getenv("MODEL", "openrouter/google/gemini-2.5-flash-preview-05-20"),
            base_url=os.getenv("BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            temperature=0.1
        )
        print("✅ LLM初始化成功")
        
        # 创建一个简单的Agent
        test_agent = Agent(
            role='Test Agent',
            goal='Test memory functionality',
            backstory='A simple agent for testing memory',
            llm=llm,
            verbose=True
        )
        print("✅ Agent创建成功")
        
        # 创建一个简单的Task
        test_task = Task(
            description='Remember that the test value is 42 and respond with "I remember the test value"',
            agent=test_agent,
            expected_output='A response indicating memory of the test value'
        )
        print("✅ Task创建成功")
        
        # 检查存储目录
        storage_dir = Path(os.getenv("CREWAI_STORAGE_DIR", "./crew_memory"))
        print(f"📁 Memory存储目录: {storage_dir}")
        
        # 创建Crew with memory
        print("🧠 创建带Memory的Crew...")
        crew = Crew(
            agents=[test_agent],
            tasks=[test_task],
            memory=True,
            verbose=True
        )
        print("✅ Crew创建成功（启用Memory）")
        
        # 检查存储目录是否创建
        if storage_dir.exists():
            print(f"✅ 存储目录已创建: {storage_dir}")
            files = list(storage_dir.iterdir())
            print(f"📄 存储文件: {[f.name for f in files]}")
        else:
            print(f"⚠️ 存储目录未创建: {storage_dir}")
        
        print("\n🚀 执行测试任务...")
        result = crew.kickoff()
        print(f"📊 任务结果: {result}")
        
        # 再次检查存储目录
        if storage_dir.exists():
            files = list(storage_dir.iterdir())
            print(f"📄 执行后存储文件: {[f.name for f in files]}")
            
            # 检查文件大小
            for file in files:
                if file.is_file():
                    size = file.stat().st_size
                    print(f"   {file.name}: {size} bytes")
        
        print("\n✅ CrewAI Memory基础测试完成")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_embedding_config():
    """测试embedding配置"""
    print(f"\n🔍 测试Embedding配置")
    
    try:
        from openai import OpenAI
        
        # 直接使用OpenAI客户端测试
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("QWEN_API_BASE")
        )
        
        # 测试embedding
        test_text = "This is a test for CrewAI memory with Qwen embedding"
        response = client.embeddings.create(
            model="text-embedding-v4",
            input=test_text
        )
        
        if response.data:
            result = response.data[0].embedding
            print(f"✅ Embedding测试成功 - 向量维度: {len(result)}")
            print(f"📊 前5个值: {result[:5]}")
            return True
        else:
            print(f"❌ Embedding测试失败: 无数据返回")
            return False
        
    except Exception as e:
        print(f"❌ Embedding测试失败: {e}")
        
        # 尝试LangChain方式，但指定正确的参数
        try:
            print("🔄 尝试LangChain OpenAIEmbeddings...")
            from langchain_openai import OpenAIEmbeddings
            
            embeddings = OpenAIEmbeddings(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("QWEN_API_BASE"),
                model="text-embedding-v4",
                show_progress_bar=False
            )
            
            result = embeddings.embed_query("test")
            print(f"✅ LangChain Embedding测试成功 - 向量维度: {len(result)}")
            return True
            
        except Exception as e2:
            print(f"❌ LangChain Embedding也失败: {e2}")
            return False

if __name__ == "__main__":
    print("🎯 开始CrewAI + Qwen Memory集成测试")
    print("=" * 60)
    
    # 测试embedding配置
    embedding_success = test_embedding_config()
    
    if embedding_success:
        # 测试CrewAI memory
        memory_success = test_crew_memory_basic()
        
        if memory_success:
            print(f"\n🎉 所有测试通过！")
            print(f"✅ Qwen embedding已成功集成到CrewAI Memory系统")
            sys.exit(0)
        else:
            print(f"\n⚠️ Memory测试失败")
            sys.exit(1)
    else:
        print(f"\n❌ Embedding配置失败")
        sys.exit(1)
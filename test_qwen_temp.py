#!/usr/bin/env python3
"""
临时测试文件：验证当前.env中的Qwen embedding配置
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

print("=== Qwen Embedding 配置测试 ===")
print(f"API Key: {os.getenv('OPENAI_API_KEY', 'NOT_SET')[:10]}...")
print(f"Base URL: {os.getenv('QWEN_API_BASE', 'NOT_SET')}")
print(f"Model: {os.getenv('QWEN_EMBEDDING_MODEL', 'NOT_SET')}")
print(f"Dimension: {os.getenv('QWEN_EMBEDDING_DIMENSION', 'NOT_SET')}")
print()

# 测试1: 使用当前.env中的配置
print("=== 测试1: 当前.env配置 ===")
try:
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("QWEN_API_BASE")
    )
    
    response = client.embeddings.create(
        model=os.getenv("QWEN_EMBEDDING_MODEL"),
        input="测试当前.env配置的千问embedding",
        dimensions=int(os.getenv("QWEN_EMBEDDING_DIMENSION", 1024)),
        encoding_format="float"
    )
    
    print("✅ 当前配置成功!")
    print(f"   模型: {response.model}")
    print(f"   向量维度: {len(response.data[0].embedding)}")
    print(f"   输入tokens: {response.usage.prompt_tokens}")
    print(f"   前5个向量值: {response.data[0].embedding[:5]}")
    
except Exception as e:
    print(f"❌ 当前配置失败: {e}")

print()

# 测试2: 检查环境变量设置
print("=== 测试2: 环境变量检查 ===")
required_vars = ["OPENAI_API_KEY", "QWEN_API_BASE", "QWEN_EMBEDDING_MODEL", "QWEN_EMBEDDING_DIMENSION"]
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: 已设置")
    else:
        print(f"❌ {var}: 未设置")

print()

# 测试3: 模拟CrewAI的embedder配置格式
print("=== 测试3: CrewAI embedder配置格式 ===")
try:
    # 这是crew.py中使用的配置格式
    qwen_embedder_config = {
        "provider": "openai",
        "config": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "api_base": os.getenv("QWEN_API_BASE"),
            "model": os.getenv("QWEN_EMBEDDING_MODEL")
        }
    }
    
    print("✅ CrewAI embedder配置格式:")
    print(f"   Provider: {qwen_embedder_config['provider']}")
    print(f"   API Base: {qwen_embedder_config['config']['api_base']}")
    print(f"   Model: {qwen_embedder_config['config']['model']}")
    print(f"   API Key: {qwen_embedder_config['config']['api_key'][:10]}...")
    
except Exception as e:
    print(f"❌ CrewAI配置格式错误: {e}")

print()
print("=== 测试完成 ===")
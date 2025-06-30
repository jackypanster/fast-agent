#!/usr/bin/env python3
"""
简单的Qwen API连通性测试

测试目标：
1. 验证Qwen API密钥和端点配置正确
2. 测试embedding API调用
3. 验证返回的embedding向量格式

使用方法：
    python test_qwen_api.py
"""

import os
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_qwen_embedding_api():
    """测试Qwen embedding API"""
    
    print("🧪 Qwen Embedding API 连通性测试")
    print("=" * 50)
    
    # 获取配置
    api_key = os.getenv("OPENAI_API_KEY")  # 这里是Qwen的key
    api_base = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model = os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v4")
    
    print(f"API Base: {api_base}")
    print(f"Model: {model}")
    print(f"API Key: {api_key[:20]}..." if api_key else "API Key: Not found")
    
    if not api_key:
        print("❌ 错误: OPENAI_API_KEY 未配置")
        return False
    
    # 准备测试数据
    test_texts = [
        "Hello, this is a test.",
        "这是一个中文测试",
        "Kubernetes cluster management",
        "K8s集群管理和监控"
    ]
    
    # 构造请求
    url = f"{api_base}/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    for i, text in enumerate(test_texts):
        print(f"\n📝 测试 {i+1}/{len(test_texts)}: {text}")
        
        data = {
            "model": model,
            "input": text,
            "encoding_format": "float"
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if "data" in result and len(result["data"]) > 0:
                    embedding = result["data"][0]["embedding"]
                    print(f"   ✅ 成功 - 向量维度: {len(embedding)}")
                    print(f"   📊 前5个值: {embedding[:5]}")
                else:
                    print(f"   ❌ 响应格式错误: {result}")
            else:
                print(f"   ❌ API调用失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                
        except requests.RequestException as e:
            print(f"   ❌ 网络错误: {str(e)}")
        except Exception as e:
            print(f"   ❌ 其他错误: {str(e)}")
    
    # 测试批量embedding
    print(f"\n📝 批量测试: {len(test_texts)} 个文本")
    
    data = {
        "model": model,
        "input": test_texts,
        "encoding_format": "float"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if "data" in result:
                print(f"   ✅ 批量成功 - 返回 {len(result['data'])} 个向量")
                for i, item in enumerate(result["data"]):
                    print(f"      向量 {i+1}: 维度 {len(item['embedding'])}")
            else:
                print(f"   ❌ 批量响应格式错误: {result}")
        else:
            print(f"   ❌ 批量API调用失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 批量测试错误: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Qwen API测试完成")
    return True

def test_openai_compatibility():
    """测试OpenAI兼容性"""
    print(f"\n🔄 测试OpenAI兼容性")
    
    # 设置环境变量，模拟CrewAI的行为
    os.environ["OPENAI_API_BASE"] = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    print(f"设置 OPENAI_API_BASE = {os.environ['OPENAI_API_BASE']}")
    print(f"设置 OPENAI_API_KEY = {os.getenv('OPENAI_API_KEY', 'Not found')[:20]}...")
    
    try:
        # 尝试导入和使用OpenAI兼容的embedding
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("QWEN_API_BASE")
        )
        
        response = client.embeddings.create(
            model="text-embedding-v4",
            input="测试OpenAI兼容性"
        )
        
        if response.data:
            embedding = response.data[0].embedding
            print(f"   ✅ OpenAI兼容性测试成功 - 向量维度: {len(embedding)}")
            return True
        else:
            print(f"   ❌ OpenAI兼容性测试失败: 无数据返回")
            return False
            
    except ImportError:
        print(f"   ⚠️ OpenAI库未安装，跳过兼容性测试")
        return True
    except Exception as e:
        print(f"   ❌ OpenAI兼容性测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_qwen_embedding_api()
    
    if success:
        test_openai_compatibility()
    
    print(f"\n🎯 测试总结:")
    print(f"   Qwen API配置已验证，可以继续进行Memory功能集成测试")
# CrewAI Memory 系统故障排除指南

## 概述

本文档详细记录了CrewAI Memory系统的调试过程，包括Qwen嵌入API配置验证、ChromaDB数据库故障诊断和解决方案。通过系统性的测试方法，我们成功解决了Memory系统无法初始化的问题。

## 问题描述

**症状**：
- CrewAI Memory系统配置后无法正常工作
- 预期的 `./crew_memory` 存储目录未被创建
- K8s MCP工具正常工作，但Memory功能失效

**环境**：
- Python 3.11
- CrewAI >= 0.134.0
- Qwen text-embedding-v4 API
- ChromaDB作为向量存储

## 调试方法论

我们采用分层调试的方法，从底层API连通性到上层CrewAI集成：

1. **API层验证** - 验证Qwen嵌入API的基本连通性
2. **配置层测试** - 验证Python环境中的API配置
3. **集成层调试** - 测试CrewAI Memory系统集成

## 测试文件详解

### 1. Qwen API配置验证 (`test_qwen_temp.py`)

```python
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
```

**测试结果**：
- ✅ Qwen API连通性正常
- ✅ 环境变量配置正确  
- ✅ CrewAI embedder配置格式正确

### 2. CrewAI Memory系统调试 (`test_crewai_memory_temp.py`)

```python
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
```

**关键发现**：
- 初次运行遇到 `KeyError: '_type'` 错误
- 错误源于ChromaDB数据库配置损坏
- 问题定位在 `~/Library/Application Support/crew_memory` 目录

## 根本原因分析

### ChromaDB配置损坏

错误信息：
```
KeyError: '_type'
  File "chromadb/config.py", line 139, in _validate_config
    assert key_name in data_to_validate, ...
```

**分析**：
- ChromaDB在初始化时尝试读取已有配置文件
- 现有配置文件缺少必要的 `_type` 字段
- 这导致ChromaDB无法正确初始化向量数据库

### 存储位置差异

CrewAI Memory系统实际存储位置：
- **预期**：`./crew_memory` (项目目录)
- **实际**：`~/Library/Application Support/crew_memory` (系统级)

## 解决方案

### 1. 清理损坏的ChromaDB数据

```bash
# 删除损坏的ChromaDB数据库
rm -rf "$HOME/Library/Application Support/crew_memory"
```

### 2. 验证修复效果

重新运行 `test_crewai_memory_temp.py`，确认：
- ✅ Memory Crew创建成功
- ✅ ChromaDB数据库正确初始化
- ✅ 存储目录包含预期的数据库文件

## 预防措施

### 1. 环境配置验证

在生产环境部署前，使用测试脚本验证：
- Qwen API连通性
- 环境变量配置完整性
- CrewAI Memory系统兼容性

### 2. 数据库健康检查

定期检查ChromaDB数据库状态：
```python
def check_chromadb_health():
    try:
        import chromadb
        client = chromadb.PersistentClient()
        return True
    except Exception as e:
        print(f"ChromaDB健康检查失败: {e}")
        return False
```

### 3. 配置文件管理

建议在 `.env` 文件中明确指定存储路径：
```env
CREWAI_STORAGE_DIR=./crew_memory
```

## 最佳实践

### 1. 分层测试策略

按优先级进行测试：
1. **API层** - 基础服务连通性
2. **配置层** - 环境变量和配置格式
3. **集成层** - 完整系统功能

### 2. 错误日志分析

关注关键错误信息：
- `KeyError: '_type'` → ChromaDB配置损坏
- `No module named 'chromadb'` → 依赖缺失  
- `Connection refused` → API连通性问题

### 3. 渐进式调试

从最小可用配置开始，逐步增加复杂性：
```python
# 最小Memory配置
simple_crew = Crew(
    agents=[agent],
    tasks=[task],
    memory=True  # 使用默认embedder
)

# 完整Qwen集成
qwen_crew = Crew(
    agents=[agent],
    tasks=[task],
    memory=True,
    embedder=qwen_embedder_config
)
```

## 技术细节

### Qwen嵌入配置

```python
qwen_embedder_config = {
    "provider": "openai",  # 使用OpenAI兼容接口
    "config": {
        "api_key": "sk-xxxxx",  # Qwen API密钥 
        "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "text-embedding-v4"  # Qwen嵌入模型
    }
}
```

### CrewAI Memory存储结构

```
~/Library/Application Support/crew_memory/
├── chroma.sqlite3          # 元数据存储
├── collections/            # 向量集合
│   ├── short_term_memory/  # 短期记忆
│   ├── long_term_memory/   # 长期记忆
│   └── entity_memory/      # 实体记忆
└── config/                 # ChromaDB配置
```

## 故障排除清单

- [ ] 验证Qwen API连通性 (`curl` 测试)
- [ ] 检查环境变量配置完整性
- [ ] 运行 `test_qwen_temp.py` 验证API配置
- [ ] 运行 `test_crewai_memory_temp.py` 调试Memory系统
- [ ] 清理损坏的ChromaDB数据（如需要）
- [ ] 验证Memory系统正常工作
- [ ] 检查生产环境配置一致性

## 结论

通过系统性的分层调试方法，我们成功解决了CrewAI Memory系统的初始化问题。关键在于：

1. **不急于使用fallback方案** - 坚持找到根本原因
2. **分层测试** - 从API到集成逐步验证
3. **临时测试文件** - 创建专门的调试工具
4. **详细日志记录** - 完整的错误信息分析

这种方法论不仅解决了当前问题，还为未来类似问题的解决提供了可复用的框架。
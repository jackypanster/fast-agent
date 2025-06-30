# Platform Agent 测试套件

本目录包含Platform Agent的完整测试套件。

## 目录结构

- `unit/` - 单元测试
- `integration/` - 集成测试  
- `memory/` - 内存系统专项测试
- `tools/` - 测试工具和实用程序
- `results/` - 测试结果和报告

## 运行测试

### 内存系统测试
```bash
# 基础内存功能测试
uv run test/memory/test_memory_basic.py

# CrewAI内存集成测试
uv run test/memory/test_crew_memory_simple.py

# Qwen API连通性测试
uv run test/memory/test_qwen_api.py
```

### 系统验证
```bash
# 系统设置验证
uv run test/tools/verify_setup.py

# 性能基准测试
uv run test/tools/benchmark_memory.py
```

### 测试报告

测试结果和报告保存在 `results/` 目录中。
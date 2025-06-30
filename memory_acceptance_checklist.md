# Platform Agent Memory功能验收清单

## 📋 验收概述

本清单用于验收Task 6: CrewAI智能记忆系统的完整功能。验收分为4个阶段，必须按顺序进行。

**验收原则**：
- ✅ 必须通过：核心功能，影响系统可用性
- ⚠️ 建议通过：增强功能，影响用户体验
- 📊 性能指标：量化标准，用于评估优化效果

---

## 🔧 阶段1: 环境和配置验收

### 1.1 依赖环境检查
- [ ] **Python版本**: 3.11+ ✅必须
- [ ] **虚拟环境**: `.venv`目录存在且可激活 ✅必须
- [ ] **ChromaDB**: `import chromadb`成功 ✅必须
- [ ] **SQLite**: `import sqlite3`成功 ✅必须

**验收方法**：
```bash
# 运行自动化检查
uv run test_memory_basic.py

# 或手动检查
python -c "import chromadb, sqlite3; print('Dependencies OK')"
```

### 1.2 配置文件验收
- [ ] **环境变量**: `.env`文件包含`CREWAI_STORAGE_DIR=./crew_memory` ✅必须
- [ ] **API配置**: 嵌入模型API密钥正确配置 ✅必须
- [ ] **权限检查**: 当前用户对项目目录有读写权限 ✅必须

**验收方法**：
```bash
# 检查配置
grep CREWAI_STORAGE_DIR .env
ls -la ./crew_memory  # 检查权限
```

---

## 🏗️ 阶段2: 基础功能验收

### 2.1 存储系统验收
- [ ] **目录创建**: 启动后自动创建`./crew_memory`目录 ✅必须
- [ ] **数据库文件**: 目录内包含`.db`或数据库相关文件 ✅必须
- [ ] **初始化成功**: 程序启动无memory相关错误日志 ✅必须

**验收方法**：
```bash
# 启动程序
./run.sh

# 检查目录和文件
ls -la ./crew_memory/
```

### 2.2 Crew集成验收
- [ ] **Memory启用**: Crew对象成功启用`memory=True`参数 ✅必须
- [ ] **Agent正常**: 所有Agent能正常初始化和运行 ✅必须
- [ ] **无冲突**: Memory功能与现有工具无冲突 ✅必须

**验收方法**：
```bash
# 运行基础功能测试
uv run test_memory_basic.py

# 观察启动日志中的memory相关信息
```

---

## 🧠 阶段3: 智能记忆功能验收

### 3.1 Short-term Memory验收
**测试场景**: 单次会话内的上下文记忆

- [ ] **第一轮查询**: 输入`"show me all k8s clusters"`
  - 预期：返回完整集群列表，有工具调用日志 ✅必须
  
- [ ] **第二轮查询**: 输入`"which cluster has the most pods?"`
  - 预期：基于第一轮结果回答，无重复工具调用 ✅必须
  
- [ ] **第三轮查询**: 输入`"what about the dev environment?"`
  - 预期：继续基于上下文回答，体现连续对话 ⚠️建议

**验收标准**：
- 第二轮查询响应时间 < 第一轮的50%
- Agent日志显示"从记忆中获取信息"相关提示

### 3.2 Long-term Memory验收
**测试场景**: 跨会话的持久化记忆

**会话1**:
- [ ] 输入：`"remember that prod-cluster-1 is our main production cluster"`
- [ ] 输入：`"show me details about the production environment"`
- [ ] 关闭程序

**会话2**（重启后）:
- [ ] 输入：`"tell me about the prod cluster I mentioned last time"`
- [ ] 预期：能回忆起prod-cluster-1的相关信息 ✅必须
- [ ] 输入：`"what clusters did we discuss before?"`
- [ ] 预期：能列出之前讨论过的集群 ⚠️建议

**验收标准**：
- 跨会话信息召回准确率 > 70%
- 能正确关联用户之前的关键信息

### 3.3 Entity Memory验收
**测试场景**: 实体识别和关联记忆

- [ ] **实体学习**: 输入多个包含具体集群名称的查询
- [ ] **实体识别**: Agent能识别并记住特定的K8s实体（集群、命名空间等）
- [ ] **实体关联**: 提到实体名称时，能自动关联相关信息 ⚠️建议

**测试用例**：
```
用户: "prod-cluster-1 has been having memory issues"
Agent: [记住 prod-cluster-1 + memory issues 关联]

用户: "how is prod-cluster-1 doing now?"
Agent: [能关联之前的memory issues信息]
```

---

## 📊 阶段4: 性能和稳定性验收

### 4.1 性能指标验收
- [ ] **响应时间优化**: 重复查询响应时间减少 ≥ 30% 📊性能
- [ ] **工具调用优化**: 重复场景工具调用减少 ≥ 50% 📊性能
- [ ] **内存使用**: 程序内存使用增长 < 100MB 📊性能

**验收方法**：
```bash
# 运行性能基准测试
uv run benchmark_memory.py

# 查看性能报告
cat memory_performance_report.txt
```

### 4.2 存储管理验收
- [ ] **存储增长**: 运行1小时后存储目录大小 < 50MB ⚠️建议
- [ ] **文件稳定**: 数据库文件无损坏，可正常读取 ✅必须
- [ ] **清理机制**: 提供清理过期记忆的方法 ⚠️建议

### 4.3 错误处理验收
- [ ] **存储异常**: 存储目录删除后能自动重建 ✅必须
- [ ] **API异常**: 嵌入模型API失败时程序不崩溃 ✅必须
- [ ] **内存异常**: Memory功能异常时能降级到无记忆模式 ⚠️建议

---

## 🎯 验收总结

### 必须通过的项目（影响发布）
- [ ] 存储系统正常创建和访问
- [ ] Short-term Memory基础功能正常
- [ ] Long-term Memory跨会话基本可用
- [ ] 程序稳定性无明显退化

### 建议通过的项目（影响体验）
- [ ] Entity Memory智能识别
- [ ] 复杂上下文理解
- [ ] 性能优化达到预期
- [ ] 存储管理和清理

### 性能基准线
- [ ] 响应时间优化 ≥ 30%
- [ ] 工具调用减少 ≥ 50%
- [ ] 跨会话召回率 ≥ 70%

---

## 📝 验收记录

**验收人员**: ________________  
**验收日期**: ________________  
**验收环境**: ________________  

**总体评价**:
- [ ] ✅ 通过验收，可以发布
- [ ] ⚠️ 部分通过，需要优化后发布
- [ ] ❌ 不通过验收，需要重新开发

**备注说明**:
```
[在此记录验收过程中发现的问题、建议和改进方向]
```

---

## 🛠️ 故障排查指南

### 常见问题和解决方案

**问题1: 存储目录创建失败**
```bash
# 检查权限
ls -la ./
chmod 755 .

# 手动创建
mkdir -p ./crew_memory
```

**问题2: ChromaDB初始化错误**
```bash
# 重新安装依赖
uv pip install --upgrade chromadb

# 清理缓存
rm -rf ./crew_memory
```

**问题3: API调用失败**
```bash
# 检查API配置
grep API_KEY .env

# 测试API连接
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     "https://api.openai.com/v1/models"
```

**问题4: 性能不达标**
```bash
# 调整memory配置
# 在crew.py中调整memory参数

# 监控资源使用
top -p $(pgrep -f "python.*main.py")
```
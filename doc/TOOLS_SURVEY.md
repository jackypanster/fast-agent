# Kubernetes MCP 工具集调研

## 1. 目的
本文档旨在调研并梳理 `kubernetes-mcp` 项目所提供的全部可用工具（Tools），为 Platform Agent 的 MVP 开发和未来迭代提供清晰的、有据可依的工具列表。

## 2. 核心发现
经过对 `kubernetes-mcp` 项目 `README.md` 的分析，得出一个关键结论：
- **`kubernetes-mcp` 是针对单一 Kubernetes 集群的**。它提供的工具是用来管理和查询**其自身连接的那个** K8s 集群。
- 项目中**没有**发现类似 `list_all_clusters`（列出所有集群）这样的跨集群管理工具。

这个发现修正了我们之前的一个假设。因此，对于 MVP 的核心场景"帮我查看一下k8s状态"，我们应该将其理解为"查看**当前**K8s集群的状态"，而不是管理多个集群。

## 3. 工具清单

`kubernetes-mcp` 提供的工具非常丰富，大致可分为以下几类：

### 3.1. 结构化高级工具 (Structured Tools)
这是最核心、最有价值的一组工具，封装了复杂的查询和操作。

| 工具名称 | 功能描述 |
| :--- | :--- |
| `GET_CLUSTER_INFO` | 获取集群的基本信息和版本详情。 |
| `GET_API_RESOURCES` | 列出集群中所有可用的 API 资源。 |
| `SEARCH_RESOURCES` | 跨命名空间和资源类型进行搜索。 |
| `EXPLAIN_RESOURCE` | 获取某个资源（如 Pod）的结构和字段定义，类似 `kubectl explain`。 |
| `APPLY_MANIFEST` | 应用 YAML 配置文件到集群中，类似 `kubectl apply`。 |
| `VALIDATE_MANIFEST` | 验证 YAML 文件的格式是否正确。 |
| `DIFF_MANIFEST` | 对比本地 YAML 与集群中已存在资源的差异。 |
| `GET_EVENTS` | 获取指定资源关联的事件（Events）。 |

### 3.2. 集群指标工具 (Cluster Metrics Tools)
用于获取集群的性能和资源使用情况。

| 工具名称 | 功能描述 |
| :--- | :--- |
| `GET_NODE_METRICS` | 获取节点的资源使用指标（CPU, 内存）。 |
| `GET_POD_METRICS` | 获取 Pod 的资源使用指标。 |
| `GET_RESOURCE_METRICS` | 获取集群整体的资源使用情况（CPU, 内存, 存储, Pod数量等）。 |
| `GET_TOP_CONSUMERS` | 找出资源消耗最高的 Pods。 |

### 3.3. 标准资源操作 (Standard Resource Operations)
这些是针对具体 K8s 资源对象的标准 CRUD（创建/读取/更新/删除）操作。对于每一个支持的资源类型（如 `Deployment`, `Pod`, `Service` 等），`kubernetes-mcp` 都会动态生成一套工具。

**支持的 API Groups**:
- `core/v1` (Pods, Nodes, Namespaces, Services, etc.)
- `apps/v1` (Deployments, ReplicaSets, StatefulSets, etc.)
- `batch/v1` (Jobs, CronJobs)
- `networking.k8s.io/v1` (Ingress, NetworkPolicy)
- 等等...

**为每个资源生成的标准工具 (以 Pod 为例)**:
- `list_pods`
- `get_pod`
- `describe_pod`
- `create_pod`
- `update_pod`
- `delete_pod`
- `get_pod_logs` (特殊)

## 4. MVP 实施建议
根据以上调研结果，针对 MVP 场景"帮我查看一下k8s状态"，我建议：
- **放弃**之前设想的 `list_clusters` 模拟工具。
- **改为模拟 `GET_CLUSTER_INFO` 工具**。这个工具的意图与用户指令高度匹配，是执行该任务的最优选择。

我们将以此为基础，更新我们的技术架构设计，并开展后续的编码工作。

## 5. 架构演进与实际集成
在项目后续的开发中，我们成功演进到了一个多 Agent 架构。
- **K8s Expert Agent**: 使用了本地的、模拟的 `get_cluster_info` 工具，其数据结构参考了真实的 K8s API 对象。
- **Web Researcher Agent**: 为了验证框架对远程工具的集成能力，我们成功地使用 `MCPServerAdapter` 集成了另一个公开的、用于网页抓取的 MCP 服务。

这次成功的远程 MCP 集成为我们未来替换掉本地模拟工具、转而接入真实的 `kubernetes-mcp` 服务，奠定了坚实的技术基础。 
"""
Platform Agent 本地工具集
提供模拟的K8s集群信息
"""

def get_cluster_info():
    """
    获取模拟的K8s集群信息
    """
    cluster_data = {
        "cluster_name": "demo-cluster",
        "cluster_version": "v1.28.3",
        "nodes": [
            {
                "name": "master-node-1",
                "status": "Ready", 
                "role": "control-plane",
                "cpu": "4 cores",
                "memory": "8Gi"
            },
            {
                "name": "worker-node-1", 
                "status": "Ready",
                "role": "worker",
                "cpu": "8 cores", 
                "memory": "16Gi"
            },
            {
                "name": "worker-node-2",
                "status": "Ready", 
                "role": "worker",
                "cpu": "8 cores",
                "memory": "16Gi"
            }
        ],
        "namespaces": ["default", "kube-system", "production", "staging"],
        "pods": {
            "total": 45,
            "running": 42,
            "pending": 2,
            "failed": 1
        },
        "services": 12,
        "deployments": 8
    }
    
    return f"""
# K8s 集群状态报告

**集群名称**: {cluster_data['cluster_name']}
**集群版本**: {cluster_data['cluster_version']}

## 节点状态
"""+ "\n".join([f"- {node['name']} ({node['role']}): {node['status']} - {node['cpu']}, {node['memory']}" 
                 for node in cluster_data['nodes']]) + f"""

## 资源概览
- **命名空间**: {len(cluster_data['namespaces'])} 个
- **Pod**: {cluster_data['pods']['total']} 个 (运行中: {cluster_data['pods']['running']}, 等待中: {cluster_data['pods']['pending']}, 失败: {cluster_data['pods']['failed']})
- **服务**: {cluster_data['services']} 个
- **部署**: {cluster_data['deployments']} 个

## 命名空间列表
{', '.join(cluster_data['namespaces'])}
"""


if __name__ == "__main__":
    print("=== Platform Agent 工具测试 ===")
    print(get_cluster_info())
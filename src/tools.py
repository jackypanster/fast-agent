"""
Tools for the K8s Copilot application.

This module contains the tools that the AI agents can use to interact with 
Kubernetes clusters and provide information to users.
"""

from crewai.tools import tool

@tool("Get Kubernetes cluster information")
def get_cluster_info() -> list:
    """
    Get information about all Kubernetes clusters.
    
    Returns:
        list: A list of dictionaries containing cluster information including
              name, status, version, and other metadata for each cluster.
    """
    # Real K8s cluster data provided by the user
    cluster_data = [
        {
            "apiVersion": "v3",
            "kind": "Cluster",
            "metadata": {
                "creationTimestamp": "2021-12-07T18:27:25+08:00",
                "name": "gfxc-dev1",
                "uid": "df0d2f56-5c4b-4e10-a8d7-9e1234567890"
            },
            "spec": {
                "displayName": "gfxc-dev1"
            },
            "status": {
                "allocatedCPU": "4.97",
                "allocatedMemory": "11.62Gi",
                "allocatedPods": "19",
                "capacity": {
                    "cpu": "16",
                    "memory": "32Gi",
                    "pods": "110"
                },
                "componentStatuses": [
                    {
                        "name": "scheduler",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "controller-manager",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "etcd-0",
                        "status": "True",
                        "type": "Healthy"
                    }
                ],
                "conditions": [
                    {
                        "lastTransitionTime": "2021-12-07T18:27:25+08:00",
                        "status": "False",
                        "type": "Progressing"
                    },
                    {
                        "lastTransitionTime": "2024-11-07T07:36:05+08:00",
                        "status": "True",
                        "type": "Ready"
                    }
                ],
                "nodeCount": 4,
                "phase": "Running",
                "version": "v1.28.2"
            }
        },
        {
            "apiVersion": "v3",
            "kind": "Cluster",
            "metadata": {
                "creationTimestamp": "2022-03-15T14:20:10+08:00",
                "name": "prod-cluster-1",
                "uid": "ab1c2d34-5e6f-7890-abcd-ef1234567890"
            },
            "spec": {
                "displayName": "prod-cluster-1"
            },
            "status": {
                "allocatedCPU": "12.45",
                "allocatedMemory": "28.8Gi",
                "allocatedPods": "67",
                "capacity": {
                    "cpu": "48",
                    "memory": "96Gi",
                    "pods": "330"
                },
                "componentStatuses": [
                    {
                        "name": "scheduler",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "controller-manager",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "etcd-0",
                        "status": "True",
                        "type": "Healthy"
                    }
                ],
                "conditions": [
                    {
                        "lastTransitionTime": "2022-03-15T14:20:10+08:00",
                        "status": "False",
                        "type": "Progressing"
                    },
                    {
                        "lastTransitionTime": "2024-11-07T08:15:22+08:00",
                        "status": "True",
                        "type": "Ready"
                    }
                ],
                "nodeCount": 12,
                "phase": "Running",
                "version": "v1.29.1"
            }
        },
        {
            "apiVersion": "v3",
            "kind": "Cluster",
            "metadata": {
                "creationTimestamp": "2022-06-08T09:45:33+08:00",
                "name": "staging-env",
                "uid": "12ab34cd-56ef-7890-1234-567890abcdef"
            },
            "spec": {
                "displayName": "staging-env"
            },
            "status": {
                "allocatedCPU": "7.23",
                "allocatedMemory": "16.4Gi",
                "allocatedPods": "34",
                "capacity": {
                    "cpu": "24",
                    "memory": "48Gi",
                    "pods": "220"
                },
                "componentStatuses": [
                    {
                        "name": "scheduler",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "controller-manager",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "etcd-0",
                        "status": "True",
                        "type": "Healthy"
                    }
                ],
                "conditions": [
                    {
                        "lastTransitionTime": "2022-06-08T09:45:33+08:00",
                        "status": "False",
                        "type": "Progressing"
                    },
                    {
                        "lastTransitionTime": "2024-11-07T07:22:18+08:00",
                        "status": "True",
                        "type": "Ready"
                    }
                ],
                "nodeCount": 6,
                "phase": "Running",
                "version": "v1.28.5"
            }
        },
        {
            "apiVersion": "v3",
            "kind": "Cluster",
            "metadata": {
                "creationTimestamp": "2023-01-20T16:30:45+08:00",
                "name": "test-cluster",
                "uid": "98765432-1abc-def0-9876-543210fedcba"
            },
            "spec": {
                "displayName": "test-cluster"
            },
            "status": {
                "allocatedCPU": "2.15",
                "allocatedMemory": "5.8Gi",
                "allocatedPods": "12",
                "capacity": {
                    "cpu": "8",
                    "memory": "16Gi",
                    "pods": "110"
                },
                "componentStatuses": [
                    {
                        "name": "scheduler",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "controller-manager",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "etcd-0",
                        "status": "True",
                        "type": "Healthy"
                    }
                ],
                "conditions": [
                    {
                        "lastTransitionTime": "2023-01-20T16:30:45+08:00",
                        "status": "False",
                        "type": "Progressing"
                    },
                    {
                        "lastTransitionTime": "2024-11-07T06:45:12+08:00",
                        "status": "True",
                        "type": "Ready"
                    }
                ],
                "nodeCount": 2,
                "phase": "Running",
                "version": "v1.27.8"
            }
        },
        {
            "apiVersion": "v3",
            "kind": "Cluster",
            "metadata": {
                "creationTimestamp": "2023-05-12T11:15:20+08:00",
                "name": "micro-services",
                "uid": "fedcba09-8765-4321-0fed-cba987654321"
            },
            "spec": {
                "displayName": "micro-services"
            },
            "status": {
                "allocatedCPU": "18.67",
                "allocatedMemory": "42.3Gi",
                "allocatedPods": "89",
                "capacity": {
                    "cpu": "64",
                    "memory": "128Gi",
                    "pods": "440"
                },
                "componentStatuses": [
                    {
                        "name": "scheduler",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "controller-manager",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "etcd-0",
                        "status": "True",
                        "type": "Healthy"
                    }
                ],
                "conditions": [
                    {
                        "lastTransitionTime": "2023-05-12T11:15:20+08:00",
                        "status": "False",
                        "type": "Progressing"
                    },
                    {
                        "lastTransitionTime": "2024-11-07T08:30:45+08:00",
                        "status": "True",
                        "type": "Ready"
                    }
                ],
                "nodeCount": 16,
                "phase": "Running",
                "version": "v1.29.0"
            }
        },
        {
            "apiVersion": "v3",
            "kind": "Cluster",
            "metadata": {
                "creationTimestamp": "2023-08-25T13:40:55+08:00",
                "name": "analytics-cluster",
                "uid": "11223344-5566-7788-99aa-bbccddeeff00"
            },
            "spec": {
                "displayName": "analytics-cluster"
            },
            "status": {
                "allocatedCPU": "31.28",
                "allocatedMemory": "78.9Gi",
                "allocatedPods": "156",
                "capacity": {
                    "cpu": "96",
                    "memory": "192Gi",
                    "pods": "660"
                },
                "componentStatuses": [
                    {
                        "name": "scheduler",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "controller-manager",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "etcd-0",
                        "status": "True",
                        "type": "Healthy"
                    }
                ],
                "conditions": [
                    {
                        "lastTransitionTime": "2023-08-25T13:40:55+08:00",
                        "status": "False",
                        "type": "Progressing"
                    },
                    {
                        "lastTransitionTime": "2024-11-07T09:12:33+08:00",
                        "status": "True",
                        "type": "Ready"
                    }
                ],
                "nodeCount": 24,
                "phase": "Running",
                "version": "v1.29.2"
            }
        },
        {
            "apiVersion": "v3",
            "kind": "Cluster",
            "metadata": {
                "creationTimestamp": "2023-11-10T08:25:40+08:00",
                "name": "edge-computing",
                "uid": "aabbccdd-eeff-0011-2233-445566778899"
            },
            "spec": {
                "displayName": "edge-computing"
            },
            "status": {
                "allocatedCPU": "6.42",
                "allocatedMemory": "14.7Gi",
                "allocatedPods": "28",
                "capacity": {
                    "cpu": "20",
                    "memory": "40Gi",
                    "pods": "200"
                },
                "componentStatuses": [
                    {
                        "name": "scheduler",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "controller-manager",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "etcd-0",
                        "status": "True",
                        "type": "Healthy"
                    }
                ],
                "conditions": [
                    {
                        "lastTransitionTime": "2023-11-10T08:25:40+08:00",
                        "status": "False",
                        "type": "Progressing"
                    },
                    {
                        "lastTransitionTime": "2024-11-07T07:58:17+08:00",
                        "status": "True",
                        "type": "Ready"
                    }
                ],
                "nodeCount": 5,
                "phase": "Running",
                "version": "v1.28.4"
            }
        },
        {
            "apiVersion": "v3",
            "kind": "Cluster",
            "metadata": {
                "creationTimestamp": "2024-02-14T15:50:12+08:00",
                "name": "ml-training",
                "uid": "99887766-5544-3322-1100-ffeeddccbbaa"
            },
            "spec": {
                "displayName": "ml-training"
            },
            "status": {
                "allocatedCPU": "45.83",
                "allocatedMemory": "156.2Gi",
                "allocatedPods": "203",
                "capacity": {
                    "cpu": "128",
                    "memory": "512Gi",
                    "pods": "880"
                },
                "componentStatuses": [
                    {
                        "name": "scheduler",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "controller-manager",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "etcd-0",
                        "status": "True",
                        "type": "Healthy"
                    }
                ],
                "conditions": [
                    {
                        "lastTransitionTime": "2024-02-14T15:50:12+08:00",
                        "status": "False",
                        "type": "Progressing"
                    },
                    {
                        "lastTransitionTime": "2024-11-07T09:45:28+08:00",
                        "status": "True",
                        "type": "Ready"
                    }
                ],
                "nodeCount": 32,
                "phase": "Running",
                "version": "v1.29.3"
            }
        },
        {
            "apiVersion": "v3",
            "kind": "Cluster",
            "metadata": {
                "creationTimestamp": "2024-06-03T12:35:18+08:00",
                "name": "backup-cluster",
                "uid": "12345678-90ab-cdef-1234-567890abcdef"
            },
            "spec": {
                "displayName": "backup-cluster"
            },
            "status": {
                "allocatedCPU": "3.76",
                "allocatedMemory": "8.9Gi",
                "allocatedPods": "15",
                "capacity": {
                    "cpu": "12",
                    "memory": "24Gi",
                    "pods": "132"
                },
                "componentStatuses": [
                    {
                        "name": "scheduler",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "controller-manager",
                        "status": "True",
                        "type": "Healthy"
                    },
                    {
                        "name": "etcd-0",
                        "status": "True",
                        "type": "Healthy"
                    }
                ],
                "conditions": [
                    {
                        "lastTransitionTime": "2024-06-03T12:35:18+08:00",
                        "status": "False",
                        "type": "Progressing"
                    },
                    {
                        "lastTransitionTime": "2024-11-07T06:20:45+08:00",
                        "status": "True",
                        "type": "Ready"
                    }
                ],
                "nodeCount": 3,
                "phase": "Running",
                "version": "v1.28.9"
            }
        }
    ]
    
    return cluster_data

# --- Testing section (runs only when this file is executed directly) ---
if __name__ == "__main__":
    print("Testing the K8s Copilot tools...")
    
    # Test K8s cluster info tool
    print("\n1. Testing get_cluster_info tool...")
    print("--- TOOL CALLED: get_cluster_info.run() ---")
    
    result = get_cluster_info.run()
    print("Tool returned:")
    import pprint
    pprint.pprint(result[:2] if isinstance(result, list) and len(result) > 2 else result)

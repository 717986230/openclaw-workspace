"""
企业级部署配置
支持 Docker、Kubernetes、CI/CD
"""

import yaml
import json
from typing import Dict, List, Optional
from pathlib import Path


class EnterpriseDeployment:
    """企业级部署配置"""
    
    def __init__(self, config_path: str):
        """初始化部署配置"""
        self.config_path = Path(config_path)
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """加载配置"""
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)
    
    def generate_docker_compose(self) -> str:
        """生成 Docker Compose 配置"""
        docker_compose = {
            "version": "3.8",
            "services": {
                "app": {
                    "build": ".",
                    "ports": ["8000:8000"],
                    "environment": self.config.get("environment", {}),
                    "volumes": [
                        "./data:/app/data",
                        "./logs:/app/logs"
                    ],
                    "depends_on": [
                        "postgres",
                        "redis",
                        "lancedb"
                    ],
                    "restart": "unless-stopped",
                    "deploy": {
                        "resources": {
                            "limits": {
                                "cpus": "4.0",
                                "memory": "8G"
                            },
                            "reservations": {
                                "cpus": "2.0",
                                "memory": "4G"
                            }
                        }
                    }
                },
                "postgres": {
                    "image": "postgres:15",
                    "environment": {
                        "POSTGRES_DB": self.config.get("postgres", {}).get("database", "erbing"),
                        "POSTGRES_USER": self.config.get("postgres", {}).get("user", "erbing"),
                        "POSTGRES_PASSWORD": self.config.get("postgres", {}).get("password", "password")
                    },
                    "volumes": [
                        "postgres_data:/var/lib/postgresql/data"
                    ],
                    "ports": ["5432:5432"],
                    "restart": "unless-stopped",
                    "deploy": {
                        "resources": {
                            "limits": {
                                "cpus": "2.0",
                                "memory": "4G"
                            }
                        }
                    }
                },
                "redis": {
                    "image": "redis:7",
                    "ports": ["6379:6379"],
                    "volumes": [
                        "redis_data:/data"
                    ],
                    "restart": "unless-stopped",
                    "deploy": {
                        "resources": {
                            "limits": {
                                "cpus": "1.0",
                                "memory": "2G"
                            }
                        }
                    }
                },
                "lancedb": {
                    "image": "lancedb/lancedb:latest",
                    "ports": ["8080:8080"],
                    "volumes": [
                        "lancedb_data:/data"
                    ],
                    "restart": "unless-stopped",
                    "deploy": {
                        "resources": {
                            "limits": {
                                "cpus": "2.0",
                                "memory": "4G"
                            }
                        }
                    }
                },
                "nginx": {
                    "image": "nginx:alpine",
                    "ports": ["80:80", "443:443"],
                    "volumes": [
                        "./nginx.conf:/etc/nginx/nginx.conf:ro",
                        "./ssl:/etc/nginx/ssl:ro"
                    ],
                    "depends_on": [
                        "app"
                    ],
                    "restart": "unless-stopped"
                },
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "ports": ["9090:9090"],
                    "volumes": [
                        "./prometheus.yml:/etc/prometheus/prometheus.yml:ro",
                        "prometheus_data:/prometheus"
                    ],
                    "restart": "unless-stopped"
                },
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "ports": ["3000:3000"],
                    "volumes": [
                        "grafana_data:/var/lib/grafana"
                    ],
                    "restart": "unless-stopped"
                }
            },
            "volumes": {
                "postgres_data": {},
                "redis_data": {},
                "lancedb_data": {},
                "prometheus_data": {},
                "grafana_data": {}
            }
        }
        
        return yaml.dump(docker_compose, default_flow_style=False)
    
    def generate_kubernetes_manifests(self) -> Dict[str, str]:
        """生成 Kubernetes 清单"""
        manifests = {}
        
        # Deployment
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "erbing",
                "namespace": self.config.get("namespace", "default")
            },
            "spec": {
                "replicas": self.config.get("replicas", 3),
                "selector": {
                    "matchLabels": {
                        "app": "erbing"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "erbing"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "erbing",
                                "image": self.config.get("image", "erbing:latest"),
                                "ports": [
                                    {
                                        "containerPort": 8000
                                    }
                                ],
                                "env": [
                                    {
                                        "name": key,
                                        "value": str(value)
                                    }
                                    for key, value in self.config.get("environment", {}).items()
                                ],
                                "resources": {
                                    "requests": {
                                        "cpu": "2",
                                        "memory": "4Gi"
                                    },
                                    "limits": {
                                        "cpu": "4",
                                        "memory": "8Gi"
                                    }
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": 8000
                                    },
                                    "initialDelaySeconds": 10,
                                    "periodSeconds": 5
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        manifests["deployment.yaml"] = yaml.dump(deployment)
        
        # Service
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "erbing",
                "namespace": self.config.get("namespace", "default")
            },
            "spec": {
                "selector": {
                    "app": "erbing"
                },
                "ports": [
                    {
                        "port": 80,
                        "targetPort": 8000
                    }
                ],
                "type": "LoadBalancer"
            }
        }
        
        manifests["service.yaml"] = yaml.dump(service)
        
        # ConfigMap
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "erbing-config",
                "namespace": self.config.get("namespace", "default")
            },
            "data": self.config.get("config_data", {})
        }
        
        manifests["configmap.yaml"] = yaml.dump(configmap)
        
        # Secret
        secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "erbing-secret",
                "namespace": self.config.get("namespace", "default")
            },
            "type": "Opaque",
            "data": {
                key: value.encode("base64")
                for key, value in self.config.get("secrets", {}).items()
            }
        }
        
        manifests["secret.yaml"] = yaml.dump(secret)
        
        # HorizontalPodAutoscaler
        hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": "erbing-hpa",
                "namespace": self.config.get("namespace", "default")
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": "erbing"
                },
                "minReplicas": self.config.get("min_replicas", 2),
                "maxReplicas": self.config.get("max_replicas", 10),
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 70
                            }
                        }
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": 80
                            }
                        }
                    }
                ]
            }
        }
        
        manifests["hpa.yaml"] = yaml.dump(hpa)
        
        return manifests
    
    def generate_ci_cd_pipeline(self) -> str:
        """生成 CI/CD 管道配置"""
        pipeline = {
            "name": "Erbing CI/CD Pipeline",
            "on": {
                "push": {
                    "branches": ["main", "develop"]
                },
                "pull_request": {
                    "branches": ["main"]
                }
            },
            "jobs": {
                "test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v3"
                        },
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {
                                "python-version": "3.11"
                            }
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt"
                        },
                        {
                            "name": "Run tests",
                            "run": "pytest tests/"
                        },
                        {
                            "name": "Run linting",
                            "run": "flake8 ."
                        }
                    ]
                },
                "build": {
                    "runs-on": "ubuntu-latest",
                    "needs": ["test"],
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v3"
                        },
                        {
                            "name": "Build Docker image",
                            "run": "docker build -t erbing:latest ."
                        },
                        {
                            "name": "Push to registry",
                            "run": "docker push erbing:latest"
                        }
                    ]
                },
                "deploy": {
                    "runs-on": "ubuntu-latest",
                    "needs": ["build"],
                    "if": "github.ref == 'refs/heads/main'",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v3"
                        },
                        {
                            "name": "Deploy to Kubernetes",
                            "run": "kubectl apply -f k8s/"
                        }
                    ]
                }
            }
        }
        
        return yaml.dump(pipeline)
    
    def generate_nginx_config(self) -> str:
        """生成 Nginx 配置"""
        config = f"""
events {{
    worker_connections 1024;
}}

http {{
    upstream erbing {{
        least_conn;
        server app:8000;
    }}
    
    server {{
        listen 80;
        server_name {self.config.get('domain', 'localhost')};
        
        location / {{
            proxy_pass http://erbing;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
        
        location /health {{
            proxy_pass http://erbing/health;
            access_log off;
        }}
        
        location /metrics {{
            proxy_pass http://erbing/metrics;
            access_log off;
        }}
    }}
}}
"""
        return config
    
    def generate_prometheus_config(self) -> str:
        """生成 Prometheus 配置"""
        config = {
            "global": {
                "scrape_interval": "15s"
            },
            "scrape_configs": [
                {
                    "job_name": "erbing",
                    "static_configs": [
                        {
                            "targets": ["app:8000"]
                        }
                    ]
                }
            ]
        }
        
        return yaml.dump(config)
    
    def save_all_configs(self, output_dir: str):
        """保存所有配置"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Docker Compose
        with open(output_path / "docker-compose.yml", "w") as f:
            f.write(self.generate_docker_compose())
        
        # Kubernetes manifests
        k8s_path = output_path / "k8s"
        k8s_path.mkdir(exist_ok=True)
        
        for name, content in self.generate_kubernetes_manifests().items():
            with open(k8s_path / name, "w") as f:
                f.write(content)
        
        # CI/CD pipeline
        with open(output_path / ".github" / "workflows" / "ci-cd.yml", "w") as f:
            f.write(self.generate_ci_cd_pipeline())
        
        # Nginx config
        with open(output_path / "nginx.conf", "w") as f:
            f.write(self.generate_nginx_config())
        
        # Prometheus config
        with open(output_path / "prometheus.yml", "w") as f:
            f.write(self.generate_prometheus_config())


# 使用示例
if __name__ == "__main__":
    # 配置
    config = {
        "namespace": "erbing",
        "replicas": 3,
        "min_replicas": 2,
        "max_replicas": 10,
        "image": "erbing:latest",
        "domain": "erbing.example.com",
        "environment": {
            "DATABASE_URL": "postgresql://erbing:password@postgres:5432/erbing",
            "REDIS_URL": "redis://redis:6379",
            "LANCEDB_URL": "http://lancedb:8080"
        },
        "secrets": {
            "DATABASE_PASSWORD": "password",
            "API_KEY": "secret_key"
        },
        "postgres": {
            "database": "erbing",
            "user": "erbing",
            "password": "password"
        }
    }
    
    # 保存配置
    deployment = EnterpriseDeployment(config)
    deployment.save_all_configs("./deployment")
    
    print("Deployment configs generated successfully!")

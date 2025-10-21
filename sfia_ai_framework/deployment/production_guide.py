"""
Production Deployment Guide for IntelliSFIA Framework

This guide provides comprehensive instructions for deploying the IntelliSFIA Framework
in production environments with multiple LLM providers and high availability.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List


class ProductionDeploymentGuide:
    """Production deployment configuration and setup guide"""
    
    @staticmethod
    def create_docker_compose():
        """Create Docker Compose configuration for production deployment"""
        docker_compose = {
            "version": "3.8",
            "services": {
                "neo4j": {
                    "image": "neo4j:5.15-enterprise",
                    "environment": {
                        "NEO4J_AUTH": "${NEO4J_USER}/${NEO4J_PASSWORD}",
                        "NEO4J_PLUGINS": '["apoc", "graph-data-science"]',
                        "NEO4J_dbms_security_procedures_unrestricted": "gds.*,apoc.*",
                        "NEO4J_dbms_memory_heap_initial__size": "2G",
                        "NEO4J_dbms_memory_heap_max__size": "4G",
                        "NEO4J_dbms_memory_pagecache_size": "2G"
                    },
                    "ports": ["7474:7474", "7687:7687"],
                    "volumes": [
                        "neo4j_data:/data",
                        "neo4j_logs:/logs",
                        "neo4j_import:/var/lib/neo4j/import",
                        "neo4j_plugins:/plugins"
                    ],
                    "restart": "unless-stopped",
                    "healthcheck": {
                        "test": ["CMD", "cypher-shell", "-u", "${NEO4J_USER}", "-p", "${NEO4J_PASSWORD}", "RETURN 1"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 5
                    }
                },
                "ollama": {
                    "image": "ollama/ollama:latest",
                    "ports": ["11434:11434"],
                    "volumes": ["ollama_data:/root/.ollama"],
                    "environment": {
                        "OLLAMA_MODELS": "/root/.ollama/models"
                    },
                    "restart": "unless-stopped",
                    "deploy": {
                        "resources": {
                            "reservations": {
                                "devices": [
                                    {
                                        "driver": "nvidia",
                                        "count": 1,
                                        "capabilities": ["gpu"]
                                    }
                                ]
                            }
                        }
                    }
                },
                "sfia-api": {
                    "build": {
                        "context": ".",
                        "dockerfile": "Dockerfile.api"
                    },
                    "ports": ["8000:8000"],
                    "environment": {
                        "NEO4J_URI": "bolt://neo4j:7687",
                        "NEO4J_USER": "${NEO4J_USER}",
                        "NEO4J_PASSWORD": "${NEO4J_PASSWORD}",
                        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
                        "AZURE_OPENAI_API_KEY": "${AZURE_OPENAI_API_KEY}",
                        "AZURE_OPENAI_ENDPOINT": "${AZURE_OPENAI_ENDPOINT}",
                        "HUGGINGFACE_API_KEY": "${HUGGINGFACE_API_KEY}",
                        "OLLAMA_BASE_URL": "http://ollama:11434"
                    },
                    "depends_on": {
                        "neo4j": {"condition": "service_healthy"},
                        "ollama": {"condition": "service_started"}
                    },
                    "restart": "unless-stopped",
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                },
                "sfia-web": {
                    "build": {
                        "context": ".",
                        "dockerfile": "Dockerfile.web"
                    },
                    "ports": ["8501:8501"],
                    "environment": {
                        "SFIA_API_URL": "http://sfia-api:8000"
                    },
                    "depends_on": ["sfia-api"],
                    "restart": "unless-stopped"
                },
                "nginx": {
                    "image": "nginx:alpine",
                    "ports": ["80:80", "443:443"],
                    "volumes": [
                        "./nginx.conf:/etc/nginx/nginx.conf",
                        "./ssl:/etc/nginx/ssl"
                    ],
                    "depends_on": ["sfia-api", "sfia-web"],
                    "restart": "unless-stopped"
                },
                "redis": {
                    "image": "redis:alpine",
                    "ports": ["6379:6379"],
                    "volumes": ["redis_data:/data"],
                    "restart": "unless-stopped",
                    "command": "redis-server --appendonly yes"
                }
            },
            "volumes": {
                "neo4j_data": None,
                "neo4j_logs": None,
                "neo4j_import": None,
                "neo4j_plugins": None,
                "ollama_data": None,
                "redis_data": None
            },
            "networks": {
                "sfia-network": {
                    "driver": "bridge"
                }
            }
        }
        
        return docker_compose
    
    @staticmethod
    def create_kubernetes_manifests():
        """Create Kubernetes manifests for production deployment"""
        manifests = {}
        
        # Namespace
        manifests["namespace.yaml"] = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "sfia-ai",
                "labels": {
                    "name": "sfia-ai"
                }
            }
        }
        
        # Neo4j StatefulSet
        manifests["neo4j.yaml"] = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": "neo4j",
                "namespace": "sfia-ai"
            },
            "spec": {
                "serviceName": "neo4j",
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "neo4j"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "neo4j"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "neo4j",
                                "image": "neo4j:5.15-enterprise",
                                "ports": [
                                    {"containerPort": 7474},
                                    {"containerPort": 7687}
                                ],
                                "env": [
                                    {
                                        "name": "NEO4J_AUTH",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": "neo4j-secrets",
                                                "key": "auth"
                                            }
                                        }
                                    }
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "neo4j-data",
                                        "mountPath": "/data"
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "memory": "2Gi",
                                        "cpu": "1"
                                    },
                                    "limits": {
                                        "memory": "4Gi",
                                        "cpu": "2"
                                    }
                                }
                            }
                        ]
                    }
                },
                "volumeClaimTemplates": [
                    {
                        "metadata": {
                            "name": "neo4j-data"
                        },
                        "spec": {
                            "accessModes": ["ReadWriteOnce"],
                            "resources": {
                                "requests": {
                                    "storage": "50Gi"
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        # SFIA API Deployment
        manifests["sfia-api.yaml"] = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "sfia-api",
                "namespace": "sfia-ai"
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "sfia-api"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "sfia-api"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "sfia-api",
                                "image": "sfia-ai/api:latest",
                                "ports": [
                                    {"containerPort": 8000}
                                ],
                                "env": [
                                    {
                                        "name": "NEO4J_URI",
                                        "value": "bolt://neo4j:7687"
                                    },
                                    {
                                        "name": "OPENAI_API_KEY",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": "llm-secrets",
                                                "key": "openai-api-key"
                                            }
                                        }
                                    }
                                ],
                                "resources": {
                                    "requests": {
                                        "memory": "1Gi",
                                        "cpu": "500m"
                                    },
                                    "limits": {
                                        "memory": "2Gi",
                                        "cpu": "1"
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
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        return manifests
    
    @staticmethod
    def create_monitoring_config():
        """Create monitoring configuration with Prometheus and Grafana"""
        monitoring_config = {
            "prometheus.yml": {
                "global": {
                    "scrape_interval": "15s",
                    "evaluation_interval": "15s"
                },
                "rule_files": [],
                "scrape_configs": [
                    {
                        "job_name": "prometheus",
                        "static_configs": [
                            {"targets": ["localhost:9090"]}
                        ]
                    },
                    {
                        "job_name": "neo4j",
                        "static_configs": [
                            {"targets": ["neo4j:2004"]}
                        ]
                    },
                    {
                        "job_name": "sfia-api",
                        "static_configs": [
                            {"targets": ["sfia-api:8000"]}
                        ],
                        "metrics_path": "/metrics"
                    }
                ]
            },
            "grafana-dashboard.json": {
                "dashboard": {
                    "title": "IntelliSFIA Framework Monitoring",
                    "panels": [
                        {
                            "title": "API Response Time",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
                                }
                            ]
                        },
                        {
                            "title": "Neo4j Transactions",
                            "type": "graph",
                            "targets": [
                                {
                                    "expr": "rate(neo4j_transaction_committed_total[5m])"
                                }
                            ]
                        },
                        {
                            "title": "LLM Provider Health",
                            "type": "stat",
                            "targets": [
                                {
                                    "expr": "llm_provider_health_status"
                                }
                            ]
                        }
                    ]
                }
            }
        }
        
        return monitoring_config
    
    @staticmethod
    def create_nginx_config():
        """Create Nginx configuration for load balancing and SSL"""
        nginx_config = """
        events {
            worker_connections 1024;
        }
        
        http {
            upstream sfia_api {
                server sfia-api:8000;
                # Add more servers for load balancing
                # server sfia-api-2:8000;
                # server sfia-api-3:8000;
            }
            
            upstream sfia_web {
                server sfia-web:8501;
            }
            
            # Rate limiting
            limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
            
            server {
                listen 80;
                server_name your-domain.com;
                
                # Redirect HTTP to HTTPS
                return 301 https://$server_name$request_uri;
            }
            
            server {
                listen 443 ssl http2;
                server_name your-domain.com;
                
                # SSL Configuration
                ssl_certificate /etc/nginx/ssl/cert.pem;
                ssl_certificate_key /etc/nginx/ssl/key.pem;
                ssl_protocols TLSv1.2 TLSv1.3;
                ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
                ssl_prefer_server_ciphers off;
                
                # API endpoints
                location /api/ {
                    limit_req zone=api burst=20 nodelay;
                    
                    proxy_pass http://sfia_api/;
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto $scheme;
                    
                    # CORS headers
                    add_header Access-Control-Allow-Origin *;
                    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
                    add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range";
                }
                
                # Web application
                location / {
                    proxy_pass http://sfia_web/;
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto $scheme;
                    
                    # WebSocket support for Streamlit
                    proxy_http_version 1.1;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection "upgrade";
                }
                
                # Health check endpoint
                location /health {
                    access_log off;
                    return 200 "healthy\\n";
                    add_header Content-Type text/plain;
                }
            }
        }
        """
        
        return nginx_config
    
    @staticmethod
    def create_environment_configs():
        """Create environment-specific configurations"""
        environments = {
            "development": {
                "framework": {
                    "neo4j_uri": "bolt://localhost:7687",
                    "neo4j_user": "neo4j",
                    "neo4j_password": "dev_password",
                    "debug": True,
                    "log_level": "DEBUG"
                },
                "llm": {
                    "default_provider": "ollama",
                    "providers": {
                        "ollama": {
                            "base_url": "http://localhost:11434",
                            "model": "llama2",
                            "temperature": 0.8
                        },
                        "openai": {
                            "api_key": "${OPENAI_API_KEY}",
                            "model": "gpt-3.5-turbo",
                            "temperature": 0.7
                        }
                    }
                }
            },
            "staging": {
                "framework": {
                    "neo4j_uri": "bolt://staging-neo4j:7687",
                    "neo4j_user": "neo4j",
                    "neo4j_password": "${NEO4J_STAGING_PASSWORD}",
                    "debug": False,
                    "log_level": "INFO"
                },
                "llm": {
                    "default_provider": "openai",
                    "providers": {
                        "openai": {
                            "api_key": "${OPENAI_API_KEY}",
                            "model": "gpt-4",
                            "temperature": 0.7
                        },
                        "anthropic": {
                            "api_key": "${ANTHROPIC_API_KEY}",
                            "model": "claude-3-sonnet-20240229",
                            "temperature": 0.7
                        }
                    }
                }
            },
            "production": {
                "framework": {
                    "neo4j_uri": "bolt+s://prod-neo4j:7687",
                    "neo4j_user": "neo4j",
                    "neo4j_password": "${NEO4J_PROD_PASSWORD}",
                    "debug": False,
                    "log_level": "WARNING",
                    "connection_pool_size": 50,
                    "request_timeout": 30
                },
                "llm": {
                    "default_provider": "openai",
                    "fallback_providers": ["anthropic", "azure_openai"],
                    "providers": {
                        "openai": {
                            "api_key": "${OPENAI_API_KEY}",
                            "model": "gpt-4",
                            "temperature": 0.7,
                            "max_retries": 3,
                            "timeout": 30
                        },
                        "anthropic": {
                            "api_key": "${ANTHROPIC_API_KEY}",
                            "model": "claude-3-sonnet-20240229",
                            "temperature": 0.7,
                            "max_retries": 3,
                            "timeout": 30
                        },
                        "azure_openai": {
                            "api_key": "${AZURE_OPENAI_API_KEY}",
                            "endpoint": "${AZURE_OPENAI_ENDPOINT}",
                            "model": "gpt-4",
                            "temperature": 0.7,
                            "max_retries": 3,
                            "timeout": 30
                        }
                    }
                },
                "security": {
                    "api_key_required": True,
                    "rate_limiting": {
                        "enabled": True,
                        "requests_per_minute": 100
                    },
                    "cors": {
                        "allowed_origins": ["https://your-domain.com"],
                        "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
                        "allowed_headers": ["*"]
                    }
                }
            }
        }
        
        return environments
    
    @staticmethod
    def create_deployment_scripts():
        """Create deployment and maintenance scripts"""
        scripts = {
            "deploy.sh": """#!/bin/bash
set -e

ENV=${1:-production}
echo "Deploying IntelliSFIA Framework to $ENV environment..."

# Load environment variables
source .env.$ENV

# Build Docker images
echo "Building Docker images..."
docker build -t sfia-ai/api:latest -f Dockerfile.api .
docker build -t sfia-ai/web:latest -f Dockerfile.web .

# Deploy with Docker Compose
echo "Starting services..."
docker-compose -f docker-compose.$ENV.yml up -d

# Wait for services to be healthy
echo "Waiting for services to be ready..."
./scripts/wait-for-services.sh

# Run database migrations
echo "Running Neo4j setup..."
./scripts/setup-neo4j.sh

# Load initial data
echo "Loading SFIA data..."
python -m sfia_ai_framework.cli load-data --file=data/sfia_skills.ttl

echo "Deployment completed successfully!"
            """,
            
            "backup.sh": """#!/bin/bash
set -e

BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "Creating backup in $BACKUP_DIR..."

# Backup Neo4j database
docker exec neo4j neo4j-admin database dump --to-path=/tmp neo4j
docker cp neo4j:/tmp/neo4j.dump $BACKUP_DIR/

# Backup configurations
cp -r configs/ $BACKUP_DIR/

# Backup application data
tar -czf $BACKUP_DIR/app_data.tar.gz data/

echo "Backup completed: $BACKUP_DIR"
            """,
            
            "restore.sh": """#!/bin/bash
set -e

BACKUP_DIR=$1
if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: $0 <backup_directory>"
    exit 1
fi

echo "Restoring from backup: $BACKUP_DIR"

# Stop services
docker-compose down

# Restore Neo4j database
docker cp $BACKUP_DIR/neo4j.dump neo4j:/tmp/
docker exec neo4j neo4j-admin database load --from-path=/tmp neo4j

# Restore configurations
cp -r $BACKUP_DIR/configs/* configs/

# Restore application data
tar -xzf $BACKUP_DIR/app_data.tar.gz -C .

# Start services
docker-compose up -d

echo "Restore completed successfully!"
            """,
            
            "health-check.sh": """#!/bin/bash

echo "IntelliSFIA Framework Health Check"
echo "=============================="

# Check Neo4j
echo -n "Neo4j: "
if curl -s http://localhost:7474/db/data/ > /dev/null; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

# Check API
echo -n "API: "
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

# Check Web App
echo -n "Web App: "
if curl -s http://localhost:8501 > /dev/null; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

# Check Ollama (if available)
echo -n "Ollama: "
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Healthy"
else
    echo "⚠️  Not available"
fi
            """
        }
        
        return scripts
    
    @staticmethod
    def generate_deployment_files():
        """Generate all deployment files"""
        guide = ProductionDeploymentGuide()
        
        # Create deployment directory
        deployment_dir = Path("deployment")
        deployment_dir.mkdir(exist_ok=True)
        
        # Docker Compose
        docker_compose = guide.create_docker_compose()
        with open(deployment_dir / "docker-compose.yml", "w") as f:
            yaml.dump(docker_compose, f, default_flow_style=False)
        
        # Kubernetes manifests
        k8s_dir = deployment_dir / "kubernetes"
        k8s_dir.mkdir(exist_ok=True)
        
        manifests = guide.create_kubernetes_manifests()
        for filename, manifest in manifests.items():
            with open(k8s_dir / filename, "w") as f:
                yaml.dump(manifest, f, default_flow_style=False)
        
        # Monitoring
        monitoring_dir = deployment_dir / "monitoring"
        monitoring_dir.mkdir(exist_ok=True)
        
        monitoring_config = guide.create_monitoring_config()
        for filename, config in monitoring_config.items():
            with open(monitoring_dir / filename, "w") as f:
                if filename.endswith(".json"):
                    import json
                    json.dump(config, f, indent=2)
                else:
                    yaml.dump(config, f, default_flow_style=False)
        
        # Nginx configuration
        nginx_config = guide.create_nginx_config()
        with open(deployment_dir / "nginx.conf", "w") as f:
            f.write(nginx_config)
        
        # Environment configurations
        configs_dir = deployment_dir / "configs"
        configs_dir.mkdir(exist_ok=True)
        
        environments = guide.create_environment_configs()
        for env_name, config in environments.items():
            with open(configs_dir / f"{env_name}.yaml", "w") as f:
                yaml.dump(config, f, default_flow_style=False)
        
        # Scripts
        scripts_dir = deployment_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        scripts = guide.create_deployment_scripts()
        for script_name, script_content in scripts.items():
            script_path = scripts_dir / script_name
            with open(script_path, "w") as f:
                f.write(script_content)
            
            # Make scripts executable
            os.chmod(script_path, 0o755)
        
        print(f"✅ Deployment files generated in: {deployment_dir}")
        print("\nGenerated files:")
        print("- docker-compose.yml")
        print("- kubernetes/ (manifests)")
        print("- monitoring/ (Prometheus, Grafana)")
        print("- nginx.conf")
        print("- configs/ (environment configs)")
        print("- scripts/ (deployment scripts)")


def create_production_dockerfile():
    """Create production-ready Dockerfiles"""
    
    # API Dockerfile
    api_dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY sfia_ai_framework/ ./sfia_ai_framework/
COPY data/ ./data/

# Create non-root user
RUN useradd --create-home --shell /bin/bash sfia
RUN chown -R sfia:sfia /app
USER sfia

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "sfia_ai_framework.web.api:app", "--host", "0.0.0.0", "--port", "8000"]
    """
    
    # Web Dockerfile
    web_dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt streamlit

# Copy application code
COPY sfia_ai_framework/ ./sfia_ai_framework/

# Create non-root user
RUN useradd --create-home --shell /bin/bash sfia
RUN chown -R sfia:sfia /app
USER sfia

EXPOSE 8501

CMD ["streamlit", "run", "sfia_ai_framework/web/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
    """
    
    with open("Dockerfile.api", "w") as f:
        f.write(api_dockerfile)
    
    with open("Dockerfile.web", "w") as f:
        f.write(web_dockerfile)
    
    print("✅ Production Dockerfiles created")


if __name__ == "__main__":
    print("🚀 IntelliSFIA Framework - Production Deployment Setup")
    print("=" * 60)
    
    # Generate deployment files
    ProductionDeploymentGuide.generate_deployment_files()
    
    # Create Dockerfiles
    create_production_dockerfile()
    
    print("\n📋 Next Steps:")
    print("1. Review and customize configuration files in deployment/configs/")
    print("2. Set up environment variables (.env files)")
    print("3. Configure SSL certificates for production")
    print("4. Run: ./deployment/scripts/deploy.sh production")
    print("5. Set up monitoring and alerting")
    print("6. Configure backup schedules")
    
    print("\n🔧 Production Checklist:")
    print("□ SSL/TLS certificates configured")
    print("□ Environment variables secured")
    print("□ Database backups scheduled")
    print("□ Monitoring and alerting set up")
    print("□ Rate limiting configured")
    print("□ Log aggregation configured")
    print("□ Health checks verified")
    print("□ Security scanning completed")
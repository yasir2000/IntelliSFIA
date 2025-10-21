# IntelliSFIA Deployment Guide

This guide covers deployment options for the complete IntelliSFIA framework including backend API, frontend web application, and enterprise integration components.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Enterprise    │
│   React App     │◄──►│   FastAPI       │◄──►│   Systems       │
│   Port: 3000    │    │   Port: 8000    │    │   SAP, Power BI │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Server    │    │   Database      │    │   Message       │
│   Nginx/Apache  │    │   Neo4j         │    │   Queue         │
│   Port: 80/443  │    │   Port: 7687    │    │   Redis/Kafka   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🐳 Docker Deployment

### Complete Docker Compose Setup

Create `docker-compose.yml` in the project root:

```yaml
version: '3.8'

services:
  # Frontend - React Application
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_WS_URL=ws://localhost:8000/ws
    depends_on:
      - backend
    networks:
      - intellisfia-network

  # Backend - FastAPI Application
  backend:
    build:
      context: ./
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=intellisfia123
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - neo4j
      - redis
    volumes:
      - ./data:/app/data
    networks:
      - intellisfia-network

  # Neo4j Database
  neo4j:
    image: neo4j:5.15-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/intellisfia123
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    networks:
      - intellisfia-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - intellisfia-network

  # Nginx Load Balancer & Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - intellisfia-network

volumes:
  neo4j_data:
  neo4j_logs:
  redis_data:

networks:
  intellisfia-network:
    driver: bridge
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Backend Dockerfile

Create `Dockerfile.backend`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application code
COPY sfia_ai_framework/ ./sfia_ai_framework/
COPY sfia_rdf/ ./sfia_rdf/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "sfia_ai_framework.web.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # Frontend (React App)
    server {
        listen 80;
        server_name intellisfia.local;

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API requests
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://backend/health;
            proxy_set_header Host $host;
        }

        # WebSocket support
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS (Elastic Container Service)

1. **Build and push Docker images**:
```bash
# Build images
docker build -t intellisfia-frontend ./frontend
docker build -t intellisfia-backend -f Dockerfile.backend .

# Tag for ECR
docker tag intellisfia-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/intellisfia-frontend:latest
docker tag intellisfia-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/intellisfia-backend:latest

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/intellisfia-frontend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/intellisfia-backend:latest
```

2. **ECS Task Definition** (`task-definition.json`):
```json
{
  "family": "intellisfia-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/intellisfia-frontend:latest",
      "portMappings": [{"containerPort": 80, "protocol": "tcp"}],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/intellisfia",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    },
    {
      "name": "backend",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/intellisfia-backend:latest",
      "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
      "essential": true,
      "environment": [
        {"name": "NEO4J_URI", "value": "bolt://neo4j.cluster.local:7687"},
        {"name": "REDIS_URL", "value": "redis://redis.cluster.local:6379"}
      ],
      "secrets": [
        {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:ssm:REGION:ACCOUNT:parameter/intellisfia/openai-key"}
      ]
    }
  ]
}
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name intellisfia-rg --location eastus

# Create container group
az container create \
  --resource-group intellisfia-rg \
  --name intellisfia-app \
  --image intellisfia-frontend:latest \
  --cpu 1 --memory 2 \
  --ports 80 8000 \
  --environment-variables \
    REACT_APP_API_URL=http://intellisfia-backend:8000 \
  --dns-name-label intellisfia-demo
```

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/intellisfia-frontend ./frontend
gcloud builds submit --tag gcr.io/PROJECT-ID/intellisfia-backend -f Dockerfile.backend .

# Deploy frontend
gcloud run deploy intellisfia-frontend \
  --image gcr.io/PROJECT-ID/intellisfia-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy backend
gcloud run deploy intellisfia-backend \
  --image gcr.io/PROJECT-ID/intellisfia-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NEO4J_URI=bolt://neo4j-instance:7687
```

## 🚀 Kubernetes Deployment

### Kubernetes Manifests

Create `k8s/` directory with the following files:

#### Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: intellisfia
```

#### Frontend Deployment
```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: intellisfia-frontend
  namespace: intellisfia
spec:
  replicas: 3
  selector:
    matchLabels:
      app: intellisfia-frontend
  template:
    metadata:
      labels:
        app: intellisfia-frontend
    spec:
      containers:
      - name: frontend
        image: intellisfia-frontend:latest
        ports:
        - containerPort: 80
        env:
        - name: REACT_APP_API_URL
          value: "http://intellisfia-backend:8000"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: intellisfia-frontend
  namespace: intellisfia
spec:
  selector:
    app: intellisfia-frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

#### Backend Deployment
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: intellisfia-backend
  namespace: intellisfia
spec:
  replicas: 2
  selector:
    matchLabels:
      app: intellisfia-backend
  template:
    metadata:
      labels:
        app: intellisfia-backend
    spec:
      containers:
      - name: backend
        image: intellisfia-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: NEO4J_URI
          value: "bolt://neo4j:7687"
        - name: REDIS_URL
          value: "redis://redis:6379"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: intellisfia-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: intellisfia-backend
  namespace: intellisfia
spec:
  selector:
    app: intellisfia-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

#### Ingress Configuration
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: intellisfia-ingress
  namespace: intellisfia
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/websocket-services: "intellisfia-backend"
spec:
  tls:
  - hosts:
    - intellisfia.yourdomain.com
    secretName: intellisfia-tls
  rules:
  - host: intellisfia.yourdomain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: intellisfia-backend
            port:
              number: 8000
      - path: /health
        pathType: Prefix
        backend:
          service:
            name: intellisfia-backend
            port:
              number: 8000
      - path: /ws
        pathType: Prefix
        backend:
          service:
            name: intellisfia-backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: intellisfia-frontend
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n intellisfia
kubectl get services -n intellisfia
kubectl get ingress -n intellisfia

# View logs
kubectl logs -f deployment/intellisfia-frontend -n intellisfia
kubectl logs -f deployment/intellisfia-backend -n intellisfia
```

## 🔧 Environment Configuration

### Production Environment Variables

Create `.env.production`:

```env
# API Configuration
REACT_APP_API_URL=https://api.intellisfia.com
REACT_APP_WS_URL=wss://api.intellisfia.com/ws
REACT_APP_VERSION=1.0.0

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_REAL_TIME=true
REACT_APP_ENABLE_DEBUG=false

# Third-party Services
REACT_APP_SENTRY_DSN=https://...
REACT_APP_ANALYTICS_ID=GA-...

# Security
REACT_APP_API_TIMEOUT=30000
REACT_APP_SESSION_TIMEOUT=3600
```

### Backend Configuration

```env
# Database
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=secure_password

# Cache
REDIS_URL=redis://redis:6379

# AI Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
AZURE_OPENAI_ENDPOINT=...

# Enterprise Integration
ENTERPRISE_REDIS_URL=redis://enterprise-redis:6379
MAX_CONCURRENT_CONNECTIONS=10
ANALYSIS_CONFIDENCE_THRESHOLD=0.7

# Security
JWT_SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_TIME=3600

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
SENTRY_DSN=https://...
```

## 📊 Monitoring & Observability

### Health Checks

The application includes comprehensive health checks:

- **Frontend**: `GET /` returns React app
- **Backend**: `GET /health` returns system status
- **Database**: Neo4j connection check
- **Cache**: Redis connection check
- **Enterprise**: Connected systems status

### Logging

Configure structured logging:

```yaml
# logging.yaml
version: 1
formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  json:
    format: '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: json
  file:
    class: logging.handlers.RotatingFileHandler
    filename: /app/logs/intellisfia.log
    maxBytes: 10485760
    backupCount: 5
    formatter: json
loggers:
  intellisfia:
    level: INFO
    handlers: [console, file]
    propagate: false
root:
  level: WARNING
  handlers: [console]
```

### Metrics Collection

Use Prometheus for metrics collection:

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'intellisfia-backend'
    static_configs:
      - targets: ['intellisfia-backend:8000']
    metrics_path: /metrics

  - job_name: 'intellisfia-frontend'
    static_configs:
      - targets: ['intellisfia-frontend:80']
    metrics_path: /metrics
```

## 🔐 Security Considerations

### SSL/TLS Configuration

Use Let's Encrypt for SSL certificates:

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Generate certificates
certbot --nginx -d intellisfia.yourdomain.com

# Auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### Security Headers

Configure security headers in Nginx:

```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Network Security

- Use private subnets for databases
- Configure security groups/firewall rules
- Enable VPC flow logs
- Use bastion hosts for SSH access

## 🚀 Performance Optimization

### Frontend Optimization

1. **Code Splitting**: Implemented with React.lazy()
2. **Bundle Analysis**: Use webpack-bundle-analyzer
3. **CDN**: Serve static assets from CDN
4. **Compression**: Enable gzip/brotli compression
5. **Caching**: Configure proper cache headers

### Backend Optimization

1. **Database Connection Pooling**: Configure Neo4j connection pools
2. **Redis Caching**: Cache frequently accessed data
3. **API Rate Limiting**: Implement rate limiting middleware
4. **Response Compression**: Enable response compression
5. **Async Processing**: Use background tasks for heavy operations

### Database Optimization

1. **Indexing**: Create appropriate Neo4j indexes
2. **Query Optimization**: Optimize Cypher queries
3. **Memory Configuration**: Tune Neo4j memory settings
4. **Backup Strategy**: Regular automated backups

## 📈 Scaling Strategy

### Horizontal Scaling

1. **Load Balancing**: Use Nginx/HAProxy for load balancing
2. **Auto Scaling**: Configure auto-scaling groups
3. **Database Clustering**: Neo4j cluster setup
4. **Microservices**: Split into smaller services as needed

### Vertical Scaling

1. **Resource Monitoring**: Monitor CPU/memory usage
2. **Performance Profiling**: Identify bottlenecks
3. **Capacity Planning**: Plan for growth
4. **Resource Allocation**: Optimize container resources

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy IntelliSFIA

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: cd frontend && npm ci
    
    - name: Run tests
      run: cd frontend && npm test -- --coverage --watchAll=false
    
    - name: Build frontend
      run: cd frontend && npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker images
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY_FRONTEND: intellisfia-frontend
        ECR_REPOSITORY_BACKEND: intellisfia-backend
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG ./frontend
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG -f Dockerfile.backend .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY_FRONTEND:$IMAGE_TAG
        docker push $ECR_REGISTRY/$ECR_REPOSITORY_BACKEND:$IMAGE_TAG
    
    - name: Deploy to ECS
      run: |
        # Update ECS service with new image
        aws ecs update-service --cluster intellisfia-cluster --service intellisfia-service --force-new-deployment
```

## 📞 Support & Troubleshooting

### Common Issues

1. **CORS Errors**: Configure CORS settings in backend
2. **Connection Refused**: Check service networking
3. **Memory Issues**: Monitor and adjust container resources
4. **SSL Certificate**: Verify certificate installation
5. **Database Connection**: Check Neo4j connection settings

### Debug Commands

```bash
# Check container logs
docker logs -f intellisfia-frontend
docker logs -f intellisfia-backend

# Test API connectivity
curl -f http://localhost:8000/health

# Check database connection
docker exec -it neo4j cypher-shell -u neo4j -p password

# Monitor resources
docker stats
kubectl top pods -n intellisfia
```

### Support Channels

- **Documentation**: Full deployment documentation
- **GitHub Issues**: Technical support and bug reports
- **Community Forum**: User discussions and help
- **Enterprise Support**: Premium support for enterprise customers

---

This deployment guide provides comprehensive instructions for deploying IntelliSFIA in various environments, from local development to enterprise-scale production deployments.
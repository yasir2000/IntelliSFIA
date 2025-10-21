# IntelliSFIA Production Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 16GB RAM and 4 CPU cores
- 100GB available disk space
- SSL certificates for production domain

### One-Command Deployment
```bash
# Clone the repository
git clone https://github.com/your-org/sfia-rdf.git
cd sfia-rdf

# Copy and configure environment variables
cp .env.example .env.prod
# Edit .env.prod with your production values

# Start the complete stack
docker-compose -f docker-compose.prod.yml up -d

# Initialize the database
docker-compose -f docker-compose.prod.yml exec postgres /docker-entrypoint-initdb.d/init-db.sh

# Import SFIA data
docker-compose -f docker-compose.prod.yml exec postgres /docker-entrypoint-initdb.d/import-sfia-data.sh
```

## 📋 Architecture Overview

IntelliSFIA production deployment consists of:

### **Core Application Services**
- **Frontend**: React 18.2.0 application with TypeScript
- **API Gateway**: FastAPI backend with authentication and rate limiting
- **SFIA Engine**: Core SFIA framework processing service
- **RDF Service**: Knowledge graph and semantic processing

### **Data Layer**
- **PostgreSQL 15**: Primary database with SFIA framework data
- **Redis 7**: Caching and session storage
- **GraphDB**: RDF triple store for knowledge graphs
- **MinIO**: Object storage for files and assets

### **Infrastructure Services**
- **Nginx**: Load balancer and reverse proxy
- **RabbitMQ**: Message queue for asynchronous processing
- **Elasticsearch**: Full-text search and logging
- **Logstash**: Log processing and aggregation
- **Kibana**: Log visualization and analysis

### **Monitoring Stack**
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Monitoring dashboards and visualization
- **Jaeger**: Distributed tracing
- **AlertManager**: Alert routing and notification
- **cAdvisor**: Container metrics collection

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# Database
POSTGRES_HOST=postgres
POSTGRES_DB=intellisfia_prod
POSTGRES_USER=intellisfia
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_HOST=redis
REDIS_PASSWORD=your_redis_password

# Security
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# SSL/TLS
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
```

### Database Configuration

The system automatically creates:
- **6 SFIA Categories**: Strategy, Change, Development, Delivery, Skills, Relationships
- **14 Subcategories**: Organized SFIA skill groupings
- **7 SFIA Levels**: From Follow (1) to Set Strategy (7)
- **16 Attributes**: Core SFIA attributes for skill assessment
- **20+ Sample Skills**: Including Programming, Project Management, Business Analysis

### Monitoring Configuration

Access monitoring services:
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601
- **Jaeger**: http://localhost:16686

## 🏗️ Deployment Options

### 1. Docker Compose (Recommended for Single Server)

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale api-gateway=3 --scale frontend=2
```

### 2. Kubernetes (Recommended for Multi-Server)

```bash
# Apply Kubernetes manifests
kubectl apply -f deployment/kubernetes/intellisfia-app.yaml

# Check deployment status
kubectl get pods -n intellisfia
kubectl get services -n intellisfia

# View logs
kubectl logs -f deployment/intellisfia-api-gateway -n intellisfia
```

### 3. Manual Installation

For custom deployments, see individual service documentation in `/deployment/docs/`.

## 🔐 Security Features

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- API rate limiting (10 requests/second per IP)
- CORS protection with configurable origins

### Data Protection
- TLS 1.2/1.3 encryption for all communications
- Database encryption at rest
- Secure password hashing (bcrypt)
- SQL injection prevention (parameterized queries)

### Infrastructure Security
- Container security scanning with Trivy
- Network segmentation with Docker networks
- Security headers (HSTS, CSP, X-Frame-Options)
- Regular security updates via automated builds

## 📊 Monitoring & Alerting

### Key Metrics Monitored
- **Application Performance**: Response times, error rates, throughput
- **System Resources**: CPU, memory, disk usage
- **Database Health**: Connection pools, query performance
- **User Activity**: Active sessions, assessment completions

### Alert Conditions
- Service downtime (> 1 minute)
- High error rate (> 10% for 2 minutes)
- Resource exhaustion (> 80% CPU/memory for 5 minutes)
- Failed authentication attempts (> 5/second for 2 minutes)

### Dashboards Available
- **Application Overview**: High-level service health
- **Infrastructure Monitoring**: System resources and container metrics
- **User Analytics**: Usage patterns and business metrics
- **Security Dashboard**: Authentication events and security alerts

## 🔄 CI/CD Pipeline

### Automated Testing
- **Frontend**: ESLint, TypeScript checking, unit tests
- **Backend**: Flake8, MyPy, pytest with coverage
- **Security**: Trivy vulnerability scanning, Semgrep SAST
- **Performance**: K6 load testing on staging

### Deployment Strategy
- **Staging**: Automatic deployment on `develop` branch
- **Production**: Manual approval required for `main` branch
- **Rollback**: Automated rollback on health check failures
- **Blue-Green**: Zero-downtime deployments with health checks

## 🛠️ Maintenance

### Regular Tasks
- **Database Backup**: Automated daily backups to MinIO
- **Log Rotation**: Automated log cleanup (30-day retention)
- **Security Updates**: Weekly automated dependency updates
- **Certificate Renewal**: Automated SSL certificate renewal

### Scaling Recommendations
- **Horizontal Scaling**: Add more API Gateway and Frontend instances
- **Database Scaling**: Use read replicas for heavy read workloads
- **Caching**: Implement Redis clustering for high availability
- **CDN**: Use CloudFlare or AWS CloudFront for static assets

## 🚨 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check service logs
docker-compose -f docker-compose.prod.yml logs service-name

# Common fixes
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose -f docker-compose.prod.yml exec postgres pg_isready

# Reset database (CAUTION: Data loss)
docker volume rm sfia-rdf_postgres_data
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Scale problematic services
docker-compose -f docker-compose.prod.yml up -d --scale api-gateway=5
```

### Health Check Endpoints
- **Frontend**: `GET /health`
- **API Gateway**: `GET /api/health`
- **SFIA Engine**: `GET /sfia/health`
- **RDF Service**: `GET /rdf/health`

## 📞 Support

### Documentation
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Architecture Diagrams**: `/deployment/docs/architecture/`
- **Runbooks**: `/deployment/docs/runbooks/`

### Monitoring Access
- **Grafana Dashboards**: http://localhost:3001
- **Log Analysis**: http://localhost:5601 (Kibana)
- **Distributed Tracing**: http://localhost:16686 (Jaeger)

### Getting Help
1. Check health endpoints for service status
2. Review logs in Kibana or via Docker Compose
3. Monitor alerts in Grafana
4. Contact support team with specific error messages

---

## 📈 Performance Characteristics

### Expected Performance (4 CPU / 16GB RAM)
- **Concurrent Users**: 1,000+ active sessions
- **API Response Time**: < 200ms (95th percentile)
- **Database Queries**: < 50ms average
- **Assessment Processing**: < 5 seconds per assessment

### Scaling Targets
- **Horizontal Scale**: 10,000+ concurrent users
- **Database**: 1M+ skills assessments
- **Storage**: 1TB+ knowledge base data
- **Availability**: 99.9% uptime target

This production deployment provides a robust, scalable, and secure platform for the IntelliSFIA SFIA framework application with comprehensive monitoring, automated operations, and enterprise-grade reliability.
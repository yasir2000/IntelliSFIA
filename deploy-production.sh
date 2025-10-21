#!/bin/bash
# Production Deployment Script for IntelliSFIA with Ollama
# ========================================================

set -e

echo "🚀 IntelliSFIA Production Deployment with Ollama"
echo "================================================="

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod-ollama.yml down 2>/dev/null || true

# Remove old images (optional)
read -p "🗑️  Remove old Docker images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing old images..."
    docker system prune -f
    docker volume prune -f
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.prod-ollama.yml up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check Ollama
if curl -sf http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama service is healthy"
else
    echo "❌ Ollama service is not responding"
fi

# Check API
if curl -sf http://localhost:8000/health > /dev/null; then
    echo "✅ API service is healthy"
else
    echo "❌ API service is not responding"
fi

# Check Frontend
if curl -sf http://localhost:3000 > /dev/null; then
    echo "✅ Frontend service is healthy"
else
    echo "❌ Frontend service is not responding"
fi

# Check PostgreSQL
if docker exec intellisfia-postgres pg_isready -U intellisfia > /dev/null; then
    echo "✅ PostgreSQL is healthy"
else
    echo "❌ PostgreSQL is not responding"
fi

# Show service status
echo ""
echo "📊 Service Status:"
echo "=================="
docker-compose -f docker-compose.prod-ollama.yml ps

echo ""
echo "🌐 Access Points:"
echo "================="
echo "• Frontend:      http://localhost:3000"
echo "• API:           http://localhost:8000"
echo "• API Docs:      http://localhost:8000/docs"
echo "• Ollama API:    http://localhost:11434"
echo "• Nginx Proxy:   http://localhost:80"

echo ""
echo "🔧 Management Commands:"
echo "======================"
echo "• View logs:       docker-compose -f docker-compose.prod-ollama.yml logs -f"
echo "• Stop services:   docker-compose -f docker-compose.prod-ollama.yml down"
echo "• Restart:         docker-compose -f docker-compose.prod-ollama.yml restart"
echo "• Shell access:    docker exec -it intellisfia-api bash"

echo ""
echo "🧪 Quick Tests:"
echo "==============="
echo "• Test API:        curl http://localhost:8000/health"
echo "• Test Ollama:     curl http://localhost:11434/api/tags"
echo "• Test Frontend:   curl http://localhost:3000"

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "💡 Note: Model downloads may take some time on first run."
echo "   Check progress with: docker logs intellisfia-model-init"
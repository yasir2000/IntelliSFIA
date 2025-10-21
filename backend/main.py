"""
IntelliSFIA Production API Server
FastAPI-based backend with enterprise features
"""

from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import redis
import asyncpg
from pydantic import BaseModel
import jwt
from contextlib import asynccontextmanager
import aiohttp
from prometheus_client import Counter, Histogram, generate_latest
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Metrics
REQUEST_COUNT = Counter('intellisfia_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('intellisfia_request_duration_seconds', 'Request duration')

# Configuration
class Settings:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.redis_url = os.getenv('REDIS_URL')
        self.jwt_secret = os.getenv('JWT_SECRET')
        self.oauth_client_id = os.getenv('OAUTH_CLIENT_ID')
        self.oauth_client_secret = os.getenv('OAUTH_CLIENT_SECRET')
        self.cors_origins = os.getenv('CORS_ORIGINS', '').split(',')
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.rate_limit_requests = int(os.getenv('RATE_LIMIT_REQUESTS_PER_MINUTE', '100'))

settings = Settings()

# Database connection pool
class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(settings.database_url)
        logger.info("Connected to PostgreSQL database")
    
    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            logger.info("Disconnected from PostgreSQL database")

# Redis connection
class Cache:
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url)
    
    async def get(self, key: str) -> Optional[str]:
        return self.redis.get(key)
    
    async def set(self, key: str, value: str, expiry: int = 3600):
        return self.redis.setex(key, expiry, value)
    
    async def delete(self, key: str):
        return self.redis.delete(key)

# Global instances
db = Database()
cache = Cache()

# Pydantic models
class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    roles: List[str]
    organization: Optional[str] = None

class SkillAssessment(BaseModel):
    skill_code: str
    current_level: int
    target_level: int
    evidence: List[str]
    assessment_date: datetime

class AssessmentRequest(BaseModel):
    user_id: str
    skills: List[str]
    evidence: Dict[str, List[str]]

class AssessmentResponse(BaseModel):
    assessment_id: str
    user_id: str
    results: Dict[str, Any]
    recommendations: List[str]
    completion_date: datetime

# Authentication
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> UserProfile:
    """Validate JWT token and return user profile"""
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        async with db.pool.acquire() as conn:
            user_data = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            if not user_data:
                raise HTTPException(status_code=401, detail="User not found")
        
        return UserProfile(
            id=user_data['id'],
            email=user_data['email'],
            name=user_data['name'],
            roles=user_data['roles'],
            organization=user_data['organization']
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Middleware for request tracking
async def track_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(process_time)
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    logger.info("IntelliSFIA API Server started")
    yield
    # Shutdown
    await db.disconnect()
    logger.info("IntelliSFIA API Server stopped")

# FastAPI application
app = FastAPI(
    title="IntelliSFIA Enterprise API",
    description="Production-ready SFIA framework API with enterprise features",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.middleware("http")(track_requests)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    try:
        # Check database connectivity
        async with db.pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        # Check Redis connectivity
        cache.redis.ping()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {
                "database": "healthy",
                "cache": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# Authentication endpoints
@app.post("/auth/login")
async def login(credentials: dict):
    """OAuth2/OIDC login endpoint"""
    # Implementation for OAuth2 flow
    # This would integrate with your identity provider
    pass

@app.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh JWT token"""
    # Implementation for token refresh
    pass

# SFIA Skills endpoints
@app.get("/api/v1/skills")
async def get_skills(
    category: Optional[str] = None,
    level: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: UserProfile = Depends(get_current_user)
):
    """Get SFIA skills with filtering and pagination"""
    try:
        # Check cache first
        cache_key = f"skills:{category}:{level}:{search}:{limit}:{offset}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return JSONResponse(content=eval(cached_result))
        
        # Build query
        query = "SELECT * FROM sfia_skills WHERE 1=1"
        params = []
        param_count = 0
        
        if category:
            param_count += 1
            query += f" AND category = ${param_count}"
            params.append(category)
        
        if level:
            param_count += 1
            query += f" AND ${param_count} = ANY(available_levels)"
            params.append(level)
        
        if search:
            param_count += 1
            query += f" AND (name ILIKE ${param_count} OR description ILIKE ${param_count})"
            params.append(f"%{search}%")
        
        query += f" ORDER BY code LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([limit, offset])
        
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            
            skills = [dict(row) for row in rows]
            
            # Cache result
            result = {
                "success": True,
                "data": {
                    "skills": skills,
                    "total": len(skills),
                    "limit": limit,
                    "offset": offset
                }
            }
            
            await cache.set(cache_key, str(result), 1800)  # 30 minutes
            
            return result
    
    except Exception as e:
        logger.error(f"Error fetching skills: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/skills/{skill_code}")
async def get_skill(
    skill_code: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Get detailed information about a specific skill"""
    try:
        cache_key = f"skill:{skill_code}"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return JSONResponse(content=eval(cached_result))
        
        async with db.pool.acquire() as conn:
            skill = await conn.fetchrow(
                "SELECT * FROM sfia_skills WHERE code = $1", 
                skill_code
            )
            
            if not skill:
                raise HTTPException(status_code=404, detail="Skill not found")
            
            result = {
                "success": True,
                "data": {
                    "skill": dict(skill)
                }
            }
            
            await cache.set(cache_key, str(result), 3600)  # 1 hour
            
            return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching skill {skill_code}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Assessment endpoints
@app.post("/api/v1/assessments", response_model=AssessmentResponse)
async def create_assessment(
    assessment_request: AssessmentRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """Create a new skills assessment"""
    try:
        # Validate user permissions
        if assessment_request.user_id != current_user.id and "admin" not in current_user.roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Process assessment using SFIA engine
        # This would integrate with the SFIA processing service
        assessment_id = f"assess_{int(time.time())}"
        
        # Store assessment in database
        async with db.pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO assessments (id, user_id, skills, evidence, status, created_at)
                   VALUES ($1, $2, $3, $4, $5, $6)""",
                assessment_id,
                assessment_request.user_id,
                assessment_request.skills,
                assessment_request.evidence,
                "processing",
                datetime.utcnow()
            )
        
        # Mock response - in production, this would be processed asynchronously
        return AssessmentResponse(
            assessment_id=assessment_id,
            user_id=assessment_request.user_id,
            results={"status": "processing"},
            recommendations=["Assessment is being processed"],
            completion_date=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating assessment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/assessments/{assessment_id}")
async def get_assessment(
    assessment_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Get assessment results"""
    try:
        async with db.pool.acquire() as conn:
            assessment = await conn.fetchrow(
                "SELECT * FROM assessments WHERE id = $1",
                assessment_id
            )
            
            if not assessment:
                raise HTTPException(status_code=404, detail="Assessment not found")
            
            # Check permissions
            if assessment['user_id'] != current_user.id and "admin" not in current_user.roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return {
                "success": True,
                "data": {
                    "assessment": dict(assessment)
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assessment {assessment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Statistics endpoint
@app.get("/api/v1/statistics")
async def get_statistics(current_user: UserProfile = Depends(get_current_user)):
    """Get SFIA framework statistics"""
    try:
        cache_key = "statistics"
        cached_result = await cache.get(cache_key)
        if cached_result:
            return JSONResponse(content=eval(cached_result))
        
        async with db.pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_skills,
                    COUNT(DISTINCT category) as total_categories,
                    COUNT(DISTINCT subcategory) as total_subcategories,
                    MAX(array_length(available_levels, 1)) as max_levels
                FROM sfia_skills
            """)
            
            result = {
                "success": True,
                "data": {
                    "statistics": {
                        "sfia_version": "SFIA 9",
                        "total_skills": stats['total_skills'],
                        "total_categories": stats['total_categories'],
                        "total_subcategories": stats['total_subcategories'],
                        "level_definitions": stats['max_levels'],
                        "data_loaded": True,
                        "last_updated": datetime.utcnow().isoformat()
                    }
                }
            }
            
            await cache.set(cache_key, str(result), 3600)  # 1 hour
            
            return result
    
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=int(os.getenv('API_WORKERS', '4')),
        log_level="info",
        access_log=True
    )
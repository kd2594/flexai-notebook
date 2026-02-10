# Integration Guide: FlexAI GPU Selector → Production (console.flex.ai)

## 📋 Overview

This guide covers integrating the GPU selector widget with your production FlexAI platform at **console.flex.ai**.

## 🔧 Backend Integration

### 1. Update FlexAI Client for Production API

Update `backend/flexai_client.py` to use real FlexAI API endpoints:

```python
# Replace the mock endpoints with production endpoints
class FlexAIClient:
    def __init__(self, api_key: str, api_url: str, org_id: str):
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')  # https://api.flex.ai
        self.org_id = org_id
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Organization-ID": org_id
        }
    
    async def get_available_gpus(self) -> List[GPUType]:
        """Get list of available GPU types from production API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/v1/compute/gpu-types",  # Real FlexAI endpoint
                headers=self.headers,
                timeout=10.0
            )
            response.raise_for_status()
            return [GPUType(**gpu) for gpu in response.json()]
    
    async def provision_instance(self, gpu_type: str, gpu_count: int, user_id: str) -> ComputeInstance:
        """Provision real compute instance via FlexAI API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/v1/compute/instances",  # Real FlexAI endpoint
                headers=self.headers,
                json={
                    "gpu_type": gpu_type,
                    "gpu_count": gpu_count,
                    "user_id": user_id,
                    "instance_type": "jupyter"
                },
                timeout=30.0
            )
            response.raise_for_status()
            return ComputeInstance(**response.json())
```

### 2. Update Environment Configuration for Production

Create `.env.production`:

```bash
# ============================================================================
# FlexAI Platform Configuration - PRODUCTION
# ============================================================================

# Production FlexAI API Configuration
FLEXAI_API_KEY=<YOUR_REAL_FLEXAI_API_KEY>
FLEXAI_API_URL=https://api.flex.ai
FLEXAI_ORG_ID=<YOUR_ORG_ID>

# Backend API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Database Configuration (Production PostgreSQL)
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database>

# Redis Configuration (Production)
REDIS_URL=redis://<host>:6379

# Security - CHANGE THESE!
SECRET_KEY=<generate_secure_random_key_here>
JWT_SECRET_KEY=<generate_secure_random_jwt_key>

# CORS Configuration - Add your frontend URL
ALLOWED_ORIGINS=https://console.flex.ai,https://notebooks.flex.ai

# Logging
LOG_LEVEL=INFO

# Feature Flags
MOCK_MODE=false
ENABLE_METRICS=true
ENABLE_TELEMETRY=true

# Session Configuration
SESSION_TIMEOUT_MINUTES=120
MAX_CONCURRENT_SESSIONS=100
```

### 3. Add Authentication Middleware

Create `backend/auth.py`:

```python
"""
Authentication middleware for production
"""
from fastapi import HTTPException, Header, Depends
from typing import Optional
import jwt
import os

async def verify_user_token(
    authorization: Optional[str] = Header(None)
) -> dict:
    """Verify JWT token from console.flex.ai"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
        
        # Verify JWT token
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=["HS256"]
        )
        
        return {
            "user_id": payload.get("user_id"),
            "org_id": payload.get("org_id"),
            "email": payload.get("email")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
```

Update `backend/main.py` to use authentication:

```python
from auth import verify_user_token

@app.post("/api/compute/instances", response_model=SelectComputeResponse)
async def create_compute_instance(
    request: SelectComputeRequest,
    user: dict = Depends(verify_user_token)
):
    """Create compute instance - requires authentication"""
    try:
        # Use authenticated user info
        session = session_manager.create_session(user_id=user["user_id"])
        
        # Provision via real FlexAI API
        instance = await flexai_client.provision_instance(
            gpu_type=request.gpu_type,
            gpu_count=request.gpu_count,
            user_id=user["user_id"]
        )
        
        return SelectComputeResponse(...)
    except Exception as e:
        logger.error(f"Error provisioning: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

## 🎨 Frontend Integration

### 4. Update Widget for Production Backend

Update `frontend/flexai_gpu_selector_pro.py`:

```python
class FlexAIGPUSelector:
    def __init__(self, backend_url="https://api.flex.ai", auth_token=None):
        self.backend_url = backend_url
        self.auth_token = auth_token  # JWT token from console.flex.ai
    
    async def fetch_gpu_types(self) -> List[Dict]:
        """Fetch from production API"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.backend_url}/api/compute/available",
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
```

Update JavaScript in the widget:

```javascript
async function saveFlexAIGPU() {
    const statusDiv = document.getElementById('flexai-status');
    statusDiv.className = 'loading';
    statusDiv.innerHTML = '⏳ Provisioning ' + selectedFlexAIGPU + '...';
    
    try {
        // Get auth token from cookie or localStorage
        const authToken = getCookie('flexai_token') || localStorage.getItem('flexai_token');
        
        const response = await fetch('https://api.flex.ai/api/compute/instances', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`  // Add auth
            },
            body: JSON.stringify({
                gpu_type: selectedFlexAIGPU,
                gpu_count: 1
            })
        });
        
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        
        const result = await response.json();
        // Handle success...
    } catch (error) {
        // Handle error...
    }
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
```

### 5. Integrate with console.flex.ai Frontend

#### Option A: Embed Widget in React/Next.js

Create `components/GPUSelector.tsx`:

```typescript
import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';

export function GPUSelector() {
  const { token } = useAuth();
  const [gpuTypes, setGpuTypes] = useState([]);
  const [selectedGPU, setSelectedGPU] = useState('CPU');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchGPUTypes();
  }, []);

  const fetchGPUTypes = async () => {
    const response = await fetch('https://api.flex.ai/api/compute/available', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await response.json();
    setGpuTypes(data);
  };

  const provisionGPU = async () => {
    const response = await fetch('https://api.flex.ai/api/compute/instances', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        gpu_type: selectedGPU,
        gpu_count: 1
      })
    });
    
    if (response.ok) {
      // Success handling
      toast.success(`Successfully provisioned ${selectedGPU}!`);
      setIsOpen(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger>
        <Button>🚀 Change Runtime Type</Button>
      </DialogTrigger>
      <DialogContent>
        {/* Render GPU options */}
        {gpuTypes.map(gpu => (
          <GPUOption
            key={gpu.id}
            gpu={gpu}
            selected={selectedGPU === gpu.id}
            onSelect={() => setSelectedGPU(gpu.id)}
          />
        ))}
        <Button onClick={provisionGPU}>Save</Button>
      </DialogContent>
    </Dialog>
  );
}
```

#### Option B: Iframe Integration

Embed Jupyter with GPU selector:

```html
<!-- In console.flex.ai -->
<iframe 
  src="https://notebooks.flex.ai/lab?token=${userToken}"
  style="width: 100%; height: 100vh; border: none;"
  sandbox="allow-scripts allow-same-origin allow-forms"
></iframe>
```

### 6. API Gateway Configuration

Set up API routes in console.flex.ai:

```nginx
# nginx.conf for console.flex.ai

# Proxy to backend API
location /api/compute/ {
    proxy_pass http://backend-service:8000/api/compute/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Authorization $http_authorization;
}

# Proxy to Jupyter
location /notebooks/ {
    proxy_pass http://jupyter-service:8888/;
    proxy_set_header Host $host;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## 🚀 Deployment Steps

### 7. Docker Deployment

Create `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    environment:
      - MOCK_MODE=false
      - FLEXAI_API_KEY=${FLEXAI_API_KEY}
      - FLEXAI_API_URL=https://api.flex.ai
      - DATABASE_URL=${DATABASE_URL}
    ports:
      - "8000:8000"
    restart: always
    
  jupyter:
    build:
      context: .
      dockerfile: docker/Dockerfile.jupyter
    environment:
      - BACKEND_API_URL=https://api.flex.ai
      - JUPYTER_TOKEN=${JUPYTER_TOKEN}
    ports:
      - "8888:8888"
    volumes:
      - jupyter-data:/home/jovyan/work
    restart: always

volumes:
  jupyter-data:
```

Deploy:

```bash
# Build and push images
docker build -t console.flex.ai/backend:latest -f docker/Dockerfile.backend .
docker build -t console.flex.ai/jupyter:latest -f docker/Dockerfile.jupyter .

docker push console.flex.ai/backend:latest
docker push console.flex.ai/jupyter:latest

# Deploy with production config
docker-compose -f docker-compose.production.yml up -d
```

### 8. Kubernetes Deployment (Optional)

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flexai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flexai-backend
  template:
    metadata:
      labels:
        app: flexai-backend
    spec:
      containers:
      - name: backend
        image: console.flex.ai/backend:latest
        env:
        - name: MOCK_MODE
          value: "false"
        - name: FLEXAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: flexai-secrets
              key: api-key
        ports:
        - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: flexai-backend-service
spec:
  selector:
    app: flexai-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 🔒 Security Checklist

- [ ] Replace all mock API keys with real production keys
- [ ] Enable JWT authentication for all API endpoints
- [ ] Set up HTTPS/TLS certificates
- [ ] Configure CORS properly (whitelist console.flex.ai)
- [ ] Enable rate limiting
- [ ] Set up API key rotation
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Set up monitoring and alerts
- [ ] Implement user session management
- [ ] Add CSRF protection
- [ ] Validate all user inputs

## 📊 Monitoring & Logging

Add to `backend/main.py`:

```python
from prometheus_client import Counter, Histogram, generate_latest
import time

gpu_provision_counter = Counter(
    'flexai_gpu_provisions_total',
    'Total GPU provisioning requests',
    ['gpu_type', 'status']
)

gpu_provision_duration = Histogram(
    'flexai_gpu_provision_duration_seconds',
    'Time spent provisioning GPUs'
)

@app.post("/api/compute/instances")
async def create_instance(request: SelectComputeRequest):
    start_time = time.time()
    try:
        # Provision logic...
        gpu_provision_counter.labels(gpu_type=request.gpu_type, status='success').inc()
        return result
    except Exception as e:
        gpu_provision_counter.labels(gpu_type=request.gpu_type, status='error').inc()
        raise
    finally:
        duration = time.time() - start_time
        gpu_provision_duration.observe(duration)

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 🧪 Testing Production Integration

```python
# test_production_integration.py
import httpx
import pytest

@pytest.mark.asyncio
async def test_production_api():
    """Test connection to production FlexAI API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.flex.ai/api/compute/available",
            headers={"Authorization": f"Bearer {TEST_API_KEY}"}
        )
        assert response.status_code == 200
        gpus = response.json()
        assert len(gpus) > 0

@pytest.mark.asyncio
async def test_gpu_provisioning():
    """Test GPU provisioning in production"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.flex.ai/api/compute/instances",
            headers={"Authorization": f"Bearer {TEST_API_KEY}"},
            json={"gpu_type": "nvidia-t4", "gpu_count": 1}
        )
        assert response.status_code == 200
        instance = response.json()
        assert instance["status"] in ["pending", "running"]
```

## 📝 Configuration Summary

### Environment Variables to Update:

1. **.env.production**:
   - `MOCK_MODE=false`
   - `FLEXAI_API_KEY=<real_key>`
   - `FLEXAI_API_URL=https://api.flex.ai`
   - `FLEXAI_ORG_ID=<your_org_id>`

2. **Frontend URLs**:
   - Backend API: `https://api.flex.ai`
   - Jupyter: `https://notebooks.flex.ai`
   - Console: `https://console.flex.ai`

3. **CORS Origins**:
   - `https://console.flex.ai`
   - `https://notebooks.flex.ai`

## 🚦 Go-Live Checklist

- [ ] Update .env with production credentials
- [ ] Build Docker images with production config
- [ ] Deploy backend API to production
- [ ] Deploy Jupyter to production  
- [ ] Configure DNS records
- [ ] Set up SSL certificates
- [ ] Test GPU provisioning end-to-end
- [ ] Enable monitoring and logging
- [ ] Set up alerting
- [ ] Document API endpoints for frontend team
- [ ] Train support team on new features
- [ ] Create rollback plan

---

Need help with any specific integration step? Let me know!

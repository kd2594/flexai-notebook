"""
FastAPI Backend for FlexAI Notebook Platform
"""
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
from dotenv import load_dotenv

from flexai_client import FlexAIClient, GPUType, ComputeInstance
from session_manager import session_manager, Session

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FlexAI Notebook Platform API",
    description="Backend API for FlexAI-integrated Jupyter Notebook platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:8888").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize FlexAI client
# In mock mode, the client will use the local mock API server
MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"

if MOCK_MODE:
    logger.info("🎭 Running in MOCK MODE - Using local mock FlexAI API")
    logger.info(f"Mock API URL: {os.getenv('FLEXAI_API_URL', 'http://mock-flexai:9000')}")
else:
    logger.info("🚀 Running in PRODUCTION MODE - Using real FlexAI API")

flexai_client = FlexAIClient(
    api_key=os.getenv("FLEXAI_API_KEY", "mock_api_key"),
    api_url=os.getenv("FLEXAI_API_URL", "http://mock-flexai:9000"),
    org_id=os.getenv("FLEXAI_ORG_ID", "mock_org_id")
)


# ============================================================================
# Request/Response Models
# ============================================================================

class SelectComputeRequest(BaseModel):
    """Request to select compute configuration"""
    gpu_type: str
    gpu_count: int = 1
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class SelectComputeResponse(BaseModel):
    """Response after selecting compute"""
    session_id: str
    instance_id: str
    status: str
    message: str


class SessionResponse(BaseModel):
    """Session information response"""
    session_id: str
    user_id: Optional[str]
    instance_id: Optional[str]
    gpu_type: Optional[str]
    gpu_count: int
    status: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await session_manager.start()
    mode = "MOCK" if MOCK_MODE else "PRODUCTION"
    logger.info(f"🚀 FlexAI Notebook Platform API started in {mode} mode")
    logger.info(f"API URL: {os.getenv('FLEXAI_API_URL')}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await session_manager.stop()
    logger.info("FlexAI Notebook Platform API shut down")


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", version="1.0.0")


# ============================================================================
# Compute Endpoints
# ============================================================================

@app.get("/api/compute/available", response_model=List[GPUType])
async def get_available_gpus():
    """Get list of available GPU types from FlexAI"""
    try:
        gpu_types = await flexai_client.get_available_gpus()
        return gpu_types
    except Exception as e:
        logger.error(f"Error fetching available GPUs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/compute/gpu-types")
async def get_gpu_types():
    """Get list of available GPU types (alternative endpoint for extension)"""
    try:
        gpu_types = await flexai_client.get_available_gpus()
        return gpu_types
    except Exception as e:
        logger.error(f"Error fetching GPU types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compute/instances")
async def create_compute_instance(request: SelectComputeRequest):
    """Create a new compute instance (alternative endpoint for extension)"""
    return await select_compute(request)


@app.get("/api/compute/instances")
async def list_compute_instances():
    """List all active compute instances"""
    try:
        instances = []
        for session_id in session_manager.sessions:
            session = session_manager.get_session(session_id)
            if session and session.instance_id:
                instances.append({
                    "id": session.instance_id,
                    "session_id": session.session_id,
                    "gpu_type": session.gpu_type,
                    "status": session.status
                })
        return instances
    except Exception as e:
        logger.error(f"Error listing instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compute/select", response_model=SelectComputeResponse)
async def select_compute(request: SelectComputeRequest):
    """Select GPU/CPU configuration and provision instance"""
    try:
        # Get or create session
        if request.session_id:
            session = session_manager.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = session_manager.create_session(user_id=request.user_id)
        
        # Update session status
        session_manager.update_session(
            session.session_id,
            status="provisioning",
            gpu_type=request.gpu_type,
            gpu_count=request.gpu_count
        )
        
        # Provision compute instance via FlexAI
        logger.info(f"Provisioning {request.gpu_type} x{request.gpu_count} for session {session.session_id}")
        instance = await flexai_client.provision_instance(
            gpu_type=request.gpu_type,
            gpu_count=request.gpu_count,
            user_id=session.user_id
        )
        
        # Update session with instance details
        session_manager.update_session(
            session.session_id,
            instance_id=instance.instance_id,
            status="active"
        )
        
        logger.info(f"Instance {instance.instance_id} provisioned for session {session.session_id}")
        
        return SelectComputeResponse(
            session_id=session.session_id,
            instance_id=instance.instance_id,
            status="active",
            message=f"Successfully provisioned {request.gpu_type} x{request.gpu_count}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting compute: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/compute/instance/{instance_id}", response_model=ComputeInstance)
async def get_instance_status(instance_id: str):
    """Get status of a compute instance"""
    try:
        instance = await flexai_client.get_instance_status(instance_id)
        return instance
    except Exception as e:
        logger.error(f"Error getting instance status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compute/instance/{instance_id}/stop")
async def stop_instance(instance_id: str):
    """Stop a compute instance"""
    try:
        success = await flexai_client.stop_instance(instance_id)
        if success:
            return {"message": "Instance stopped successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stop instance")
    except Exception as e:
        logger.error(f"Error stopping instance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Session Endpoints
# ============================================================================

@app.post("/api/sessions/create", response_model=SessionResponse)
async def create_session(user_id: Optional[str] = None):
    """Create a new session"""
    try:
        session = session_manager.create_session(user_id=user_id)
        return SessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            instance_id=session.instance_id,
            gpu_type=session.gpu_type,
            gpu_count=session.gpu_count,
            status=session.status
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        instance_id=session.instance_id,
        gpu_type=session.gpu_type,
        gpu_count=session.gpu_count,
        status=session.status
    )


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and associated resources"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Stop/delete instance if exists
        if session.instance_id:
            await flexai_client.delete_instance(session.instance_id)
        
        # Delete session
        session_manager.delete_session(session_id)
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sessions/{session_id}/extend")
async def extend_session(session_id: str, hours: int = 1):
    """Extend session expiration"""
    session = session_manager.extend_session(session_id, hours=hours)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": f"Session extended by {hours} hours"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

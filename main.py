"""
💳 Project Raseed - FastAPI Main Application
AI-Powered Receipt & Spending Companion

This FastAPI application provides REST API endpoints for the Project Raseed workflow.
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Import Project Raseed components
from src.main_orchestrator import MainOrchestrator
from src.utils.helpers import load_env_config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="💳 Project Raseed - AI-Powered Receipt & Spending Companion",
    description="AI-driven personal finance assistant that automatically extracts, categorizes, and analyzes receipt data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = None

# Pydantic models
class WorkflowRequest(BaseModel):
    session_id: Optional[str] = None
    days_back: int = 7

class ReceiptRequest(BaseModel):
    merchant: str
    amount: float
    currency: str = "USD"
    category: Optional[str] = None
    items: List[str] = []
    date: str
    source: str = "Manual"

class SingleReceiptRequest(BaseModel):
    receipt: ReceiptRequest

@app.on_event("startup")
async def startup_event():
    """Initialize the Project Raseed orchestrator on startup"""
    global orchestrator
    
    try:
        # Load configuration
        config = load_env_config()
        
        # Check required API keys
        required_keys = ["COMPOSIO_API_KEY", "GEMINI_API_KEY"]
        missing_keys = [key for key in required_keys if not config.get(key)]
        
        if missing_keys:
            logger.warning(f"Missing required API keys: {missing_keys}")
            logger.warning("Some features may not work properly")
        
        # Initialize orchestrator
        orchestrator = MainOrchestrator()
        logger.info("✅ Project Raseed orchestrator initialized")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize orchestrator: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "💳 Project Raseed - AI-Powered Receipt & Spending Companion",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global orchestrator
    
    health_status = {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "orchestrator_initialized": orchestrator is not None
    }
    
    if orchestrator:
        try:
            agent_status = await orchestrator.get_workflow_status()
            health_status["agents"] = agent_status.get("agents_status", {})
        except Exception as e:
            health_status["status"] = "degraded"
            health_status["error"] = str(e)
    
    return health_status

@app.post("/workflow/start")
async def start_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Start the complete Project Raseed workflow"""
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        logger.info(f"🚀 Starting workflow with session_id: {request.session_id}")
        
        # Start workflow in background
        results = await orchestrator.start_workflow(request.session_id)
        
        return {
            "status": "success",
            "message": "Workflow completed successfully",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Workflow failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")

@app.post("/workflow/status")
async def get_workflow_status():
    """Get current workflow status"""
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        status = await orchestrator.get_workflow_status()
        return {
            "status": "success",
            "workflow_status": status
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@app.post("/receipt/process")
async def process_single_receipt(request: SingleReceiptRequest):
    """Process a single receipt through the complete pipeline"""
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        # Convert to receipt data format
        receipt_data = {
            "merchant": request.receipt.merchant,
            "amount": request.receipt.amount,
            "currency": request.receipt.currency,
            "category": request.receipt.category,
            "items": request.receipt.items,
            "date": request.receipt.date,
            "source": request.receipt.source,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        logger.info(f"🧾 Processing receipt: {request.receipt.merchant}")
        
        # Process the receipt
        results = await orchestrator.process_single_receipt(receipt_data)
        
        return {
            "status": "success",
            "message": "Receipt processed successfully",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Receipt processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Receipt processing failed: {str(e)}")

@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        workflow_status = await orchestrator.get_workflow_status()
        agents_status = workflow_status.get("agents_status", {})
        
        return {
            "status": "success",
            "agents": agents_status
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get agents status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agents status: {str(e)}")

@app.get("/config")
async def get_configuration():
    """Get current configuration (without sensitive data)"""
    config = load_env_config()
    
    # Remove sensitive information
    safe_config = {
        "user_id": config.get("USER_ID"),
        "slack_channel": config.get("SLACK_CHANNEL"),
        "receipt_days_back": config.get("RECEIPT_DAYS_BACK", "7"),
        "notification_enabled": config.get("NOTIFICATION_ENABLED", "true"),
        "api_keys_configured": {
            "composio": bool(config.get("COMPOSIO_API_KEY")),
            "gemini": bool(config.get("GEMINI_API_KEY")),
            "openai": bool(config.get("OPENAI_API_KEY"))
        }
    }
    
    return {
        "status": "success",
        "configuration": safe_config
    }

@app.get("/demo")
async def demo_endpoint():
    """Demo endpoint to test the system"""
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        # Create a sample receipt for demo
        sample_receipt = {
            "merchant": "Demo Store",
            "amount": 25.99,
            "currency": "USD",
            "category": "Shopping",
            "items": ["Demo Item 1", "Demo Item 2"],
            "date": "2024-01-15",
            "source": "Demo",
            "timestamp": "2024-01-15T12:00:00Z"
        }
        
        # Process the demo receipt
        results = await orchestrator.process_single_receipt(sample_receipt)
        
        return {
            "status": "success",
            "message": "Demo completed successfully",
            "demo_results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo failed: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"❌ Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG") == "True" else "An error occurred"
        }
    )

if __name__ == "__main__":
    # Get configuration
    config = load_env_config()
    
    # Server settings
    host = config.get("HOST", "0.0.0.0")
    port = int(config.get("PORT", 8000))
    debug = config.get("DEBUG", "True").lower() == "true"
    
    print("💳 Project Raseed - AI-Powered Receipt & Spending Companion")
    print("=" * 60)
    print(f"🚀 Starting server on {host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    print("=" * 60)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

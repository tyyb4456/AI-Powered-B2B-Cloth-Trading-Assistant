from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Import your updated workflow routes
from api.workflow_routes import router as workflow_router

app = FastAPI(
    title="B2B Textile Procurement Assistant",
    description="LangGraph-powered procurement & negotiation backend with GET endpoints",
    version="1.0.0",
)

from fastapi.middleware.cors import CORSMiddleware


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your existing routes...

# Include the workflow router
app.include_router(workflow_router, prefix="/api/workflow", tags=["workflow"])

@app.get("/")
def root():
    return {
        "message": "B2B Textile Procurement Assistant Backend is running",
        "endpoints": {
            "start_workflow": "/api/workflow/start?user_input=your_input&input_type=quote",
            "continue_workflow": "/api/workflow/continue/{session_id}?supplier_response=response",
            "get_state": "/api/workflow/state/{session_id}",
            "get_history": "/api/workflow/history/{session_id}",
            "replay_workflow": "/api/workflow/replay/{session_id}?new_input_type=negotiate",
            "list_sessions": "/api/workflow/sessions"
        },
        "graph_config": {
            "default_get_quote_input": "I need a quote for 5,000 meters of organic cotton canvas",
            "default_negotiation_input": "Can you improve the lead time from 60 to 45 days?"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "textile-procurement-api"}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# uvicorn main:app --reload
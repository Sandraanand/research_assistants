"""
Simplified FastAPI Backend - FIXED VERSION
- Independent operations (no workflow required)
- PDF support
- Progress tracking
- All features work standalone
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
import asyncio

from config import config
from database import init_db, get_db, PaperSubmission
from orchestrator import get_orchestrator
from pdf_utils import extract_text_from_pdf, extract_pdf_metadata

# Initialize FastAPI
app = FastAPI(title="Simple Research Assistant - Fixed", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Progress tracking
workflow_progress = {}

# Initialize database on startup
@app.on_event("startup")
async def startup():
    config.validate()
    init_db()
    print("✅ Backend initialized - All features work independently!")


# ==================== Request/Response Models ====================

class ResearchRequest(BaseModel):
    topic: str
    max_papers: int = 5


class ConceptRequest(BaseModel):
    concept: str
    context: Optional[str] = None


class PaperCheckRequest(BaseModel):
    title: str
    content: str


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "running",
        "message": "Research Assistant API - Fixed Version",
        "version": "2.0.0",
        "features": [
            "Independent literature search",
            "Independent concept explanation",
            "Independent paper checking",
            "Full workflow (optional)"
        ]
    }


# ==================== LITERATURE SEARCH (Independent) ====================

@app.post("/api/literature/search")
async def search_literature_only(request: ResearchRequest):
    """
    Search literature ONLY - No synthesis, no extensions
    Independent operation
    """
    try:
        orch = get_orchestrator()
        results = await orch.search_literature(
            topic=request.topic,
            max_papers=request.max_papers
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== FULL RESEARCH WORKFLOW (Optional) ====================

@app.post("/api/research/full")
async def run_full_research(request: ResearchRequest):
    """
    Full workflow: Literature → Synthesis → Extensions
    """
    workflow_id = str(uuid.uuid4())
    
    # Initialize progress
    workflow_progress[workflow_id] = {
        "status": "starting",
        "step": "Initializing workflow",
        "progress": 0,
        "results": {}
    }
    
    # Start workflow in background
    asyncio.create_task(run_research_background(workflow_id, request))
    
    return {
        "workflow_id": workflow_id,
        "message": "Research workflow started",
        "check_progress_at": f"/api/research/progress/{workflow_id}"
    }


async def run_research_background(workflow_id: str, request: ResearchRequest):
    """Run research workflow in background"""
    try:
        orch = get_orchestrator()
        
        def update_progress(step, progress):
            workflow_progress[workflow_id].update({
                "status": "running",
                "step": step,
                "progress": progress
            })
        
        # Run full workflow
        results = await orch.run_full_workflow(
            topic=request.topic,
            max_papers=request.max_papers,
            progress_callback=update_progress
        )
        
        # Complete
        workflow_progress[workflow_id].update({
            "status": "completed",
            "step": "Research completed",
            "progress": 100,
            "results": results
        })
        
    except Exception as e:
        workflow_progress[workflow_id].update({
            "status": "failed",
            "step": f"Error: {str(e)}",
            "progress": 0,
            "error": str(e)
        })


@app.get("/api/research/progress/{workflow_id}")
async def get_research_progress(workflow_id: str):
    """Get research workflow progress"""
    if workflow_id not in workflow_progress:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow_progress[workflow_id]


# ==================== CONCEPT EXPLANATION (Independent) ====================

@app.post("/api/explain")
async def explain_concept(request: ConceptRequest):
    """
    Explain a concept - INDEPENDENT (no research workflow needed)
    Works standalone!
    """
    try:
        orch = get_orchestrator()
        explanation = await orch.explain_concept(
            concept=request.concept,
            context=request.context
        )
        return {
            "concept": request.concept,
            "explanation": explanation,
            "standalone": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PAPER CHECKING (Independent) ====================

@app.post("/api/check-paper")
async def check_paper(request: PaperCheckRequest):
    """
    Check paper formatting - INDEPENDENT (no research workflow needed)
    Works standalone!
    """
    try:
        orch = get_orchestrator()
        feedback = await orch.check_paper(
            title=request.title,
            content=request.content
        )
        return {
            **feedback,
            "standalone": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/check-paper-pdf")
async def check_paper_pdf(
    pdf_file: UploadFile = File(...),
    title: Optional[str] = Form(None)
):
    """
    Check paper formatting from PDF - INDEPENDENT
    Works standalone!
    """
    try:
        # Read PDF
        pdf_bytes = await pdf_file.read()
        
        # Extract text
        content = extract_text_from_pdf(pdf_bytes)
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Extract metadata if title not provided
        if not title:
            metadata = extract_pdf_metadata(pdf_bytes)
            title = metadata.get("title", pdf_file.filename)
        
        # Check formatting
        orch = get_orchestrator()
        feedback = await orch.check_paper(title=title, content=content)
        
        return {
            **feedback,
            "pdf_filename": pdf_file.filename,
            "standalone": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PAPER SUBMISSION (Independent) ====================

@app.post("/api/submit-paper-pdf")
async def submit_paper_pdf(
    pdf_file: UploadFile = File(...),
    title: str = Form(...),
    authors: str = Form(...),
    professor_email: str = Form(...)
):
    """
    Submit paper from PDF - INDEPENDENT
    Works standalone!
    """
    try:
        # Read PDF
        pdf_bytes = await pdf_file.read()
        
        # Extract text
        content = extract_text_from_pdf(pdf_bytes)
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Parse authors
        authors_list = [a.strip() for a in authors.split(",")]
        
        # Generate submission ID
        submission_id = f"SUB-{uuid.uuid4().hex[:8].upper()}"
        
        # Check formatting (optional, quick)
        try:
            orch = get_orchestrator()
            feedback = await orch.check_paper(title=title, content=content)
            feedback_text = feedback.get('feedback', '')
        except:
            feedback_text = "Formatting check skipped"
        
        # Store in database
        db = next(get_db())
        submission = PaperSubmission(
            submission_id=submission_id,
            title=title,
            authors=", ".join(authors_list),
            content=content[:5000],  # Store preview only
            professor_email=professor_email,
            status="submitted",
            feedback=feedback_text
        )
        db.add(submission)
        db.commit()
        
        return {
            "submission_id": submission_id,
            "status": "submitted",
            "message": f"Paper submitted to {professor_email}",
            "submitted_at": datetime.now().isoformat(),
            "formatting_feedback": feedback_text,
            "standalone": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SUBMISSION STATUS (Independent) ====================

@app.get("/api/submission/{submission_id}")
async def get_submission_status(submission_id: str):
    """
    Check submission status - INDEPENDENT
    Works anytime!
    """
    try:
        db = next(get_db())
        submission = db.query(PaperSubmission).filter(
            PaperSubmission.submission_id == submission_id
        ).first()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        return {
            "submission_id": submission.submission_id,
            "title": submission.title,
            "status": submission.status,
            "submitted_at": submission.submitted_at.isoformat(),
            "feedback": submission.feedback,
            "standalone": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.BACKEND_PORT)

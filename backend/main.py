import os
import uuid
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

from generator import AssignmentGenerator
from docx_builder import build_docx
from pdf_builder import build_pdf
from database import init_db, save_assignment, get_history, get_assignment_by_id

app = FastAPI(title="AssignmentForge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUTS_DIR = Path("/tmp/outputs") if os.environ.get("VERCEL") else Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)

init_db()


class GenerateRequest(BaseModel):
    student_name: str
    course_code: str = "AUTO"
    assignment_number: str = "1"
    assignment_type: str = "custom_assignment"
    business_name: Optional[str] = ""
    business_website: Optional[str] = ""
    business_industry: Optional[str] = ""
    business_mission: Optional[str] = ""
    additional_requirements: Optional[str] = ""
    openai_api_key: Optional[str] = ""
    instructor_name: Optional[str] = "TBD"


class GenerateResponse(BaseModel):
    id: str
    content: dict
    status: str


# Create a router for all API endpoints
api_router = APIRouter(prefix="/api")

@api_router.get("/")
def root():
    return {"message": "AssignmentForge API is running", "version": "1.0.0"}


@api_router.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@api_router.get("/assignment-types")
def get_assignment_types():
    return {
        "types": [
            {"id": "content_aggregators", "label": "Content Aggregators Research", "course": "SMALT", "number": "A1"},
            {"id": "social_media_aggregators_critique", "label": "Social Media Aggregators Critique", "course": "SMALT", "number": "A2"},
            {"id": "social_listening_critique", "label": "Social Media Listening Tools Critique", "course": "SMALT", "number": "A3"},
            {"id": "social_media_tools_report", "label": "Social Media Aggregators & Listeners", "course": "SMALT", "number": "A4"},
            {"id": "goals_objectives", "label": "Content Outreach – Goals & Objectives", "course": "CA-CNTOR", "number": "A1P1"},
            {"id": "target_audience", "label": "Content Outreach – Target Audience", "course": "CA-CNTOR", "number": "A1P2"},
            {"id": "content_plan_viral", "label": "Content Outreach – Content Plan & Viral", "course": "CA-CNTOR", "number": "A1P3"},
            {"id": "social_profiles_outreach", "label": "Social Media Profiles Outreach-Ready", "course": "CA-CNTOR", "number": "A2"},
            {"id": "influencer_outreach", "label": "Influencer Outreach", "course": "CA-CNTOR", "number": "A3"},
            {"id": "final_project_report", "label": "Final Project Report", "course": "CA-CNTOR", "number": "A4"},
        ]
    }


@api_router.post("/generate", response_model=GenerateResponse)
async def generate_assignment(req: GenerateRequest):
    assignment_id = str(uuid.uuid4())

    api_key = req.openai_api_key or os.environ.get("OPENAI_API_KEY", "")

    generator = AssignmentGenerator(api_key=api_key)

    try:
        content = await generator.generate(
            student_name=req.student_name,
            course_code=req.course_code,
            assignment_number=req.assignment_number,
            assignment_type=req.assignment_type,
            business_name=req.business_name,
            business_website=req.business_website,
            business_industry=req.business_industry,
            business_mission=req.business_mission,
            additional_requirements=req.additional_requirements,
            instructor_name=req.instructor_name,
        )

        save_assignment(
            assignment_id=assignment_id,
            student_name=req.student_name,
            course_code=req.course_code,
            assignment_type=req.assignment_type,
            content=content,
            business_name=req.business_name,
            business_website=req.business_website,
            additional_requirements=req.additional_requirements
        )

        return GenerateResponse(id=assignment_id, content=content, status="success")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/download/docx/{assignment_id}")
def download_docx(assignment_id: str):
    assignment = get_assignment_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    output_path = OUTPUTS_DIR / f"{assignment_id}.docx"
    build_docx(assignment["content"], output_path, assignment["student_name"], assignment["course_code"])

    filename = f"{assignment['student_name'].replace(' ', '_')}_{assignment['course_code']}_A{assignment['content'].get('assignment_number', '1')}.docx"
    return FileResponse(
        path=str(output_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )


@api_router.get("/download/pdf/{assignment_id}")
def download_pdf(assignment_id: str):
    assignment = get_assignment_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    output_path = OUTPUTS_DIR / f"{assignment_id}.pdf"
    build_pdf(assignment["content"], str(output_path))

    filename = f"{assignment['student_name'].replace(' ', '_')}_{assignment['course_code']}_A{assignment['content'].get('assignment_number', '1')}.pdf"
    return FileResponse(
        path=str(output_path),
        media_type="application/pdf",
        filename=filename,
    )


@api_router.post("/export/docx")
async def export_docx(content: dict):
    assignment_id = str(uuid.uuid4())
    output_path = OUTPUTS_DIR / f"{assignment_id}_temp.docx"
    student_name = content.get("student_name", "Student")
    course_code = content.get("course", "Academic")
    
    build_docx(content, output_path, student_name, course_code)
    
    return FileResponse(
        path=str(output_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"Assignment_{student_name.replace(' ', '_')}.docx",
    )


@api_router.post("/export/pdf")
async def export_pdf(content: dict):
    assignment_id = str(uuid.uuid4())
    output_path = OUTPUTS_DIR / f"{assignment_id}_temp.pdf"
    
    build_pdf(content, str(output_path))
    
    return FileResponse(
        path=str(output_path),
        media_type="application/pdf",
        filename=f"Assignment_{content.get('student_name', 'Student').replace(' ', '_')}.pdf",
    )


@api_router.get("/assignment/{assignment_id}")
def get_assignment(assignment_id: str):
    assignment = get_assignment_by_id(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@api_router.get("/history")
def get_assignment_history():
    return {"history": get_history()}


@api_router.post("/generate-image")
async def generate_image_endpoint(req: dict):
    prompt = req.get("prompt")
    api_key = req.get("openai_api_key") or os.environ.get("OPENAI_API_KEY", "")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required for image generation")

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        response = await client.images.generate(
            model="dall-e-3",
            prompt=f"A clean, professional academic screenshot or diagram for a student assignment: {prompt}. High quality, minimalist style, readable text.",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return {"url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/history/{assignment_id}")
def delete_assignment(assignment_id: str):
    conn = sqlite3.connect("/tmp/assignmentforge.db" if os.environ.get("VERCEL") else "assignmentforge.db")
    conn.execute("DELETE FROM assignments WHERE id = ?", (assignment_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

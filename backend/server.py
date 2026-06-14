"""CV Optimizer / ATS Enhancer — FastAPI backend."""
import os
import io
import uuid
import logging
import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Optional, Annotated, Any
from dotenv import load_dotenv

from fastapi import FastAPI, APIRouter, Depends, HTTPException, UploadFile, File, Form, Header
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field, ConfigDict, BeforeValidator
from bson import ObjectId

import ai_service
import file_service


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALG = "HS256"
JWT_EXP_DAYS = 30

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

app = FastAPI(title="CV Optimizer API")
api = APIRouter(prefix="/api")


# ===================== Helpers =====================

def _oid(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    return str(v)


PyObjectId = Annotated[str, BeforeValidator(_oid)]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXP_DAYS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")
    token = authorization.split(None, 1)[1].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        user_id = payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token")
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(401, "User not found")
    user.pop("_id", None)
    return user


# ===================== Models =====================

class RegisterReq(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginReq(BaseModel):
    email: EmailStr
    password: str


class AuthResp(BaseModel):
    token: str
    user: dict


class CVUploadResp(BaseModel):
    id: str
    filename: str
    text_length: int


class AnalyzeReq(BaseModel):
    cv_id: str
    job_title: str
    company: str
    job_description: str


class AnalysisResp(BaseModel):
    id: str
    cv_id: str
    job_title: str
    company: str
    ats_score: int
    score_breakdown: dict
    matched_keywords: List[str]
    missing_keywords: List[str]
    gaps: List[str]
    strengths: List[str]
    section_suggestions: dict
    overall_recommendation: str
    created_at: str


class OptimizeReq(BaseModel):
    analysis_id: str


class OptimizedCVResp(BaseModel):
    id: str
    analysis_id: str
    cv_id: str
    structured_cv: dict
    cover_letter: str
    created_at: str


# ===================== Auth =====================

@api.post("/auth/register", response_model=AuthResp)
async def register(req: RegisterReq):
    existing = await db.users.find_one({"email": req.email.lower()})
    if existing:
        raise HTTPException(409, "Email already registered")
    user_id = str(uuid.uuid4())
    doc = {
        "id": user_id,
        "name": req.name.strip(),
        "email": req.email.lower(),
        "password_hash": hash_password(req.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(doc)
    return AuthResp(token=create_token(user_id),
                    user={"id": user_id, "name": doc["name"], "email": doc["email"]})


@api.post("/auth/login", response_model=AuthResp)
async def login(req: LoginReq):
    user = await db.users.find_one({"email": req.email.lower()})
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    return AuthResp(token=create_token(user["id"]),
                    user={"id": user["id"], "name": user["name"], "email": user["email"]})


@api.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return {"id": user["id"], "name": user["name"], "email": user["email"]}


# ===================== CV Upload =====================

@api.post("/cv/upload", response_model=CVUploadResp)
async def upload_cv(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    if not file.filename:
        raise HTTPException(400, "No filename")
    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty file")
    try:
        text = file_service.parse_cv_bytes(content, file.filename)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if len(text) < 50:
        raise HTTPException(400, "Could not extract enough text from CV. Try a different file.")

    cv_id = str(uuid.uuid4())
    doc = {
        "id": cv_id,
        "user_id": user["id"],
        "filename": file.filename,
        "text": text,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.cvs.insert_one(doc)
    return CVUploadResp(id=cv_id, filename=file.filename, text_length=len(text))


@api.get("/cv/list")
async def list_cvs(user: dict = Depends(get_current_user)):
    cursor = db.cvs.find({"user_id": user["id"]}, {"_id": 0, "text": 0}).sort("created_at", -1)
    return await cursor.to_list(100)


@api.get("/cv/{cv_id}")
async def get_cv(cv_id: str, user: dict = Depends(get_current_user)):
    cv = await db.cvs.find_one({"id": cv_id, "user_id": user["id"]}, {"_id": 0})
    if not cv:
        raise HTTPException(404, "CV not found")
    return cv


# ===================== Analyze =====================

@api.post("/analyze", response_model=AnalysisResp)
async def analyze(req: AnalyzeReq, user: dict = Depends(get_current_user)):
    cv = await db.cvs.find_one({"id": req.cv_id, "user_id": user["id"]}, {"_id": 0})
    if not cv:
        raise HTTPException(404, "CV not found")

    session_id = f"analyze-{uuid.uuid4()}"
    result = await ai_service.analyze_cv(
        cv_text=cv["text"],
        job_title=req.job_title,
        company=req.company,
        job_description=req.job_description,
        session_id=session_id,
    )

    analysis_id = str(uuid.uuid4())
    doc = {
        "id": analysis_id,
        "user_id": user["id"],
        "cv_id": req.cv_id,
        "job_title": req.job_title,
        "company": req.company,
        "job_description": req.job_description,
        "ats_score": int(result.get("ats_score", 0)),
        "score_breakdown": result.get("score_breakdown", {}),
        "matched_keywords": result.get("matched_keywords", []),
        "missing_keywords": result.get("missing_keywords", []),
        "gaps": result.get("gaps", []),
        "strengths": result.get("strengths", []),
        "section_suggestions": result.get("section_suggestions", {}),
        "overall_recommendation": result.get("overall_recommendation", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.analyses.insert_one(doc)
    doc.pop("job_description", None)
    return AnalysisResp(**doc)


@api.get("/analyses")
async def list_analyses(user: dict = Depends(get_current_user)):
    cursor = db.analyses.find(
        {"user_id": user["id"]},
        {"_id": 0, "job_description": 0, "section_suggestions": 0, "matched_keywords": 0,
         "missing_keywords": 0, "gaps": 0, "strengths": 0, "score_breakdown": 0}
    ).sort("created_at", -1)
    return await cursor.to_list(100)


@api.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: str, user: dict = Depends(get_current_user)):
    a = await db.analyses.find_one({"id": analysis_id, "user_id": user["id"]}, {"_id": 0})
    if not a:
        raise HTTPException(404, "Analysis not found")
    return a


# ===================== Optimize =====================

@api.post("/optimize", response_model=OptimizedCVResp)
async def optimize(req: OptimizeReq, user: dict = Depends(get_current_user)):
    analysis = await db.analyses.find_one({"id": req.analysis_id, "user_id": user["id"]}, {"_id": 0})
    if not analysis:
        raise HTTPException(404, "Analysis not found")
    cv = await db.cvs.find_one({"id": analysis["cv_id"], "user_id": user["id"]}, {"_id": 0})
    if not cv:
        raise HTTPException(404, "Source CV not found")

    session_id_opt = f"optimize-{uuid.uuid4()}"
    structured = await ai_service.optimize_cv(
        cv_text=cv["text"],
        job_title=analysis["job_title"],
        company=analysis["company"],
        job_description=analysis["job_description"],
        missing_keywords=analysis.get("missing_keywords", []),
        session_id=session_id_opt,
    )

    session_id_cl = f"coverletter-{uuid.uuid4()}"
    candidate_name = structured.get("full_name") or user.get("name", "")
    cover_letter = await ai_service.generate_cover_letter(
        cv_text=cv["text"],
        job_title=analysis["job_title"],
        company=analysis["company"],
        job_description=analysis["job_description"],
        candidate_name=candidate_name,
        session_id=session_id_cl,
    )

    opt_id = str(uuid.uuid4())
    doc = {
        "id": opt_id,
        "user_id": user["id"],
        "analysis_id": req.analysis_id,
        "cv_id": analysis["cv_id"],
        "structured_cv": structured,
        "cover_letter": cover_letter,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.optimized.insert_one(doc)
    return OptimizedCVResp(
        id=opt_id, analysis_id=req.analysis_id, cv_id=analysis["cv_id"],
        structured_cv=structured, cover_letter=cover_letter, created_at=doc["created_at"],
    )


@api.get("/optimized/{opt_id}")
async def get_optimized(opt_id: str, user: dict = Depends(get_current_user)):
    o = await db.optimized.find_one({"id": opt_id, "user_id": user["id"]}, {"_id": 0})
    if not o:
        raise HTTPException(404, "Optimized CV not found")
    return o


# ===================== Downloads =====================

def _slug(s: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in (s or "cv")).strip("_") or "cv"


@api.get("/optimized/{opt_id}/download")
async def download_optimized(opt_id: str, kind: str, fmt: str,
                             token: Optional[str] = None,
                             authorization: Optional[str] = Header(None)):
    """kind: cv | cover_letter ; fmt: pdf | docx. Accepts token via query (for direct browser downloads) or header."""
    # Auth via header OR query token (for <a href> downloads)
    auth_token: Optional[str] = None
    if authorization and authorization.lower().startswith("bearer "):
        auth_token = authorization.split(None, 1)[1].strip()
    elif token:
        auth_token = token
    if not auth_token:
        raise HTTPException(401, "Missing token")
    try:
        payload = jwt.decode(auth_token, JWT_SECRET, algorithms=[JWT_ALG])
        user_id = payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")

    o = await db.optimized.find_one({"id": opt_id, "user_id": user_id}, {"_id": 0})
    if not o:
        raise HTTPException(404, "Not found")

    cv = o["structured_cv"]
    candidate = cv.get("full_name") or "candidate"
    base = _slug(candidate)

    if kind == "cv" and fmt == "pdf":
        data = file_service.generate_cv_pdf(cv)
        media = "application/pdf"
        filename = f"{base}_optimized_cv.pdf"
    elif kind == "cv" and fmt == "docx":
        data = file_service.generate_cv_docx(cv)
        media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{base}_optimized_cv.docx"
    elif kind == "cover_letter" and fmt == "pdf":
        data = file_service.generate_cover_letter_pdf(o["cover_letter"], candidate)
        media = "application/pdf"
        filename = f"{base}_cover_letter.pdf"
    elif kind == "cover_letter" and fmt == "docx":
        data = file_service.generate_cover_letter_docx(o["cover_letter"], candidate)
        media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{base}_cover_letter.docx"
    else:
        raise HTTPException(400, "Invalid kind/fmt")

    return StreamingResponse(
        io.BytesIO(data),
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ===================== Root =====================

@api.get("/")
async def root():
    return {"app": "CV Optimizer API", "status": "ok"}


app.include_router(api)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

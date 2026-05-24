from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from app.github_client import fetch_repository_files
from app.analyser import analyse_repository
from app.ai_recommender import generate_recommendation

load_dotenv()

app = FastAPI(
    title="ReactLens API",
    description="AI-powered technical debt analysis for React codebases",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ─────────────────────────────────────────

class AnalyseRequest(BaseModel):
    repo_url: str
    github_token: Optional[str] = None
    anthropic_key: Optional[str] = None


class ComponentResult(BaseModel):
    filename: str
    filepath: str
    loc: int
    props_count: int
    any_count: int
    todo_count: int
    component_count: int
    nested_ternary_count: int
    console_log_count: int
    missing_return_type_count: int
    debt_score: float
    debt_level: str
    issues: list[str]


class AnalyseResponse(BaseModel):
    repo_name: str
    total_files: int
    high_debt_count: int
    medium_debt_count: int
    low_debt_count: int
    components: list[ComponentResult]
    ai_summary: Optional[str] = None
    ai_top_issues: Optional[list[str]] = None
    ai_remediation_plan: Optional[list[str]] = None
    ai_overall_score: Optional[int] = None
    ai_score_label: Optional[str] = None


# ── Routes ────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "ReactLens API is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/analyse", response_model=AnalyseResponse)
async def analyse(request: AnalyseRequest):
    # Validate URL
    if "github.com" not in request.repo_url:
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid GitHub repository URL.",
        )

    github_token  = request.github_token  or os.getenv("GITHUB_TOKEN")
    anthropic_key = request.anthropic_key or os.getenv("ANTHROPIC_API_KEY")

    # Fetch files from GitHub
    try:
        files = await fetch_repository_files(request.repo_url, token=github_token)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch repository: {str(e)}",
        )

    if not files:
        raise HTTPException(
            status_code=404,
            detail="No React/TypeScript files found in this repository.",
        )

    # Run static analysis
    results = analyse_repository(files)

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No analysable React component files found.",
        )

    repo_name = request.repo_url.rstrip("/").split("/")[-1]

    high   = [r for r in results if r.debt_level == "high"]
    medium = [r for r in results if r.debt_level == "medium"]
    low    = [r for r in results if r.debt_level == "low"]

    response = AnalyseResponse(
        repo_name=repo_name,
        total_files=len(results),
        high_debt_count=len(high),
        medium_debt_count=len(medium),
        low_debt_count=len(low),
        components=[ComponentResult(**vars(r)) for r in results],
    )

    # AI recommendations (non-fatal if unavailable)
    if anthropic_key:
        try:
            top_components = [
                {
                    "filename":   r.filename,
                    "debt_score": r.debt_score,
                    "issues":     r.issues,
                }
                for r in results[:5]
            ]
            ai = generate_recommendation(
                repo_name=repo_name,
                total_files=len(results),
                high_debt_files=len(high),
                medium_debt_files=len(medium),
                low_debt_files=len(low),
                top_components=top_components,
                api_key=anthropic_key,
            )
            response.ai_summary          = ai.summary
            response.ai_top_issues       = ai.top_issues
            response.ai_remediation_plan = ai.remediation_plan
            response.ai_overall_score    = ai.overall_score
            response.ai_score_label      = ai.score_label
        except Exception as e:
            response.ai_summary = f"AI recommendations unavailable: {str(e)}"

    return response

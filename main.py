from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from pathlib import Path
from fastapi import Form

from scrapers import leetcode_scraper, github_scraper, resume_parser
from core import scorer

app = FastAPI(title="ELO Rating System API", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "ELO Rating System API",
        "version": "1.0",
        "endpoints": {
            "calculate_rating": "/api/calculate-rating",
            "health": "/api/health"
        }
    }


@app.post("/api/calculate-rating")
async def calculate_rating(
    leetcode_username: str = Form(...), # <-- Change here
    github_username: str = Form(...),   # <-- And here
    resume: UploadFile = File(...)
):
    """
    Calculate comprehensive ELO rating from all platforms.
    
    Parameters:
    - leetcode_username: LeetCode profile username
    - github_username: GitHub profile username
    - resume: Resume file (PDF, DOCX, or TXT)
    
    Returns:
    - ELO rating (1000-2500)
    - Platform scores (0-100 each)
    - Raw data from each platform
    """
    try:
        # Step 1: Fetch LeetCode data
        print(f"📊 Fetching LeetCode data for {leetcode_username}...")
        leetcode_data = leetcode_scraper.get_leetcode_data(leetcode_username)
        
        # Step 2: Fetch GitHub data
        print(f"💻 Fetching GitHub data for {github_username}...")
        github_data = github_scraper.get_github_data(github_username)
        
        # Step 3: Parse resume
        print(f"📄 Parsing resume: {resume.filename}...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(resume.filename).suffix) as tmp_file:
            content = await resume.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            metrics = resume_parser.parse_resume(tmp_file_path)
            
            if not metrics:
                raise ValueError("Failed to parse resume")
            
            score_result = resume_parser.calculate_resume_score(metrics)
            
            resume_data = {
                "internships": metrics['internships'],
                "projects": metrics['projects'],
                "certifications": metrics['certifications'],
                "skills": metrics['skills'],
                "achievements": metrics['achievements'],
                "score": score_result['scores']['total_score']
            }
            
        finally:
            os.unlink(tmp_file_path)
        
        # Step 4: Compile platform scores
        platform_scores = {
            "leetcode_score": leetcode_data["score"],
            "github_score": github_data["score"],
            "resume_score": resume_data["score"]
        }
        
        # Step 5: Calculate final ELO
        elo_rating = scorer.compute_elo(platform_scores)
        
        print(f"✅ ELO Rating calculated: {elo_rating}")
        
        return {
            "username": leetcode_username,
            "elo_rating": elo_rating,
            "platform_scores": platform_scores,
            "raw_data": {
                "leetcode": leetcode_data,
                "github": github_data,
                "resume": resume_data
            }
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "services": {
            "leetcode": "operational",
            "github": "operational",
            "resume_parser": "operational"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
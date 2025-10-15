# api/ratings.py

from fastapi import APIRouter
from scrapers import leetcode_scraper, github_scraper
from core import scorer
from schemas.profile import UserProfileData, LeetCodeProfile, GitHubProfile

router = APIRouter()

@router.get("/elo/{username}", tags=["Ratings"])
def get_user_elo(username: str):
    # Step 1: Scrape data from all platforms
    lc_data = leetcode_scraper.get_leetcode_data(username)
    gh_data = github_scraper.get_github_data(username)
    
    # Step 2: Validate data with Pydantic schemas
    user_profile = UserProfileData(
        leetcode=LeetCodeProfile(**lc_data),
        github=GitHubProfile(**gh_data)
    )

    # Step 3: Calculate platform scores (0-100)
    platform_scores = scorer.calculate_platform_scores(user_profile)
    
    # Step 4: Compute the final ELO rating
    elo_rating = scorer.compute_elo(platform_scores)
    
    return {
        "username": username,
        "elo_rating": elo_rating,
        "platform_scores": platform_scores,
        "raw_data": user_profile
    }

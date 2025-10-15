# schemas/profile.py

from pydantic import BaseModel

class LeetCodeProfile(BaseModel):
    total_solved: int
    hard_solved: int
    contest_rating: int

class GitHubProfile(BaseModel):
    repos: int
    commits_last_year: int
    stars_received: int

class UserProfileData(BaseModel):
    leetcode: LeetCodeProfile
    github: GitHubProfile

"""
GitHub Data Scraper
Fetches repository stats, contributions, and activity from GitHub API
"""

import requests
import os # Import the 'os' module to access environment variables


def get_github_data(username: str) -> dict:
    """
    Fetch GitHub data and calculate score.
    
    Args:
        username: GitHub username
    
    Returns:
        dict: {
            "public_repos": int,
            "commits_last_year": int,
            "total_stars": int,
            "followers": int,
            "language_diversity": int,
            "score": int (0-100)
        }
    
    Scoring Formula:
        - Repositories (20%): (repos / 50) * 20
        - Commits (30%): (commits / 1000) * 30
        - Stars (25%): (stars / 200) * 25
        - Followers (15%): (followers / 100) * 15
        - Languages (10%): (languages / 10) * 10
    """
    
    # --- CHANGE: Create headers to send the API token ---
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    try:
        # We now check the status code directly and give a more precise error.
        # --- CHANGE: Pass the headers with the request ---
        user_response = requests.get(f"https://api.github.com/users/{username}", headers=headers)
        
        if user_response.status_code == 404:
            raise ValueError(f"GitHub user '{username}' not found. Please check for typos and correct capitalization.")
        user_response.raise_for_status() # Raises an error for other bad responses (500, 403, etc.)
        
        user_data = user_response.json()
        public_repos = user_data.get("public_repos", 0)
        followers = user_data.get("followers", 0)
        
        # Fetch contribution data (commits last year)
        contrib_response = requests.get(
            f"https://github-contributions-api.jogruber.de/v4/{username}?y=last"
        )
        commits_last_year = 0
        if contrib_response.status_code == 200:
            contrib_data = contrib_response.json().get("total", {})
            if contrib_data:
                commits_last_year = contrib_data.get("lastYear", 0)
        
        # Fetch repositories for stars and language diversity
        # --- CHANGE: Pass the headers with the request ---
        repos_response = requests.get(
            f"https://api.github.com/users/{username}/repos?per_page=100", headers=headers
        )
        repos_response.raise_for_status()
        
        total_stars = 0
        unique_languages = set()
        
        for repo in repos_response.json():
            total_stars += repo.get("stargazers_count", 0)
            language = repo.get("language")
            if language:
                unique_languages.add(language)
        
        language_diversity = len(unique_languages)
        
        # Calculate GitHub score (0-100)
        max_values = {
            "repos": 50,
            "commits": 1000,
            "stars": 200,
            "followers": 100,
            "languages": 10
        }

        # Apply caps to prevent outliers
        capped_repos = min(public_repos, max_values["repos"])
        capped_commits = min(commits_last_year, max_values["commits"])
        capped_stars = min(total_stars, max_values["stars"])
        capped_followers = min(followers, max_values["followers"])
        capped_languages = min(language_diversity, max_values["languages"])
        
        # Calculate weighted score components
        repo_score = (capped_repos / max_values["repos"]) * 20
        commit_score = (capped_commits / max_values["commits"]) * 30
        star_score = (capped_stars / max_values["stars"]) * 25
        follower_score = (capped_followers / max_values["followers"]) * 15
        language_score = (capped_languages / max_values["languages"]) * 10
        
        github_score = round(
            repo_score + commit_score + star_score + follower_score + language_score
        )
        
        return {
            "public_repos": public_repos,
            "commits_last_year": commits_last_year,
            "total_stars": total_stars,
            "followers": followers,
            "language_diversity": language_diversity,
            "score": github_score
        }
        
    except requests.RequestException as e:
        raise ValueError(f"Network error when fetching GitHub data: {str(e)}")
    except ValueError as e: # Catch our specific "not found" error
        raise e
    except Exception as e:
        # This will now catch other unexpected errors during processing
        raise ValueError(f"An unexpected error occurred while processing GitHub data: {str(e)}")


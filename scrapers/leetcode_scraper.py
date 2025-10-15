"""
LeetCode Data Scraper
Fetches problem stats and contest rating from LeetCode GraphQL API
"""

import requests


def get_leetcode_data(username: str) -> dict:
    """
    Fetch LeetCode data and calculate score.
    
    Args:
        username: LeetCode username
    
    Returns:
        dict: {
            "total_solved": int,
            "hard_solved": int,
            "contest_rating": int,
            "has_contest_history": bool,
            "score": float (0-100)
        }
    
    Note:
        - Users without contest participation get base rating of 1500
        - This prevents penalizing non-contest participants
    
    Scoring Formula:
        - Total problems (40%): (total_solved / 1000) * 40
        - Difficulty ratio (20%): (hard_solved / total_solved) * 20
        - Contest rating (40%): (contest_rating / 2500) * 40
    """
    url = "https://leetcode.com/graphql"
    
    # Query 1: Get problem statistics
    query_problems = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        submitStats: submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """
    
    # Query 2: Get contest rating
    query_contest = """
    query userContestRankingInfo($username: String!) {
        userContestRanking(username: $username) {
            attendedContestsCount
            rating
            globalRanking
            topPercentage
        }
    }
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/json',
        'Referer': f'https://leetcode.com/{username}'
    }
    
    try:
        # Fetch problem stats
        response1 = requests.post(
            url, 
            json={"query": query_problems, "variables": {"username": username}}, 
            headers=headers
        )
        data1 = response1.json()
        
        if data1.get("errors") or not data1.get("data", {}).get("matchedUser"):
            raise ValueError(f"LeetCode user '{username}' not found")
        
        # Parse problem statistics
        submissions = data1["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]
        solved_stats = {"All": 0, "Hard": 0}
        for sub in submissions:
            if sub["difficulty"] in solved_stats:
                solved_stats[sub["difficulty"]] = sub["count"]
        
        # Fetch contest rating
        response2 = requests.post(
            url, 
            json={"query": query_contest, "variables": {"username": username}}, 
            headers=headers
        )
        data2 = response2.json()
        
        # Default base rating for users without contest participation
        contest_rating = 1500
        has_contest_history = False
        
        if data2.get("data", {}).get("userContestRanking"):
            contest_data = data2["data"]["userContestRanking"]
            if contest_data.get("rating"):
                contest_rating = round(contest_data["rating"])
                has_contest_history = True
        
        # Calculate LeetCode score (0-100)
        total_solved = solved_stats["All"]
        hard_solved = solved_stats["Hard"]
        
        # Component 1: Total problems solved (cap at 1000)
        total_solved_capped = min(total_solved, 1000)
        total_score_part = (total_solved_capped / 1000) * 40
        
        # Component 2: Difficulty ratio (hard problems)
        difficulty_score_part = 0
        if total_solved > 0:
            difficulty_score_part = (hard_solved / total_solved) * 20
        
        # Component 3: Contest rating (cap at 2500)
        contest_rating_capped = min(contest_rating, 2500)
        rating_score_part = (contest_rating_capped / 2500) * 40
        
        leetcode_score = round(total_score_part + difficulty_score_part + rating_score_part, 2)
        
        return {
            "total_solved": total_solved,
            "hard_solved": hard_solved,
            "contest_rating": contest_rating,
            "has_contest_history": has_contest_history,
            "score": round(leetcode_score)
        }
        
    except requests.RequestException as e:
        raise ValueError(f"Error fetching LeetCode data: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing LeetCode data: {str(e)}")
"""
ELO Rating Calculation Module
Computes final ELO rating from platform scores
"""


def compute_elo(platform_scores: dict) -> int:
    """
    Calculate final ELO rating from weighted platform scores.
    
    Args:
        platform_scores: Dict containing scores from each platform
            - leetcode_score (0-100)
            - github_score (0-100)
            - resume_score (0-100)
    
    Returns:
        int: ELO rating (1000-2500 scale)
    
    Weights:
        - LeetCode: 40% (coding skills, problem-solving)
        - GitHub: 30% (practical development, collaboration)
        - Resume: 30% (professional experience, achievements)
    """
    
    # Weighted average of platform scores
    final_raw_score = (
        0.4 * platform_scores["leetcode_score"] +
        0.3 * platform_scores["github_score"] +
        0.3 * platform_scores["resume_score"]
    )
    
    # Convert 0-100 scale to ELO scale (1000-2500)
    # Formula: 1000 + (raw_score / 100) * 1500
    elo = 1000 + (final_raw_score / 100) * 1500
    
    return int(elo)


def get_rating_tier(elo: int) -> dict:
    """
    Get rating tier information based on ELO score.
    
    Args:
        elo: ELO rating (1000-2500)
    
    Returns:
        dict: Tier information including name, color, and percentile
    """
    if elo >= 2300:
        return {
            "tier": "Grandmaster",
            "color": "#FF6B6B",
            "percentile": "Top 1%",
            "description": "Elite developer"
        }
    elif elo >= 2100:
        return {
            "tier": "Master",
            "color": "#FFD93D",
            "percentile": "Top 5%",
            "description": "Expert developer"
        }
    elif elo >= 1900:
        return {
            "tier": "Diamond",
            "color": "#6BCB77",
            "percentile": "Top 15%",
            "description": "Advanced developer"
        }
    elif elo >= 1700:
        return {
            "tier": "Platinum",
            "color": "#4D96FF",
            "percentile": "Top 30%",
            "description": "Proficient developer"
        }
    elif elo >= 1500:
        return {
            "tier": "Gold",
            "color": "#F4A460",
            "percentile": "Top 50%",
            "description": "Competent developer"
        }
    elif elo >= 1300:
        return {
            "tier": "Silver",
            "color": "#C0C0C0",
            "percentile": "Top 70%",
            "description": "Developing skills"
        }
    else:
        return {
            "tier": "Bronze",
            "color": "#CD7F32",
            "percentile": "Entry level",
            "description": "Beginner"
        }
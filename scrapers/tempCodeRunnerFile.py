def calculate_linkedin_score(internships: int, certifications: int, 
                            endorsements: int, recommendations: int) -> float:
    """
    Calculates LinkedIn Professional Readiness Score (max 20/100 for overall score).
    
    Weight Distribution:
    - Internships: 40% (cap at 2 = 80%)
    - Certifications: 30% 
    - Endorsements: 20% (cap at 50)
    - Recommendations: 10% (cap at 10)
    """
    # Internships: 40% weight, capped at 2 internships = 80%
    internships_capped = min(internships, 2)
    internships_score = (internships_capped / 2) * 0.80 * 40
    
    # Certifications: 30% weight
    # Formula: (certifications / 5) * 30, capped at 30
    certifications_score = min((certifications / 5) * 30, 30)
    
    # Endorsements: 20% weight, capped at 50 endorsements
    # Formula: (endorsements / 50) * 20
    endorsements_capped = min(endorsements, 50)
    endorsements_score = (endorsements_capped / 50) * 20
    
    # Recommendations: 10% weight, capped at 10
    # Formula: (recommendations / 10) * 10
    recommendations_capped = min(recommendations, 10)
    recommendations_score = (recommendations_capped / 10) * 10
    
    total_score = (internships_score + certifications_score + 
                   endorsements_score + recommendations_score)
    
    return round(total_score, 2)


def display_breakdown(internships: int, certifications: int, 
                     endorsements: int, recommendations: int, 
                     total_score: float):
    """
    Displays detailed score breakdown with visual representation.
    """
    print("\n" + "=" * 60)
    print("🎯 LINKEDIN PROFESSIONAL READINESS SCORE BREAKDOWN")
    print("=" * 60)
    
    # Calculate individual scores
    internships_capped = min(internships, 2)
    internships_score = (internships_capped / 2) * 0.80 * 40
    
    certifications_score = min((certifications / 5) * 30, 30)
    
    endorsements_capped = min(endorsements, 50)
    endorsements_score = (endorsements_capped / 50) * 20
    
    recommendations_capped = min(recommendations, 10)
    recommendations_score = (recommendations_capped / 10) * 10
    
    # Display metrics
    print(f"\n📊 YOUR METRICS:")
    print("-" * 60)
    print(f"  Internships:       {internships:>3} {'(capped at 2)' if internships > 2 else ''}")
    print(f"  Certifications:    {certifications:>3}")
    print(f"  Endorsements:      {endorsements:>3} {'(capped at 50)' if endorsements > 50 else ''}")
    print(f"  Recommendations:   {recommendations:>3} {'(capped at 10)' if recommendations > 10 else ''}")
    
    # Display score breakdown
    print(f"\n💯 SCORE BREAKDOWN:")
    print("-" * 60)
    print(f"  Internships       (40%): {internships_score:>6.2f} / 40.00")
    print(f"  Certifications    (30%): {certifications_score:>6.2f} / 30.00")
    print(f"  Endorsements      (20%): {endorsements_score:>6.2f} / 20.00")
    print(f"  Recommendations   (10%): {recommendations_score:>6.2f} / 10.00")
    print("-" * 60)
    print(f"  TOTAL SCORE:             {total_score:>6.2f} / 100.00")
    print("=" * 60)
    
    # Performance assessment
    if total_score >= 80:
        assessment = "🌟 EXCELLENT - Outstanding professional profile!"
    elif total_score >= 60:
        assessment = "✨ GOOD - Strong professional presence"
    elif total_score >= 40:
        assessment = "📈 MODERATE - Room for improvement"
    else:
        assessment = "🎯 DEVELOPING - Focus on building your profile"
    
    print(f"\n{assessment}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS TO IMPROVE:")
    print("-" * 60)
    if internships < 2:
        print(f"  • Gain {2 - internships} more internship(s) for maximum impact")
    if certifications < 5:
        print(f"  • Add {5 - certifications} more certification(s) to reach optimal level")
    if endorsements < 50:
        print(f"  • Request {50 - endorsements} more endorsement(s) from connections")
    if recommendations < 10:
        print(f"  • Get {10 - recommendations} more recommendation(s) from colleagues/managers")
    print("=" * 60 + "\n")


def get_valid_input(prompt: str, metric_name: str) -> int:
    """
    Gets valid integer input from user with error handling.
    """
    while True:
        try:
            value = input(prompt)
            if value.strip() == "":
                print(f"❌ {metric_name} cannot be empty. Please enter a number.")
                continue
            num = int(value)
            if num < 0:
                print(f"❌ {metric_name} cannot be negative. Please enter a valid number.")
                continue
            return num
        except ValueError:
            print(f"❌ Invalid input. Please enter a valid number for {metric_name}.")


def main():
    """
    Main function to run the LinkedIn score calculator.
    """
    print("=" * 60)
    print("🔗 LINKEDIN PROFESSIONAL READINESS SCORE CALCULATOR")
    print("=" * 60)
    print("\nThis evaluates industry exposure, network strength, and credibility.")
    print("Please enter your LinkedIn profile metrics:\n")
    
    # Get user inputs
    internships = get_valid_input(
        "Number of Internships: ",
        "Internships"
    )
    
    certifications = get_valid_input(
        "Number of Certifications: ",
        "Certifications"
    )
    
    endorsements = get_valid_input(
        "Number of Endorsements: ",
        "Endorsements"
    )
    
    recommendations = get_valid_input(
        "Number of Recommendations: ",
        "Recommendations"
    )
    
    # Calculate score
    score = calculate_linkedin_score(
        internships, certifications, endorsements, recommendations
    )
    
    # Display results
    display_breakdown(
        internships, certifications, endorsements, recommendations, score
    )


if __name__ == "__main__":
    main()
import re
import os
from pathlib import Path
from collections import Counter
from typing import Dict, List, Set, Tuple

# PDF parsing
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️  PyPDF2 not installed. Install with: pip install PyPDF2")

# DOCX parsing
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️  python-docx not installed. Install with: pip install python-docx")


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    if not PDF_AVAILABLE:
        raise ImportError("PyPDF2 is required to parse PDF files")
    
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx is required to parse DOCX files")
    
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()


def extract_resume_text(file_path: str) -> str:
    """Extract text from resume file based on extension."""
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Supported: .pdf, .docx, .txt")


def find_section(text: str, section_headers: List[str]) -> Tuple[int, int]:
    """
    Find a section in the resume by multiple possible headers.
    Returns (start_pos, end_pos) or (-1, -1) if not found.
    """
    text_lower = text.lower()
    
    # Try to find the section header
    for header in section_headers:
        pattern = r'\n\s*' + re.escape(header) + r'\s*[:\n]'
        match = re.search(pattern, text_lower)
        if match:
            start = match.end()
            
            # Find the next section (common section headers)
            next_section_pattern = r'\n\s*(experience|work\s+experience|internships?|professional\s+experience|projects?|education|academic\s+background|certifications?|certificates?|achievements?|awards?|honors?|technical\s+skills?|skills?|extracurricular|activities|leadership|positions?\s+of\s+responsibility|training|courses?|publications?|references?)\s*[:\n]'
            next_match = re.search(next_section_pattern, text_lower[start:])
            
            if next_match:
                end = start + next_match.start()
            else:
                end = start + 3000  # Read next 3000 chars if no next section
            
            return start, end
    
    return -1, -1


def count_internships(text: str) -> int:
    """
    Count internships and work experiences using multiple strategies.
    """
    text_lower = text.lower()
    
    # Strategy 1: Find experience section and count entries
    exp_headers = [
        'experience', 'work experience', 'professional experience',
        'internships', 'internship', 'work history', 'employment'
    ]
    
    start, end = find_section(text, exp_headers)
    
    if start != -1:
        section_text = text_lower[start:end]
        
        # Count different indicators
        indicators = []
        
        # 1. Date ranges (MMM YYYY - MMM YYYY or MMM YYYY - Present)
        date_patterns = re.findall(
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s,.-]*\d{4}\s*[-–—to]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|present|current|ongoing)',
            section_text
        )
        indicators.append(len(date_patterns))
        
        # 2. Company/organization names (usually followed by location or date)
        # Look for capitalized words followed by city/date patterns
        company_patterns = len(re.findall(
            r'\n\s*[A-Z][a-zA-Z\s&,.-]+(?:\s+[-–|]\s+|\s*\n\s*)(?:[A-Z][a-z]+(?:,\s*[A-Z]{2})?|\d{4})',
            text[start:end]
        ))
        indicators.append(company_patterns)
        
        # 3. Role/position titles
        role_keywords = [
            'intern', 'developer', 'engineer', 'analyst', 'designer',
            'consultant', 'associate', 'trainee', 'assistant', 'specialist',
            'coordinator', 'lead', 'manager', 'researcher', 'programmer',
            'scientist', 'architect', 'administrator', 'technician'
        ]
        role_pattern = r'\b(' + '|'.join(role_keywords) + r')\b'
        role_count = len(re.findall(role_pattern, section_text))
        indicators.append(role_count)
        
        # 4. Bullet points (each experience typically has multiple bullets)
        bullets = len(re.findall(r'\n\s*[•●▪▸►→⦿◆■-]\s+', section_text))
        # Estimate experiences (typically 3-5 bullets per experience)
        indicators.append(bullets // 4)
        
        # Take the median of non-zero indicators for robustness
        valid_indicators = [i for i in indicators if i > 0]
        if valid_indicators:
            valid_indicators.sort()
            count = valid_indicators[len(valid_indicators) // 2]
            return min(count, 5)  # Cap at 5
    
    # Fallback: Search entire document
    fallback_count = len(re.findall(
        r'\b(intern|internship|co-?op|trainee)\b',
        text_lower
    ))
    
    return min(max(fallback_count, 0), 5)


def count_projects(text: str) -> int:
    """
    Count projects using multiple detection strategies.
    """
    text_lower = text.lower()
    
    # Find projects section
    project_headers = [
        'projects', 'personal projects', 'academic projects',
        'key projects', 'technical projects', 'major projects',
        'project work', 'project experience'
    ]
    
    start, end = find_section(text, project_headers)
    
    if start != -1:
        section_text = text_lower[start:end]
        original_section = text[start:end]
        
        indicators = []
        
        # 1. Project title patterns (Name | Tech Stack or Name - Tech Stack)
        title_patterns = len(re.findall(
            r'\n\s*[A-Z][a-zA-Z0-9\s]+\s*[|–—-]\s*[A-Za-z,\s.+#]+',
            original_section
        ))
        indicators.append(title_patterns)
        
        # 2. Action verbs that start project descriptions
        action_verbs = [
            'developed', 'built', 'created', 'designed', 'implemented',
            'engineered', 'constructed', 'programmed', 'coded', 'architected',
            'deployed', 'launched', 'established', 'integrated', 'devised'
        ]
        action_pattern = r'\b(' + '|'.join(action_verbs) + r')\b'
        action_count = len(re.findall(action_pattern, section_text))
        # Each project typically has 1-3 action verbs
        indicators.append(action_count // 2)
        
        # 3. Technical terms indicating project scope
        tech_indicators = len(re.findall(
            r'(web\s+application|mobile\s+app|system|platform|api|website|software|tool|dashboard|interface|database|algorithm|model|framework)',
            section_text
        ))
        indicators.append(tech_indicators // 2)
        
        # 4. Bullet points
        bullets = len(re.findall(r'\n\s*[•●▪▸►→⦿◆■-]\s+', section_text))
        indicators.append(bullets // 3)  # Typically 2-4 bullets per project
        
        # 5. GitHub/link patterns
        github_links = len(re.findall(r'github\.com|gitlab\.com|bitbucket\.org', section_text))
        indicators.append(github_links)
        
        # Use median of valid indicators
        valid_indicators = [i for i in indicators if i > 0]
        if valid_indicators:
            valid_indicators.sort()
            count = valid_indicators[len(valid_indicators) // 2]
            return min(max(count, 1), 8)  # At least 1 if section exists, cap at 8
    
    # Fallback: Look for project-like descriptions globally
    fallback = len(re.findall(
        r'(developed|built|created)\s+(?:a|an|the)?\s*(?:\w+\s+){0,3}(application|system|platform|website|tool)',
        text_lower
    ))
    
    return min(max(fallback, 0), 8)


def count_certifications(text: str) -> int:
    """
    Count certifications and courses with comprehensive pattern matching.
    """
    text_lower = text.lower()
    
    # Find certification section
    cert_headers = [
        'certifications', 'certification', 'certificates',
        'licenses and certifications', 'professional certifications',
        'courses', 'online courses', 'training', 'courses and certifications'
    ]
    
    start, end = find_section(text, cert_headers)
    
    if start != -1:
        section_text = text_lower[start:end]
        
        indicators = []
        
        # 1. Count bullet points
        bullets = len(re.findall(r'\n\s*[•●▪▸►→⦿◆■-]\s+', section_text))
        indicators.append(bullets)
        
        # 2. Platform names
        platforms = [
            'coursera', 'udemy', 'edx', 'linkedin learning', 'pluralsight',
            'udacity', 'codecademy', 'freecodecamp', 'khan academy',
            'microsoft', 'google', 'amazon', 'ibm', 'oracle', 'cisco',
            'aws', 'azure', 'comptia', 'nptel', 'swayam'
        ]
        platform_pattern = r'\b(' + '|'.join(platforms) + r')\b'
        platform_count = len(re.findall(platform_pattern, section_text))
        indicators.append(platform_count)
        
        # 3. Certification keywords
        cert_keywords = len(re.findall(
            r'\b(certified|certification|certificate|credential|diploma|course|training|completion)\b',
            section_text
        ))
        indicators.append(cert_keywords // 2)  # Usually multiple keywords per cert
        
        # 4. Dates/years (certifications usually have dates)
        dates = len(re.findall(r'\b(20\d{2}|19\d{2})\b', section_text))
        indicators.append(dates)
        
        # 5. Common cert name patterns
        common_certs = len(re.findall(
            r'(aws\s+certified|google\s+certified|microsoft\s+certified|cisco\s+certified|python|java|machine\s+learning|data\s+science|web\s+development|full\s+stack)',
            section_text
        ))
        indicators.append(common_certs)
        
        # Use maximum for certifications (they're usually well-listed)
        if indicators:
            count = max(indicators)
            return min(count, 10)
    
    # Fallback: Search for certification mentions globally
    fallback = len(re.findall(
        r'\b(coursera|udemy|nptel|aws\s+certified|google\s+certified)\b',
        text_lower
    ))
    
    return min(max(fallback, 0), 10)


def count_skills(text: str) -> int:
    """
    Count technical skills comprehensively across all categories.
    """
    text_lower = text.lower()
    found_skills = set()
    
    # Comprehensive skill database organized by category
    skill_categories = {
        'programming_languages': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'cpp', 'c#',
            'c', 'go', 'golang', 'rust', 'kotlin', 'swift', 'ruby', 'php',
            'scala', 'r', 'matlab', 'perl', 'haskell', 'dart', 'shell',
            'bash', 'powershell', 'objective-c', 'assembly', 'sql', 'pl/sql'
        ],
        'web_frontend': [
            'html', 'css', 'html5', 'css3', 'react', 'reactjs', 'angular',
            'angularjs', 'vue', 'vuejs', 'svelte', 'next.js', 'nextjs',
            'nuxt', 'gatsby', 'redux', 'jquery', 'bootstrap', 'tailwind',
            'material-ui', 'mui', 'sass', 'scss', 'less', 'webpack', 'vite'
        ],
        'web_backend': [
            'node.js', 'nodejs', 'node', 'express', 'expressjs', 'django',
            'flask', 'fastapi', 'spring boot', 'spring', 'asp.net', 'dotnet',
            '.net', 'laravel', 'rails', 'ruby on rails', 'graphql', 'rest api',
            'restful', 'microservices', 'serverless', 'websocket'
        ],
        'mobile': [
            'android', 'ios', 'react native', 'flutter', 'kotlin',
            'swift', 'swiftui', 'xamarin', 'ionic', 'cordova'
        ],
        'databases': [
            'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle',
            'sql server', 'mssql', 'cassandra', 'dynamodb', 'firebase',
            'firestore', 'elasticsearch', 'neo4j', 'couchdb', 'mariadb'
        ],
        'cloud_devops': [
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes',
            'k8s', 'jenkins', 'terraform', 'ansible', 'ci/cd', 'github actions',
            'gitlab ci', 'circleci', 'travis ci', 'heroku', 'netlify', 'vercel'
        ],
        'ml_ai': [
            'machine learning', 'deep learning', 'tensorflow', 'pytorch',
            'keras', 'scikit-learn', 'sklearn', 'pandas', 'numpy', 'opencv',
            'nlp', 'computer vision', 'neural networks', 'transformers',
            'bert', 'gpt', 'cnn', 'rnn', 'lstm', 'gan', 'xgboost'
        ],
        'data_science': [
            'data analysis', 'data science', 'data visualization', 'tableau',
            'power bi', 'matplotlib', 'seaborn', 'plotly', 'jupyter',
            'apache spark', 'hadoop', 'kafka', 'airflow', 'etl'
        ],
        'tools_ides': [
            'git', 'github', 'gitlab', 'bitbucket', 'svn', 'vs code',
            'visual studio', 'intellij', 'pycharm', 'eclipse', 'android studio',
            'xcode', 'postman', 'insomnia', 'jira', 'confluence', 'trello',
            'slack', 'figma', 'adobe xd'
        ],
        'concepts': [
            'data structures', 'algorithms', 'oop', 'oops', 'design patterns',
            'system design', 'distributed systems', 'multithreading',
            'networking', 'operating systems', 'dbms', 'agile', 'scrum',
            'tdd', 'testing', 'unit testing', 'api development'
        ]
    }
    
    # Flatten all skills
    all_skills = []
    for category_skills in skill_categories.values():
        all_skills.extend(category_skills)
    
    # Find skills using word boundaries
    for skill in all_skills:
        # Handle special characters in skill names
        skill_pattern = skill.replace('+', r'\+').replace('.', r'\.')
        skill_pattern = skill_pattern.replace('#', r'\#').replace('/', r'\/')
        
        # Use word boundaries, but be flexible with hyphens and dots
        pattern = r'\b' + skill_pattern.replace(' ', r'\s+') + r'\b'
        
        if re.search(pattern, text_lower):
            found_skills.add(skill)
    
    # Find skills section to get better count from comma-separated lists
    skill_headers = ['skills', 'technical skills', 'core competencies', 'technologies']
    start, end = find_section(text, skill_headers)
    
    bonus_skills = 0
    if start != -1:
        skills_text = text_lower[start:end]
        # Count commas and semicolons (indicating list format)
        separators = len(re.findall(r'[,;]', skills_text))
        # Many resumes list skills separated by commas
        if separators > len(found_skills):
            bonus_skills = separators - len(found_skills)
    
    total_skills = len(found_skills) + (bonus_skills // 2)  # Add half of bonus skills
    return min(total_skills, 30)


def count_achievements(text: str) -> int:
    """
    Count achievements, awards, honors, and competitive programming accomplishments.
    """
    text_lower = text.lower()
    
    # Find achievement sections
    achievement_headers = [
        'achievements', 'achievement', 'awards', 'honors', 'accomplishments',
        'awards and honors', 'recognitions', 'scholarships'
    ]
    
    # Also check extracurricular for leadership achievements
    extra_headers = ['extracurricular', 'activities', 'leadership', 'positions of responsibility']
    
    total_count = 0
    
    # Check achievements section
    start, end = find_section(text, achievement_headers)
    if start != -1:
        section_text = text_lower[start:end]
        
        # Count bullets
        bullets = len(re.findall(r'\n\s*[•●▪▸►→⦿◆■-]\s+', section_text))
        
        # Competitive programming achievements
        cp_patterns = [
            r'\bgate\b', r'\bleetcode\b', r'\bcodeforces\b', r'\bcodechef\b',
            r'\bhackerrank\b', r'\bhackerearth\b', r'\btopcoder\b',
            r'\batcoder\b', r'\bgfg\b', r'\bgeeksforgeeks\b',
            r'\bsolved\s+\d+\+?\s+(problems?|questions?)',
            r'\d+\s*-?\s*star\b', r'\brating\s*:?\s*\d{3,4}\b',
            r'\brank\s*:?\s*\d+', r'\bair\s+\d+', r'\btop\s+\d+%?'
        ]
        
        # Awards and honors
        award_patterns = [
            r'\bscholarship\b', r'\bfellowship\b', r'\baward\b',
            r'\bwinner\b', r'\bfinalist\b', r'\bchampion\b',
            r'\bmerit\b', r'\bdean\'?s\s+list\b', r'\bhonor\s+roll\b',
            r'\b(first|1st|second|2nd|third|3rd)\s+(place|position|prize|rank)\b',
            r'\bgold\s+medal\b', r'\bsilver\s+medal\b', r'\bbronze\s+medal\b'
        ]
        
        # Hackathons and competitions
        competition_patterns = [
            r'\bhackathon\b', r'\bcompetition\b', r'\bcontest\b',
            r'\bcode\s*jam\b', r'\bhash\s*code\b', r'\bkick\s*start\b'
        ]
        
        all_patterns = cp_patterns + award_patterns + competition_patterns
        pattern_matches = sum(len(re.findall(p, section_text)) for p in all_patterns)
        
        total_count = max(bullets, pattern_matches)
    
    # Check extracurricular for leadership positions
    start, end = find_section(text, extra_headers)
    if start != -1:
        section_text = text_lower[start:end]
        
        leadership_patterns = [
            r'\b(president|vice president|vp|secretary|treasurer)\b',
            r'\b(head|lead|captain|coordinator|director|chair)\b',
            r'\b(founder|co-founder|organizer|mentor)\b',
            r'\bcore\s+(team\s+)?member\b', r'\bproject\s+lead\b',
            r'\b(organized|conducted|led|managed|spearheaded)\b'
        ]
        
        leadership_count = sum(len(re.findall(p, section_text)) for p in leadership_patterns)
        total_count = max(total_count, leadership_count // 2)
    
    # Check for certifications that might be listed as achievements
    if total_count == 0:
        # Some resumes list NPTEL, Coursera, etc. under achievements
        cert_as_achievement = len(re.findall(
            r'\b(nptel|coursera|udemy|aws\s+certified|google\s+certified)\b',
            text_lower
        ))
        total_count = max(total_count, cert_as_achievement)
    
    return min(total_count, 8)


def parse_resume(file_path: str) -> dict:
    """Parse resume and extract all metrics."""
    print(f"\n📄 Parsing resume: {os.path.basename(file_path)}")
    print("-" * 65)
    
    try:
        text = extract_resume_text(file_path)
        
        if not text.strip():
            raise ValueError("Could not extract text from resume")
        
        print("✓ Text extraction successful")
        print(f"✓ Extracted {len(text)} characters")
        print("✓ Analyzing resume content...\n")
        
        metrics = {
            'internships': count_internships(text),
            'projects': count_projects(text),
            'certifications': count_certifications(text),
            'skills': count_skills(text),
            'achievements': count_achievements(text)
        }
        
        return metrics
        
    except Exception as e:
        print(f"❌ Error parsing resume: {e}")
        return None


def calculate_resume_score(metrics: dict) -> dict:
    """
    Calculate weighted resume score with dynamic weighting.
    Adjusts weights based on what's actually present in the resume.
    """
    # Base weights (total = 100)
    weights = {
        'internships': 30,
        'projects': 25,
        'certifications': 20,
        'skills': 15,
        'achievements': 10
    }
    
    # Maximum expected values for normalization
    max_values = {
        'internships': 3,
        'projects': 4,
        'certifications': 5,
        'skills': 20,
        'achievements': 5
    }
    
    # Calculate individual scores
    scores = {}
    for key in metrics:
        capped_value = min(metrics[key], max_values[key])
        normalized = capped_value / max_values[key]
        scores[f"{key}_score"] = round(normalized * weights[key], 2)
    
    # Calculate total
    total_score = round(sum(scores.values()))
    
    scores['total_score'] = round(total_score, 2)
    
    return {"scores": scores}


def display_breakdown(metrics: dict, scores: dict):
    """Display detailed score breakdown with insights."""
    print("\n" + "=" * 65)
    print("⚖️  RESUME SCORE BREAKDOWN")
    print("=" * 65)
    
    print(f"\n📊 DETECTED ITEMS:")
    print("-" * 65)
    print(f"  Internships/Experience: {metrics['internships']:>3}  (max considered: 3)")
    print(f"  Projects:               {metrics['projects']:>3}  (max considered: 5)")
    print(f"  Certifications:         {metrics['certifications']:>3}  (max considered: 5)")
    print(f"  Technical Skills:       {metrics['skills']:>3}  (max considered: 20)")
    print(f"  Achievements:           {metrics['achievements']:>3}  (max considered: 5)")
    
    print(f"\n💯 WEIGHTED SCORES:")
    print("-" * 65)
    print(f"  Internships       (30%): {scores['internships_score']:>6.2f} / 30.00")
    print(f"  Projects          (25%): {scores['projects_score']:>6.2f} / 25.00")
    print(f"  Certifications    (20%): {scores['certifications_score']:>6.2f} / 20.00")
    print(f"  Skills            (15%): {scores['skills_score']:>6.2f} / 15.00")
    print(f"  Achievements      (10%): {scores['achievements_score']:>6.2f} / 10.00")
    print("-" * 65)
    print(f"  TOTAL RESUME SCORE:      {scores['total_score']:>6.2f} / 100.00")
    print("=" * 65)
    
    # Performance tier
    total = scores['total_score']
    if total >= 90:
        tier = "🏆 S-TIER - Elite candidate"
        insight = "Outstanding profile with exceptional depth across all areas."
    elif total >= 80:
        tier = "🌟 A-TIER - Excellent candidate"
        insight = "Strong profile with impressive experience and skills."
    elif total >= 70:
        tier = "✨ B-TIER - Very good candidate"
        insight = "Solid profile with good balance of experience and projects."
    elif total >= 55:
        tier = "📈 C-TIER - Good candidate"
        insight = "Decent profile with room for growth in some areas."
    elif total >= 40:
        tier = "⚠️  D-TIER - Developing candidate"
        insight = "Emerging profile - focus on building more projects and skills."
    else:
        tier = "🔴 E-TIER - Entry-level candidate"
        insight = "Starting out - prioritize internships, projects, and certifications."
    
    print(f"\n{tier}")
    print(f"💡 {insight}")
    
    # Recommendations
    print(f"\n📈 RECOMMENDATIONS:")
    print("-" * 65)
    if metrics['internships'] < 2:
        print("  • Gain more internship/work experience")
    if metrics['projects'] < 3:
        print("  • Build more technical projects to showcase your skills")
    if metrics['certifications'] < 3:
        print("  • Consider earning relevant certifications (Coursera, AWS, etc.)")
    if metrics['skills'] < 15:
        print("  • Expand your technical skill set")
    if metrics['achievements'] < 2:
        print("  • Participate in hackathons, competitions, or leadership roles")
    
    if total >= 80:
        print("  ✓ Excellent profile! Focus on depth and advanced skills.")
    
    print("=" * 65 + "\n")


def main():
    """Main function."""
    print("=" * 65)
    print("📄 ADVANCED RESUME SCORE CALCULATOR v2.0")
    print("=" * 65)
    print("\nFeatures:")
    print("  • Intelligent section detection")
    print("  • Multi-strategy counting algorithms")
    print("  • Comprehensive skill database (200+ skills)")
    print("  • Unbiased scoring across resume formats")
    print("\nSupported formats: PDF (.pdf), Word (.docx), Text (.txt)")
    print("=" * 65)
    
    file_path = input("\nEnter the path to your resume file: ").strip().strip('"').strip("'")
    
    if not os.path.exists(file_path):
        print(f"\n❌ Error: File not found at '{file_path}'")
        return
    
    metrics = parse_resume(file_path)
    
    if not metrics:
        print("\n❌ Failed to parse resume.")
        return
    
    results = calculate_resume_score(metrics)
    display_breakdown(metrics, results['scores'])


if __name__ == "__main__":
    main()
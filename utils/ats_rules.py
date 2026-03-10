import re
from typing import List, Dict

def check_ats_compliance(resume_text: str) -> List[Dict]:
    """
    Check resume against common ATS rules
    """
    issues = []
    
    # Check 1: File format issues (simulated)
    if len(resume_text.split()) > 1000:
        issues.append({
            'type': 'warning',
            'message': 'Resume might be too long (>1000 words)',
            'suggestion': 'Keep resume to 1-2 pages maximum'
        })
    
    # Check 2: Contact information
    if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text):
        issues.append({
            'type': 'critical',
            'message': 'Email address not found',
            'suggestion': 'Add a professional email address'
        })
    
    # Check 3: Section headers
    if not re.search(r'^(?:[A-Z][A-Z\s]+)$', resume_text, re.MULTILINE):
        issues.append({
            'type': 'warning',
            'message': 'Section headers may not be clear',
            'suggestion': 'Use ALL CAPS or bold for section headers'
        })
    
    # Check 4: Tables
    if resume_text.count('\t') > 10:
        issues.append({
            'type': 'critical',
            'message': 'Tables detected',
            'suggestion': 'ATS systems may not parse tables correctly. Remove tables.'
        })
    
    # Check 5: Bullet points
    if not any(char in resume_text for char in ['•', '·', '-']):
        issues.append({
            'type': 'warning',
            'message': 'No bullet points detected',
            'suggestion': 'Use bullet points for better readability'
        })
    
    # Check 6: Keywords in context
    if len(resume_text.split()) < 200:
        issues.append({
            'type': 'warning',
            'message': 'Resume might be too short',
            'suggestion': 'Add more details and achievements'
        })
    
    # Check 7: Font issues (simulated)
    unusual_chars = re.findall(r'[^\x00-\x7F]', resume_text)
    if len(unusual_chars) > 10:
        issues.append({
            'type': 'warning',
            'message': 'Unusual characters detected',
            'suggestion': 'Use standard fonts (Arial, Calibri, Times New Roman)'
        })
    
    # Check 8: Skills section
    if not re.search(r'(?:skills|technical skills|competencies)', resume_text, re.IGNORECASE):
        issues.append({
            'type': 'medium',
            'message': 'No dedicated skills section',
            'suggestion': 'Add a skills section with relevant keywords'
        })
    
    return issues

def get_ats_tips() -> List[str]:
    """
    Get general ATS tips
    """
    return [
        "Use standard section headers: SUMMARY, EXPERIENCE, EDUCATION, SKILLS",
        "Include keywords from the job description",
        "Use bullet points instead of paragraphs",
        "Avoid tables, columns, and graphics",
        "Save as PDF for best compatibility",
        "Include contact information at the top",
        "Use reverse chronological order",
        "Quantify achievements with numbers"
    ]
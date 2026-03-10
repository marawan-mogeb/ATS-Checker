import numpy as np
import re
import pickle
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from typing import List, Dict, Tuple, Set
import json
import os

# Try to load spaCy model, fallback to simpler processing
try:
    nlp = spacy.load('en_core_web_sm')
    SPACY_AVAILABLE = True
except:
    SPACY_AVAILABLE = False
    print("spaCy model not found. Using simpler NLP processing.")

class ResumeEnhancer:
    def __init__(self, model_path=None):
        # Comprehensive list of generic words to ignore
        self.generic_words: Set[str] = {
            # Generic verbs and actions
            'learn', 'learning', 'working', 'work', 'related', 'skills', 'skill',
            'knowledge', 'know', 'degree', 'experience', 'experienced', 'development',
            'develop', 'developer', 'engineer', 'engineers', 'computer', 'preprocessing',
            'processing', 'process', 'methods', 'methodology', 'methodologies',
            'project', 'projects', 'research', 'researching', 'professional',
            'meetings', 'meeting', 'findings', 'find', 'present', 'presenting',
            'documenting', 'document', 'processes', 'new', 'good', 'better',
            'best', 'excellent', 'strong', 'proficient', 'familiar', 'basic',
            'advanced', 'intermediate', 'junior', 'senior', 'lead', 'leading',
            'team', 'collaboration', 'collaborative', 'communication', 'problem',
            'solving', 'analytical', 'analysis', 'analyst', 'ability', 'abilities',
            'capable', 'capability', 'responsible', 'responsibility', 'duties',
            'role', 'position', 'job', 'career', 'field', 'industry', 'sector',
            
            # Common resume filler words
            'extensive', 'comprehensive', 'proven', 'successful', 'effective',
            'efficient', 'innovative', 'creative', 'strategic', 'technical',
            'various', 'multiple', 'several', 'different', 'diverse',
            'including', 'etc', 'etcetera', 'share', 'maintain',
            
            # Common job description filler words
            'trends', 'key', 'responsibilities', 'responsibility', 'exploratory',
            'creating', 'developing', 'cleaning', 'tools', 'like', 'science',
            'requirements', 'requirements', 'maintain', 'support', 'provide',
            'ensure', 'contribute', 'participate', 'involve', 'manage',
            
            # Education-related
            'education', 'educational', 'academic', 'university', 'college',
            'school', 'studies', 'course', 'courses', 'training', 'certification',
            
            # Time-related
            'years', 'year', 'months', 'month', 'daily', 'weekly', 'monthly',
            'annual', 'annually', 'current', 'previous', 'prior', 'former',
            
            # Business jargon
            'business', 'company', 'organization', 'corporate', 'enterprise',
            'stakeholder', 'stakeholders', 'client', 'clients', 'customer',
            'customers', 'vendor', 'vendors', 'partner', 'partners', 'team',
            'department', 'division', 'group', 'unit'
        }
        
        # Industry-specific keyword databases with priority levels
        self.industry_keywords: Dict[str, List[str]] = {
            'software': [
                # High priority
                'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
                'node.js', 'django', 'flask', 'spring', 'aws', 'azure', 'gcp',
                'docker', 'kubernetes', 'devops', 'ci/cd', 'microservices',
                
                # Medium priority
                'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis',
                'rest', 'api', 'graphql', 'git', 'github', 'gitlab',
                'jenkins', 'terraform', 'ansible', 'agile', 'scrum',
                
                # Technical concepts
                'data structures', 'algorithms', 'machine learning', 'ai',
                'object-oriented', 'design patterns', 'test-driven development'
            ],
            'data_science': [
                # Programming & Tools
                'python', 'r', 'sql', 'pandas', 'numpy', 'tensorflow', 'pytorch',
                'scikit-learn', 'keras', 'spark', 'hadoop', 'tableau', 'power bi',
                
                # ML/AI Techniques
                'machine learning', 'deep learning', 'neural networks', 'nlp',
                'natural language processing', 'computer vision', 'time series',
                'predictive modeling', 'statistical analysis', 'regression',
                'classification', 'clustering', 'reinforcement learning',
                
                # Data Engineering
                'data pipeline', 'etl', 'data warehousing', 'big data',
                'data visualization', 'feature engineering', 'model deployment',
                'mlops', 'a/b testing', 'experimentation'
            ],
            'marketing': [
                # Digital Marketing
                'seo', 'search engine optimization', 'sem', 'ppc', 'google ads',
                'facebook ads', 'social media marketing', 'content marketing',
                'email marketing', 'influencer marketing', 'affiliate marketing',
                
                # Analytics & Tools
                'google analytics', 'google tag manager', 'crm', 'hubspot',
                'marketo', 'salesforce', 'adobe analytics',
                
                # Strategy
                'brand strategy', 'market research', 'competitive analysis',
                'customer segmentation', 'conversion rate optimization',
                'roi analysis', 'kpi tracking', 'campaign management'
            ],
            'finance': [
                # Financial Analysis
                'financial modeling', 'valuation', 'forecasting', 'budgeting',
                'financial analysis', 'investment analysis', 'risk management',
                
                # Tools & Software
                'excel', 'vba', 'python', 'sql', 'bloomberg', 'reuters',
                'quickbooks', 'sap', 'oracle',
                
                # Compliance & Reporting
                'gaap', 'ifrs', 'sox compliance', 'audit', 'internal controls',
                'financial reporting', 'regulatory compliance',
                
                # Specializations
                'corporate finance', 'investment banking', 'private equity',
                'venture capital', 'portfolio management', 'derivatives'
            ],
            'general': [
                'leadership', 'project management', 'team management',
                'problem solving', 'communication skills', 'strategic planning',
                'client relations', 'stakeholder management', 'cross-functional',
                'process improvement', 'change management', 'quality assurance'
            ]
        }
        
        # Technical terms that should always be prioritized
        self.technical_terms: Set[str] = {
            'python', 'java', 'javascript', 'react', 'node.js', 'aws', 'docker',
            'kubernetes', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'sql',
            'mongodb', 'tableau', 'power bi', 'spark', 'hadoop', 'scikit-learn',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'data science', 'artificial intelligence', 'devops', 'ci/cd',
            'microservices', 'rest api', 'graphql', 'git', 'agile', 'scrum'
        }
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 3),
            max_features=5000,
            min_df=2,
            max_df=0.8
        )
        
        # Action verbs for resume improvement
        self.action_verbs: List[str] = [
            'developed', 'created', 'implemented', 'designed', 'built',
            'engineered', 'architected', 'programmed', 'coded', 'debugged',
            'tested', 'deployed', 'managed', 'led', 'supervised', 'coordinated',
            'directed', 'oversaw', 'mentored', 'trained', 'optimized',
            'improved', 'enhanced', 'streamlined', 'automated', 'integrated',
            'analyzed', 'researched', 'evaluated', 'assessed', 'identified',
            'solved', 'resolved', 'reduced', 'increased', 'decreased',
            'accelerated', 'expanded', 'generated', 'produced', 'delivered'
        ]
        
        # Initialize with sample data
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize TF-IDF with sample resumes from different industries"""
        sample_resumes = [
            "Experienced software engineer with python java javascript react node.js aws docker kubernetes devops skills",
            "Data scientist with machine learning deep learning tensorflow pytorch pandas numpy sql experience",
            "Marketing professional with seo sem google analytics social media content marketing expertise",
            "Financial analyst with financial modeling valuation forecasting excel vba python sql background",
            "Project manager with agile scrum leadership communication stakeholder management capabilities"
        ]
        self.vectorizer.fit(sample_resumes)
    
    def extract_entities(self, text: str) -> Dict:
        """Extract entities from text using spaCy or regex"""
        if SPACY_AVAILABLE:
            doc = nlp(text)
            entities = {
                'skills': [],
                'organizations': [],
                'dates': [],
                'education': [],
                'certifications': []
            }
            
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PRODUCT']:
                    entities['organizations'].append(ent.text)
                elif ent.label_ == 'DATE':
                    entities['dates'].append(ent.text)
            
            # Extract skills and certifications
            entities['skills'] = self._extract_technical_skills(text)
            entities['certifications'] = self._extract_certifications(text)
            
            return entities
        else:
            # Fallback to regex-based extraction
            return self._extract_entities_regex(text)
    
    def _extract_technical_skills(self, text: str) -> List[str]:
        """Extract technical skills from text with priority"""
        found_skills = []
        text_lower = text.lower()
        
        # Check for high-priority technical terms first
        for skill in self.technical_terms:
            if skill in text_lower:
                found_skills.append(skill)
        
        # Check industry-specific keywords
        for industry, skills in self.industry_keywords.items():
            for skill in skills:
                skill_lower = skill.lower()
                if skill_lower in text_lower and skill_lower not in found_skills:
                    found_skills.append(skill)
        
        return list(set(found_skills))
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from text"""
        cert_patterns = [
            r'([A-Z]+-[0-9]+)',  # AWS-123, AZ-900 style
            r'(AWS Certified [A-Za-z ]+)',
            r'(Microsoft Certified: [A-Za-z ]+)',
            r'(Google [A-Za-z ]+ Certified)',
            r'(PMP|PMI-[A-Z]+)',
            r'(CFA|CPA|FRM)',
            r'(Scrum Master|Product Owner)'
        ]
        
        certifications = []
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend(matches)
        
        return list(set(certifications))
    
    def _extract_entities_regex(self, text: str) -> Dict:
        """Fallback entity extraction using regex"""
        entities = {
            'skills': self._extract_technical_skills(text),
            'organizations': re.findall(r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b(?!\s+(?:Inc|Ltd|LLC|Corp))', text)[:10],
            'dates': re.findall(r'\b(?:20\d{2}|19\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b', text, re.IGNORECASE),
            'education': re.findall(r'\b(?:B\.?[AS]\.?|M\.?[AS]\.?|Ph\.?D\.?|MBA|MS|BS|BA|Bachelor|Master|Doctorate)\b', text, re.IGNORECASE),
            'certifications': self._extract_certifications(text)
        }
        return entities
    
    def get_ats_score(self, resume_text: str, job_description: str) -> Tuple[float, Dict]:
        """Calculate ATS compatibility score with improved keyword analysis"""
        # Clean texts
        resume_clean = self._clean_text(resume_text)
        job_clean = self._clean_text(job_description)
        
        # Vectorize
        vectors = self.vectorizer.transform([resume_clean, job_clean])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        # Extract meaningful keywords
        resume_keywords = set(self._extract_meaningful_keywords(resume_clean))
        job_keywords = set(self._extract_meaningful_keywords(job_clean))
        
        # Find matches - prioritize technical terms
        matches = []
        priority_matches = []
        
        for job_keyword in job_keywords:
            if job_keyword in resume_keywords:
                matches.append(job_keyword)
                if job_keyword in self.technical_terms:
                    priority_matches.append(job_keyword)
        
        # Find missing keywords
        missing_keywords = list(job_keywords - resume_keywords)
        
        # Calculate weighted score
        base_score = similarity * 100
        
        if job_keywords:
            # Keyword coverage with technical term bonus
            coverage = len(matches) / len(job_keywords)
            technical_bonus = len(priority_matches) * 2  # Extra weight for technical terms
            
            # Industry keyword bonus
            industry_bonus = self._calculate_industry_bonus(resume_text, job_description)
            
            final_score = (
                base_score * 0.4 +  # Base similarity
                coverage * 100 * 0.4 +  # Keyword coverage
                technical_bonus * 0.1 +  # Technical term bonus
                industry_bonus * 0.1  # Industry relevance bonus
            )
        else:
            final_score = base_score
        
        # Cap score at 100
        final_score = min(final_score, 100)
        
        analysis = {
            'keyword_matches': matches[:20],
            'priority_matches': priority_matches[:10],
            'missing_keywords': self._filter_generic_words(missing_keywords)[:20],
            'keyword_coverage': f"{(len(matches)/len(job_keywords)*100):.1f}%" if job_keywords else "0%",
            'resume_keywords_count': len(resume_keywords),
            'job_keywords_count': len(job_keywords),
            'technical_match_count': len(priority_matches),
            'similarity_score': round(similarity * 100, 1)
        }
        
        return round(final_score, 1), analysis
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        text = text.lower()
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        # Remove phone numbers
        text = re.sub(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '', text)
        # Remove special characters but keep meaningful punctuation
        text = re.sub(r'[^\w\s.,;:!?-]', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove numbers that aren't part of versions (like Python 3.8)
        text = re.sub(r'\b\d+\b', '', text)
        
        return text.strip()
    
    def _extract_meaningful_keywords(self, text: str, top_n: int = 50) -> List[str]:
        """Extract meaningful keywords, filtering out generic words"""
        # Clean text first
        text = self._clean_text(text)
        
        # Extract n-grams (1-3 words)
        words = text.lower().split()
        ngrams = []
        
        # Generate 1-gram, 2-gram, 3-gram
        for n in range(1, 4):
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n]).strip()
                # Remove any trailing punctuation
                ngram = re.sub(r'[,\.:;!\?\)]$', '', ngram).strip()
                
                if (len(ngram) > 3 and  # Filter very short ngrams
                    ngram and  # Not empty
                    not ngram.endswith(':') and  # Not formatting
                    not ngram.endswith(',') and  # Not formatting
                    not any(c in ngram for c in ['(', ')', ',', ':'])):  # No stray punctuation
                    ngrams.append(ngram)
        
        # Count frequency
        ngram_freq = Counter(ngrams)
        
        # Filter out generic ngrams
        meaningful_ngrams = []
        for ngram, freq in ngram_freq.most_common(top_n * 5):
            if (freq >= 2 and  # At least appears twice
                not self._is_generic_ngram(ngram) and  # Not generic
                not any(word.isdigit() for word in ngram.split()) and  # No standalone numbers
                len(ngram) > 4):  # Reasonable length
                meaningful_ngrams.append(ngram)
        
        return meaningful_ngrams[:top_n]
    
    def _is_generic_ngram(self, ngram: str) -> bool:
        """Check if an n-gram is generic"""
        words = ngram.split()
        
        # Check individual words
        for word in words:
            if word in self.generic_words:
                return True
        
        # Check common generic patterns
        generic_patterns = [
            r'^years of experience$',
            r'^strong .* skills$',
            r'^excellent .* skills$',
            r'^ability to .*$',
            r'^team player$',
            r'^hard worker$',
            r'^fast learner$',
            r'^detail oriented$',
            r'^problem solver$'
        ]
        
        ngram_lower = ngram.lower()
        for pattern in generic_patterns:
            if re.match(pattern, ngram_lower):
                return True
        
        return False
    
    def _filter_generic_words(self, keywords: List[str]) -> List[str]:
        """Filter out generic words from keyword list"""
        filtered = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if (not self._is_generic_ngram(keyword_lower) and
                keyword_lower not in self.generic_words and
                len(keyword_lower) > 4):  # Minimum length
                filtered.append(keyword)
        return filtered
    
    def _calculate_industry_bonus(self, resume_text: str, job_description: str) -> float:
        """Calculate industry relevance bonus"""
        # Simple implementation - detect industry from keywords
        industry_scores = {}
        
        for industry, keywords in self.industry_keywords.items():
            if industry == 'general':
                continue
            
            score = 0
            for keyword in keywords[:20]:  # Check top keywords
                if keyword in resume_text.lower() and keyword in job_description.lower():
                    score += 1
            
            industry_scores[industry] = score
        
        # Return the highest industry score
        if industry_scores:
            return min(max(industry_scores.values()) * 2, 10)  # Max 10 bonus points
        return 0
    
    def get_missing_keywords(self, resume_text: str, job_description: str) -> List[str]:
        """Get meaningful missing keywords with prioritization"""
        # Extract meaningful keywords
        resume_keywords = set(self._extract_meaningful_keywords(resume_text))
        job_keywords = set(self._extract_meaningful_keywords(job_description))
        
        # Find missing keywords
        missing = list(job_keywords - resume_keywords)
        
        # Filter out generic words
        missing = self._filter_generic_words(missing)
        
        # Categorize and prioritize
        categorized_keywords = self._categorize_keywords(missing)
        
        # Return combined list with high-priority first
        prioritized = (
            categorized_keywords['technical'] +
            categorized_keywords['industry_specific'] +
            categorized_keywords['soft_skills']
        )
        
        return prioritized[:15]
    
    def _categorize_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Categorize keywords by type"""
        categorized = {
            'technical': [],
            'industry_specific': [],
            'soft_skills': []
        }
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Check if it's a technical term
            is_technical = False
            for tech_term in self.technical_terms:
                if tech_term in keyword_lower or keyword_lower in tech_term:
                    categorized['technical'].append(keyword)
                    is_technical = True
                    break
            
            if is_technical:
                continue
            
            # Check if it's industry-specific
            is_industry = False
            for industry, industry_keywords in self.industry_keywords.items():
                for industry_keyword in industry_keywords:
                    if (industry_keyword in keyword_lower or 
                        keyword_lower in industry_keyword):
                        categorized['industry_specific'].append(keyword)
                        is_industry = True
                        break
                if is_industry:
                    break
            
            if not is_technical and not is_industry:
                # Likely a soft skill or general term
                categorized['soft_skills'].append(keyword)
        
        return categorized
    
    def enhance_resume(self, resume_text: str, job_description: str) -> Dict:
        """Provide comprehensive ML-based enhancement suggestions"""
        score, analysis = self.get_ats_score(resume_text, job_description)
        missing_keywords = self.get_missing_keywords(resume_text, job_description)
        categorized_keywords = self._categorize_keywords(missing_keywords)
        
        suggestions = []
        strengths = []
        weaknesses = []
        
        # Analyze resume structure
        sections = self._analyze_structure(resume_text)
        
        # Section analysis
        required_sections = ['summary', 'experience', 'education', 'skills']
        for section in required_sections:
            if section in sections:
                strengths.append(f"Has '{section.title()}' section")
            else:
                weaknesses.append(f"Missing '{section.title()}' section")
                if section == 'summary':
                    suggestions.append("Add a professional summary at the top")
                elif section == 'skills':
                    suggestions.append("Create a dedicated skills section")
        
        # Keyword analysis
        if analysis['technical_match_count'] < 3:
            weaknesses.append(f"Low technical keyword matches ({analysis['technical_match_count']})")
            suggestions.append("Add more technical keywords from the job description")
        else:
            strengths.append(f"Good technical keyword coverage ({analysis['technical_match_count']} matches)")
        
        # Action verb analysis
        action_verbs_found = self._analyze_action_verbs(resume_text)
        if len(action_verbs_found) < 5:
            weaknesses.append(f"Limited action verbs ({len(action_verbs_found)} found)")
            suggestions.append("Start bullet points with strong action verbs")
        else:
            strengths.append(f"Uses strong action verbs ({len(action_verbs_found)} found)")
        
        # Quantifiable achievements
        if not self._has_quantifiable_achievements(resume_text):
            weaknesses.append("Few quantifiable achievements")
            suggestions.append("Add metrics and numbers to achievements (e.g., 'increased efficiency by 30%')")
        else:
            strengths.append("Contains quantifiable achievements")
        
        # Resume length
        word_count = len(resume_text.split())
        if word_count < 250:
            weaknesses.append(f"Resume too short ({word_count} words)")
            suggestions.append("Add more details about projects and responsibilities")
        elif word_count > 800:
            weaknesses.append(f"Resume too long ({word_count} words)")
            suggestions.append("Consider removing less relevant experience")
        else:
            strengths.append(f"Good resume length ({word_count} words)")
        
        # Add specific keyword suggestions
        if categorized_keywords['technical']:
            suggestions.append(f"Add technical keywords: {', '.join(categorized_keywords['technical'][:3])}")
        
        # Formatting check
        formatting_issues = self._check_formatting(resume_text)
        weaknesses.extend(formatting_issues)
        
        return {
            'compatibility_score': score,
            'suggestions': suggestions[:10],  # Limit to top 10 suggestions
            'strengths': strengths[:8],  # Limit strengths
            'weaknesses': weaknesses[:8],  # Limit weaknesses
            'analysis': analysis,
            'categorized_keywords': categorized_keywords,
            'resume_stats': {
                'word_count': word_count,
                'section_count': len(sections),
                'action_verbs_count': len(action_verbs_found),
                'technical_keywords_count': analysis['technical_match_count']
            }
        }
    
    def _analyze_structure(self, text: str) -> List[str]:
        """Analyze resume structure with better detection"""
        sections = []
        
        # Enhanced section detection patterns
        section_patterns = {
            'summary': r'^(?:SUMMARY|Summary|PROFILE|Profile|OBJECTIVE|Objective|## Summary)[\s:-]*',
            'experience': r'^(?:EXPERIENCE|Experience|WORK EXPERIENCE|Work Experience|EMPLOYMENT|Employment|PROFESSIONAL EXPERIENCE|## Experience)[\s:-]*',
            'education': r'^(?:EDUCATION|Education|ACADEMIC BACKGROUND|Academic Background|## Education)[\s:-]*',
            'skills': r'^(?:SKILLS|Skills|TECHNICAL SKILLS|Technical Skills|TECHNICAL EXPERTISE|Technical Expertise|COMPETENCIES|Competencies|## Technical Skills)[\s:-]*',
            'projects': r'^(?:PROJECTS|Projects|PERSONAL PROJECTS|Personal Projects|PORTFOLIO|Portfolio|## Projects)[\s:-]*',
            'publications': r'^(?:PUBLICATIONS|Publications|RESEARCH|Research|## Publications)[\s:-]*',
            'certifications': r'^(?:CERTIFICATIONS|Certifications|CERTIFICATES|Certificates|TRAINING|Training|## Certifications)[\s:-]*',
            'languages': r'^(?:LANGUAGES|Languages|LANGUAGE PROFICIENCY|## Languages)[\s:-]*',
            'activities': r'^(?:ACTIVITIES|Activities|EXTRACURRICULAR|Extracurricular|LEADERSHIP|Leadership|## Extracurricular Activities)[\s:-]*'
        }
        
        lines = text.split('\n')
        
        print(f"DEBUG: Analyzing {len(lines)} lines")  # Debug log
        
        for i, line in enumerate(lines[:100]):  # Check first 100 lines
            line_clean = line.strip()
            
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line_clean, re.IGNORECASE):
                    print(f"DEBUG: Found section '{section_name}' at line {i}: '{line_clean}'")  # Debug
                    if section_name not in sections:
                        sections.append(section_name)
                    break  # Found a section, move to next line
        
        print(f"DEBUG: Detected sections: {sections}")  # Debug
        return sections
    
    def _analyze_action_verbs(self, text: str) -> List[str]:
        """Analyze action verbs in resume"""
        found_verbs = []
        text_lower = text.lower()
        
        for verb in self.action_verbs:
            # Look for verb at start of bullet points or sentences
            patterns = [
                rf'^\s*[-•*]\s*{verb}[a-z]*\s+',  # Bullet points
                rf'\b{verb}[a-z]*\s+',  # Anywhere in text
            ]
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.MULTILINE):
                    found_verbs.append(verb)
                    break
        
        return list(set(found_verbs))
    
    def _has_quantifiable_achievements(self, text: str) -> bool:
        """Check if resume has quantifiable achievements"""
        quantifiable_patterns = [
            # Percentages
            r'\b\d+\s*%\b',
            r'\bincreased\s+by\s+\d+',
            r'\breduced\s+by\s+\d+',
            r'\bimproved\s+by\s+\d+',
            r'\bdecreased\s+by\s+\d+',
            
            # Dollar amounts
            r'\$\d+(?:,\d+)*(?:\.\d+)?',
            r'\bsaved\s+\$\d+',
            r'\bgenerated\s+\$\d+',
            r'\bincreased\s+revenue\s+by\s+\$\d+',
            
            # Multipliers
            r'\d+\s*x\b',
            r'\d+\s*times\b',
            
            # Specific numbers
            r'\bmanaged\s+\d+\s+people\b',
            r'\bled\s+a\s+team\s+of\s+\d+\b',
            r'\boversaw\s+\$\d+\s+budget\b',
            r'\bhandled\s+\d+\s+clients\b'
        ]
        
        for pattern in quantifiable_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _check_formatting(self, text: str) -> List[str]:
        """Check for formatting issues"""
        issues = []
        
        # Check for tables (multiple tabs)
        if text.count('\t') > 10:
            issues.append("Avoid tabs - use spaces or bullet points instead")
        
        # Check for consistent bullet points
        bullet_types = text.count('•') + text.count('*') + text.count('-')
        if bullet_types == 0:
            issues.append("Consider using bullet points for better readability")
        
        # Check for appropriate line length
        lines = text.split('\n')
        long_lines = sum(1 for line in lines if len(line.strip()) > 100)
        if long_lines > 5:
            issues.append("Some lines are too long - break into shorter bullet points")
        
        # Check for contact info
        if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text):
            issues.append("Add email address for contact information")
        
        # Check for consistent tense
        present_tense = len(re.findall(r'\b(?:am|is|are|develop|manage|lead)\b', text, re.IGNORECASE))
        past_tense = len(re.findall(r'\b(?:was|were|developed|managed|led)\b', text, re.IGNORECASE))
        
        if present_tense > 0 and past_tense > 0:
            # Mixed tense is common in resumes (current job present, past jobs past)
            # Only flag if it's excessive
            if abs(present_tense - past_tense) > 10:
                issues.append("Check for consistent verb tense usage")
        
        return issues
    
    def generate_enhanced_resume(self, resume_text: str, job_description: str) -> str:
        """Generate enhanced resume version with ML suggestions"""
        # Get enhancement suggestions
        enhancement = self.enhance_resume(resume_text, job_description)
        missing_keywords = self.get_missing_keywords(resume_text, job_description)
        
        # Start with original resume
        enhanced_lines = resume_text.split('\n')
        
        # Add missing keywords to skills section if it exists
        skills_added = False
        for i, line in enumerate(enhanced_lines):
            line_lower = line.lower()
            if any(skill_section in line_lower for skill_section in ['skills', 'technical skills']):
                # Add missing technical keywords
                technical_keywords = missing_keywords[:5]  # Top 5
                if technical_keywords:
                    enhanced_lines[i] = line.rstrip() + ' | ' + ' | '.join(technical_keywords)
                    skills_added = True
                    break
        
        # If no skills section found, add one
        if not skills_added and missing_keywords:
            # Find a good place to insert skills section (after summary/objective, before experience)
            insert_index = 0
            for i, line in enumerate(enhanced_lines):
                if any(section in line.lower() for section in ['experience', 'work history', 'employment']):
                    insert_index = i
                    break
                elif any(section in line.lower() for section in ['education']):
                    insert_index = i
                    break
            
            skills_section = "SKILLS\n" + " | ".join(missing_keywords[:8])
            enhanced_lines.insert(insert_index, skills_section)
        
        # Add summary if missing and we have keywords
        if 'summary' not in resume_text.lower() and 'objective' not in resume_text.lower():
            summary = "SUMMARY\n"
            # Create a summary based on job description keywords
            job_keywords = self._extract_meaningful_keywords(job_description)[:5]
            if job_keywords:
                summary += f"Experienced professional with expertise in {', '.join(job_keywords[:3])}."
            else:
                summary += "Results-driven professional seeking new opportunities."
            
            enhanced_lines.insert(0, summary + "\n")
        
        # Ensure action verbs at start of bullet points
        for i, line in enumerate(enhanced_lines):
            line_stripped = line.strip()
            if line_stripped.startswith(('-', '•', '*', '·')):
                # Check if line starts with an action verb
                first_word = line_stripped[1:].strip().split()[0].lower().rstrip('s')
                if first_word not in self.action_verbs:
                    # Find an appropriate action verb
                    for verb in self.action_verbs:
                        if verb in line_stripped.lower():
                            # Replace first word with action verb
                            words = line_stripped.split()
                            if len(words) > 1:
                                words[1] = verb.capitalize()
                                enhanced_lines[i] = ' '.join(words)
                            break
        
        return '\n'.join(enhanced_lines)
    
    def get_industry_keywords(self, industry: str) -> List[str]:
        """Get industry-specific keywords"""
        return self.industry_keywords.get(industry, self.industry_keywords['general'])
    
    def get_detailed_suggestions(self, resume_text: str, job_description: str) -> List[Dict]:
        """Get detailed suggestions categorized by priority and impact"""
        enhancement = self.enhance_resume(resume_text, job_description)
        missing_keywords = self.get_missing_keywords(resume_text, job_description)
        
        suggestions = []
        
        # High priority suggestions
        if enhancement['resume_stats']['technical_keywords_count'] < 3:
            suggestions.append({
                'priority': 'high',
                'category': 'keywords',
                'suggestion': 'Add more technical keywords from job description',
                'impact': 'Significant impact on ATS score',
                'action': 'Review job description and add 3-5 technical terms'
            })
        
        if not enhancement['resume_stats']['action_verbs_count']:
            suggestions.append({
                'priority': 'high',
                'category': 'writing',
                'suggestion': 'Start bullet points with strong action verbs',
                'impact': 'Makes accomplishments more impactful',
                'action': 'Use verbs like Developed, Created, Implemented, Managed'
            })
        
        # Medium priority suggestions
        if missing_keywords:
            suggestions.append({
                'priority': 'medium',
                'category': 'keywords',
                'suggestion': f"Incorporate missing keywords: {', '.join(missing_keywords[:5])}",
                'impact': 'Improves keyword matching',
                'action': 'Add these keywords to skills and experience sections'
            })
        
        if 'summary' not in resume_text.lower():
            suggestions.append({
                'priority': 'medium',
                'category': 'structure',
                'suggestion': 'Add a professional summary section',
                'impact': 'Helps ATS understand your profile quickly',
                'action': 'Add 2-3 sentence summary at the top'
            })
        
        # Low priority suggestions
        formatting_issues = self._check_formatting(resume_text)
        for issue in formatting_issues[:2]:
            suggestions.append({
                'priority': 'low',
                'category': 'formatting',
                'suggestion': issue,
                'impact': 'Improves readability and ATS parsing',
                'action': 'Check formatting guidelines'
            })
        
        return suggestions

# Global function for backward compatibility
def get_ats_score(resume_text: str, job_description: str) -> Tuple[float, Dict]:
    enhancer = ResumeEnhancer()
    return enhancer.get_ats_score(resume_text, job_description)
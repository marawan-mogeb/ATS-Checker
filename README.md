# ATS Resume Analyzer with ML

🤖 **ML-powered resume optimization for Applicant Tracking Systems**

An intelligent web application that analyzes your resume against job descriptions using Machine Learning and Natural Language Processing. Get comprehensive feedback on ATS compatibility, keyword matching, and actionable suggestions to improve your resume.

---

## ✨ Features

- **Resume Analysis**: Upload PDF resumes or paste text directly
- **Keyword Matching**: Identify matched and missing keywords from job descriptions
- **ATS Compliance Check**: Validate resume against ATS system rules
- **Overall Score**: Combined metric (60% ATS + 40% ML compatibility)
- **ML-Powered Suggestions**: AI-driven recommendations for improvements
- **Resume Enhancement**: Generate optimized resume versions
- **Industry Keywords**: Tailored keyword suggestions by industry
  - Software & IT
  - Data Science & Analytics
  - Marketing & Sales
  - Finance & Accounting

---

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**
- **Flask 2.3.3** - Web framework
- **scikit-learn 1.3.0** - ML algorithms
- **spaCy 3.6.1** - NLP processing
- **PyMuPDF (fitz) 1.23.4** - PDF extraction
- **pdfplumber 0.10.3** - Advanced PDF parsing

### Frontend
- **HTML5**
- **CSS3** (with gradient designs and animations)
- **JavaScript (ES6+)**
- **Font Awesome 6.4.0** - Icons
- **Google Fonts (Poppins)**

### PDF Processing
- Multiple PDF extraction methods (PyMuPDF, pdfplumber, PyPDF2)
- OCR support with pytesseract
- Fallback mechanisms for robust text extraction

---

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- 4GB RAM (minimum)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Optional
- Tesseract OCR (for image-based PDF extraction)

---

## 🚀 Installation

### 1. Clone or Download Project
```bash
cd .\ATS
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

The app will be available at `http://localhost:5000`

---

## 📂 Project Structure

```
ATS/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
│
├── utils/
│   ├── pdf_parser.py              # PDF text extraction
│   ├── ml_processor.py            # ML analysis & keyword extraction
│   └── ats_rules.py               # ATS compliance checks
│
├── templates/
│   └── index.html                 # Frontend UI
│
├── static/
│   ├── css/
│   │   └── style.css              # Styling
│   └── js/
│       └── script.js              # Frontend logic
│
├── uploads/                        # Temporary resume uploads
└── README.md                       # This file
```

---

## 📖 Usage Guide

### 1. **Analyze Resume**

#### Option A: PDF Upload
1. Paste the job description in the "Job Description" textarea
2. Click "Upload Your Resume" or drag & drop a PDF
3. Click "Analyze Resume" button

#### Option B: Text Input
1. Paste job description
2. Paste your resume text directly
3. Click "Analyze Resume"

### 2. **View Results**

The analysis displays:
- **Overall Score** (0-100): Composite metric
- **ATS Score**: Percentage match for ATS systems
- **ML Compatibility**: AI-based relevance score
- **Keyword Coverage**: % of matched keywords

### 3. **Tabs Overview**

#### Keywords Tab
- **Matched Keywords** (green): Keywords found in both resume and job description
- **Missing Keywords** (yellow): Relevant keywords to add to your resume

#### Suggestions Tab
- **ML-Powered Suggestions**: Specific improvements recommended
- **Strengths**: What your resume does well
- **Weaknesses**: Areas that need improvement

#### Compliance Tab
- ATS system compatibility issues
- Critical, warning, and informational alerts
- Best practices for ATS optimization

#### Enhance Tab
- Generate an AI-enhanced version of your resume
- Automatic keyword injection
- Improved formatting suggestions

---

## 🔌 API Endpoints

### `POST /analyze`
Analyze resume via PDF file upload
```json
Request:
{
  "job_description": "Your job description",
  "resume": <PDF file>
}

Response:
{
  "success": true,
  "overall_score": 75.5,
  "ats_score": 78.0,
  "ml_compatibility_score": 72.0,
  "keyword_analysis": {...},
  "missing_keywords": [...],
  "compliance_issues": [...],
  "strengths": [...],
  "weaknesses": [...]
}
```

### `POST /analyze-text`
Analyze resume via text input
```json
Request:
{
  "job_description": "Your job description",
  "resume_text": "Your resume text"
}

Response: (same as /analyze)
```

### `POST /enhance`
Generate enhanced resume
```json
Request:
{
  "resume_text": "Your resume text",
  "job_description": "Job description"
}

Response:
{
  "success": true,
  "enhanced_resume": "Enhanced text...",
  "suggestions": [...]
}
```

### `GET /industry_keywords`
Get keywords for specific industry
```
Query: ?industry=software
Response: {"industry": "software", "keywords": [...]}
```

---

## 🎯 Scoring Breakdown

### Overall Score (0-100)
- **60%**: ATS Score (keyword relevance + structure + compliance)
- **40%**: ML Compatibility (semantic similarity + context match)

### ATS Score Components
1. **Keyword Match**: 0-40%
2. **Structural Compliance**: 0-30%
3. **Industry Bonus**: 0-30%

### Compliance Checks
- ✅ Email validation
- ✅ Section headers presence
- ✅ Bullet point usage
- ✅ Resume length validation
- ✅ Table detection
- ✅ Special character analysis
- ✅ Skills section check

---

## 🔍 How It Works

### 1. **PDF Extraction**
- Tries 3 methods: PyMuPDF → pdfplumber → PyPDF2
- Falls back to OCR if text extraction fails
- Cleans and normalizes extracted text

### 2. **Keyword Extraction**
- Generates 1-gram, 2-gram, and 3-gram phrases
- Filters generic/filler words
- Prioritizes industry-specific keywords
- Removes formatting artifacts

### 3. **Matching Algorithm**
- TF-IDF vectorization for relevance
- Cosine similarity for semantic matching
- N-gram frequency analysis
- Industry-specific bonus scoring

### 4. **ML Analysis**
- Structure evaluation (sections, organization)
- Action verb detection
- Quantifiable achievement checking
- Formatting quality assessment

---

## ⚙️ Configuration

Edit these settings in `app.py`:

```python
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this!
app.config['UPLOAD_FOLDER'] = 'uploads'            # Upload directory
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB file limit
```

---

## 📊 Example Output

```
Overall Score: 78.5/100

ATS Score: 82%
- Keywords matched: 24/35
- Section headers: ✓
- Bullet points: ✓
- Tables: ✗ (remove)

ML Compatibility: 75%
- Strong action verbs: ✓
- Quantifiable achievements: ✓
- Weak areas: Limited metrics

Missing Keywords (Top 15):
1. machine learning
2. data visualization
3. statistical analysis
4. python scikit-learn
5. ...

Compliance Issues:
⚠️ Warning: Resume might be too long (1200 words)
❌ Critical: No email address found
ℹ️ Info: Consider adding more specific metrics
```

---

## 🐛 Troubleshooting

### PDF Upload Issues
- **"Could not extract text from PDF"**
  - Use the text input option instead
  - Ensure PDF is not password-protected
  - Try converting PDF to text first

### Missing Keywords Shows Generic Words
- The filtering has been improved
- Generic words like "skills", "experience" are filtered
- Focus on specific technical keywords

### Low ATS Score
- Check section headers are uppercase
- Add more keywords from job description
- Include quantifiable achievements
- Avoid tables and special formatting

---

## 🚀 Future Enhancements

- [ ] Support for DOCX format resumes
- [ ] Batch resume analysis
- [ ] Resume templates with best practices
- [ ] ATS system-specific optimization (LinkedIn, Workday, etc.)
- [ ] Interview question suggestions
- [ ] Salary benchmarking by keywords
- [ ] Multi-language support
- [ ] Export analysis to PDF
- [ ] User accounts & history tracking
- [ ] Real-time collaboration features

---

## 📄 License

This project is provided as-is for educational and personal use.

**Disclaimer**: This tool provides suggestions only. Always review and customize your resume before submitting. The accuracy may vary based on resume clarity and job description specificity.

---

**Version**: 1.0  
**Last Updated**: March 10, 2026  


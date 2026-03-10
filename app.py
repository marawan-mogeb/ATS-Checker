import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from utils.pdf_parser import extract_text_from_pdf
from utils.ml_processor import ResumeEnhancer, get_ats_score
from utils.ats_rules import check_ats_compliance
import tempfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize ML model
resume_enhancer = ResumeEnhancer()

# Allowed extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

def perform_resume_analysis(resume_text: str, job_description: str) -> dict:
    """
    Shared function to perform all resume analysis
    """
    try:
        # Get ATS score
        ats_score, keyword_analysis = get_ats_score(resume_text, job_description)
        
        # Check ATS compliance
        compliance_issues = check_ats_compliance(resume_text)
        
        # Get ML-based suggestions
        ml_suggestions = resume_enhancer.enhance_resume(resume_text, job_description)
        
        # Generate missing keywords
        missing_keywords = resume_enhancer.get_missing_keywords(resume_text, job_description)
        
        # Calculate overall score
        overall_score = ats_score * 0.6 + ml_suggestions.get('compatibility_score', 0) * 0.4
        
        return {
            'success': True,
            'overall_score': round(overall_score, 1),
            'ats_score': round(ats_score, 1),
            'ml_compatibility_score': ml_suggestions.get('compatibility_score', 0),
            'keyword_analysis': keyword_analysis,
            'missing_keywords': missing_keywords[:15],
            'compliance_issues': compliance_issues,
            'ml_suggestions': ml_suggestions.get('suggestions', []),
            'strengths': ml_suggestions.get('strengths', []),
            'weaknesses': ml_suggestions.get('weaknesses', []),
            'resume_summary': {
                'word_count': len(resume_text.split()),
                'section_count': len(resume_text.split('\n\n')),
                'has_contact_info': any(keyword in resume_text.lower() for keyword in ['@', 'phone', 'email'])
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file uploaded'}), 400
    
    job_description = request.form.get('job_description', '')
    resume_file = request.files['resume']
    
    if resume_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(resume_file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(resume_file.filename)
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        resume_file.save(temp_path)
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(temp_path)
        
        # Clean up temp file
        os.remove(temp_path)
        
        if not resume_text.strip():
            return jsonify({'error': 'Could not extract text from PDF'}), 400
        
        # Perform analysis
        result = perform_resume_analysis(resume_text, job_description)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({'error': result['error']}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/analyze-text', methods=['POST'])
def analyze_resume_text():
    data = request.get_json()
    job_description = data.get('job_description', '')
    resume_text = data.get('resume_text', '')
    
    if not resume_text or not job_description:
        return jsonify({'error': 'Missing resume text or job description'}), 400
    
    # Perform analysis
    result = perform_resume_analysis(resume_text, job_description)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify({'error': result['error']}), 500
    
@app.route('/enhance', methods=['POST'])
def enhance_resume():
    data = request.get_json()
    resume_text = data.get('resume_text', '')
    job_description = data.get('job_description', '')
    
    if not resume_text or not job_description:
        return jsonify({'error': 'Missing resume text or job description'}), 400
    
    try:
        # Get enhanced version with ML
        enhanced_resume = resume_enhancer.generate_enhanced_resume(resume_text, job_description)
        
        # Get specific suggestions
        suggestions = resume_enhancer.get_detailed_suggestions(resume_text, job_description)
        
        return jsonify({
            'success': True,
            'enhanced_resume': enhanced_resume,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/industry_keywords', methods=['GET'])
def get_industry_keywords():
    industry = request.args.get('industry', 'general')
    keywords = resume_enhancer.get_industry_keywords(industry)
    return jsonify({'industry': industry, 'keywords': keywords})

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
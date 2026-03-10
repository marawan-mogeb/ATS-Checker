// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const resumeFile = document.getElementById('resumeFile');
const fileInfo = document.getElementById('fileInfo');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const jobDescription = document.getElementById('jobDescription');
const industrySelect = document.getElementById('industrySelect');

// File upload handling
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.backgroundColor = '';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.backgroundColor = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

resumeFile.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    if (file.type !== 'application/pdf') {
        alert('Please upload a PDF file');
        return;
    }
    
    fileInfo.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    fileInfo.style.color = '#4CAF50';
}

// Tab switching
function openTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').classList.add('active');
    
    // Activate corresponding button
    event.currentTarget.classList.add('active');
}

// Main analysis function
async function analyzeResume() {
    const jobDesc = jobDescription.value.trim();
    const file = resumeFile.files[0];
    const resumeTextInput = document.getElementById('resumeText').value.trim();
    
    if (!jobDesc) {
        alert('Please paste a job description');
        return;
    }
    
    // Use either file upload or text input
    let resumeText = resumeTextInput;
    
    if (!resumeText && !file) {
        alert('Please upload your resume PDF OR paste resume text');
        return;
    }
    
    // Show loading
    analyzeBtn.disabled = true;
    loading.style.display = 'block';
    
    try {
        let data;
        
        if (file && !resumeText) {
            // Use file upload
            const formData = new FormData();
            formData.append('job_description', jobDesc);
            formData.append('resume', file);
            
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });
            data = await response.json();
        } else {
            // Use text input
            const response = await fetch('/analyze-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_description: jobDesc,
                    resume_text: resumeText
                })
            });
            data = await response.json();
        }
        
        if (data.success) {
            displayResults(data);
            loadATSTips();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error analyzing resume: ' + error.message);
    } finally {
        analyzeBtn.disabled = false;
        loading.style.display = 'none';
    }
}

function displayResults(data) {
    // Show results section
    resultsSection.style.display = 'block';
    
    // Update scores
    document.getElementById('overallScore').textContent = data.overall_score;
    document.getElementById('atsScore').textContent = data.ats_score + '%';
    document.getElementById('mlScore').textContent = data.ml_compatibility_score + '%';
    document.getElementById('keywordCoverage').textContent = data.keyword_analysis.keyword_coverage;
    
    // Animate score circle
    const scoreCircle = document.getElementById('scoreCircle');
    const circumference = 339.292; // 2 * π * r (54)
    const offset = circumference - (data.overall_score / 100) * circumference;
    scoreCircle.style.strokeDashoffset = offset;
    
    // Update matched keywords
    const matchedKeywordsDiv = document.getElementById('matchedKeywords');
    matchedKeywordsDiv.innerHTML = data.keyword_analysis.keyword_matches
        .map(keyword => `<span class="keyword-tag success">${keyword}</span>`)
        .join('');
    
    // Update missing keywords
    const missingKeywordsDiv = document.getElementById('missingKeywords');
    missingKeywordsDiv.innerHTML = data.missing_keywords
        .map(keyword => `<span class="keyword-tag warning">${keyword}</span>`)
        .join('');
    
    // Update ML suggestions
    const suggestionsDiv = document.getElementById('mlSuggestions');
    suggestionsDiv.innerHTML = data.ml_suggestions
        .map(suggestion => `
            <div class="suggestion-item">
                <i class="fas fa-bullseye"></i>
                <div>${suggestion}</div>
            </div>
        `).join('');
    
    // Update strengths
    const strengthsDiv = document.getElementById('strengthsList');
    strengthsDiv.innerHTML = data.strengths
        .map(strength => `
            <div class="strength-item">
                <i class="fas fa-check-circle"></i>
                <div>${strength}</div>
            </div>
        `).join('');
    
    // Update weaknesses
    const weaknessesDiv = document.getElementById('weaknessesList');
    weaknessesDiv.innerHTML = data.weaknesses
        .map(weakness => `
            <div class="weakness-item">
                <i class="fas fa-exclamation-triangle"></i>
                <div>${weakness}</div>
            </div>
        `).join('');
    
    // Update compliance issues
    const complianceDiv = document.getElementById('complianceIssues');
    complianceDiv.innerHTML = data.compliance_issues
        .map(issue => `
            <div class="compliance-item ${issue.type}">
                <i class="fas fa-${issue.type === 'critical' ? 'exclamation-circle' : 'info-circle'}"></i>
                <div>
                    <strong>${issue.message}</strong>
                    <p>${issue.suggestion}</p>
                </div>
            </div>
        `).join('');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function loadATSTips() {
    const tips = [
        "Use standard section headers: SUMMARY, EXPERIENCE, EDUCATION, SKILLS",
        "Include keywords from the job description naturally",
        "Use bullet points instead of paragraphs",
        "Avoid tables, columns, and graphics",
        "Save as PDF for best compatibility",
        "Include contact information at the top",
        "Use reverse chronological order",
        "Quantify achievements with numbers and percentages",
        "Use standard fonts (Arial, Calibri, Times New Roman)",
        "Keep resume length to 1-2 pages maximum"
    ];
    
    const tipsList = document.getElementById('atsTips');
    tipsList.innerHTML = tips
        .map(tip => `<li>${tip}</li>`)
        .join('');
}

// Enhance resume function
async function enhanceResume() {
    const jobDesc = jobDescription.value.trim();
    const resumeTextInput = document.getElementById('resumeText').value.trim();
    
    if (!jobDesc) {
        alert('Please paste a job description first');
        return;
    }
    
    if (!resumeTextInput) {
        alert('Please paste your resume text first');
        return;
    }
    
    const enhanceBtn = document.getElementById('enhanceBtn');
    enhanceBtn.disabled = true;
    enhanceBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enhancing...';
    
    try {
        const response = await fetch('/enhance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                resume_text: resumeTextInput,
                job_description: jobDesc
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const enhancedDiv = document.getElementById('enhancedResume');
            enhancedDiv.textContent = data.enhanced_resume;
            enhancedDiv.style.display = 'block';
            
            // Show suggestions if any
            if (data.suggestions && data.suggestions.length > 0) {
                alert('Resume enhanced! Check the suggestions tab for details.');
            }
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error enhancing resume: ' + error.message);
    } finally {
        enhanceBtn.disabled = false;
        enhanceBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> Generate Enhanced Resume';
    }
}

// Get industry keywords
async function getIndustryKeywords(industry) {
    try {
        const response = await fetch(`/industry_keywords?industry=${industry}`);
        const data = await response.json();
        
        // You could display these keywords to the user
        console.log(`Keywords for ${industry}:`, data.keywords);
    } catch (error) {
        console.error('Error fetching keywords:', error);
    }
}

// Event listener for industry change
industrySelect.addEventListener('change', (e) => {
    getIndustryKeywords(e.target.value);
});

// Initialize by getting keywords for default industry
document.addEventListener('DOMContentLoaded', () => {
    getIndustryKeywords('software');
});


// Add to script.js
function updateProgress(percentage, message) {
    const progressBar = document.getElementById('progressBar');
    progressBar.style.width = percentage + '%';
    progressBar.textContent = message;
}
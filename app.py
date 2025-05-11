from flask import Flask, request, render_template, redirect, url_for, flash, send_file
import os
import cv2
import numpy as np
from datetime import datetime
import time
import uuid
from werkzeug.utils import secure_filename
from utils.detector import detect_violations
from utils.report_generator import generate_pdf_report

app = Flask(__name__)
app.secret_key = 'trafficviolation123'

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'
REPORTS_FOLDER = 'static/reports'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Create folders if they don't exist
for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER, REPORTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['video']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Create unique filename
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{unique_id}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Redirect to processing page
        return redirect(url_for('process_video', filename=filename))
    
    flash('Invalid file type. Please upload MP4, AVI, MOV, or MKV video files.')
    return redirect(url_for('index'))

@app.route('/process/<filename>')
def process_video(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Create a folder for processed frames
    unique_folder = os.path.splitext(filename)[0]
    output_folder = os.path.join(PROCESSED_FOLDER, unique_folder)
    os.makedirs(output_folder, exist_ok=True)
    
    # Process video and detect violations
    violations = detect_violations(file_path, output_folder)
    
    # Generate PDF report
    report_filename = f"{unique_folder}_report.pdf"
    report_path = os.path.join(REPORTS_FOLDER, report_filename)
    
    # Basic video info
    video_info = {
        'filename': filename,
        'processed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'violation_count': len(violations)
    }
    
    generate_pdf_report(video_info, violations, output_folder, report_path)
    
    return redirect(url_for('show_results', report=report_filename, folder=unique_folder))

@app.route('/results')
def show_results():
    report = request.args.get('report')
    folder = request.args.get('folder')
    
    # Get list of evidence images
    evidence_path = os.path.join(PROCESSED_FOLDER, folder)
    evidence_files = []
    
    if os.path.exists(evidence_path):
        for file in os.listdir(evidence_path):
            if file.endswith('.jpg'):
                evidence_files.append(file)
    
    return render_template('result.html', 
                           report=report, 
                           folder=folder,
                           evidence_files=evidence_files)

@app.route('/download/<report>')
def download_report(report):
    report_path = os.path.join(REPORTS_FOLDER, report)
    return send_file(report_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
from fpdf import FPDF
import os
import time
from datetime import datetime, timedelta

class ViolationReport(FPDF):
    def header(self):
        # Logo
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Traffic Violation Detection Report', 0, 1, 'C')
        self.ln(10)
        
    def footer(self):
        # Page numbers
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def format_timestamp(seconds):
    """Convert seconds to readable time format"""
    return str(timedelta(seconds=int(seconds)))

def violation_type_to_string(violation_type):
    """Convert violation type code to readable string"""
    types = {
        'speeding': 'Speed Violation',
        'red_light': 'Red Light Violation',
        'lane_violation': 'Lane Discipline Violation',
        'illegal_stopping': 'Illegal Stopping'
    }
    return types.get(violation_type, violation_type)

def generate_pdf_report(video_info, violations, evidence_folder, output_path):
    """
    Generate PDF report of traffic violations
    
    Args:
        video_info: Dictionary with video metadata
        violations: List of violation dictionaries
        evidence_folder: Path to folder with evidence images
        output_path: Path to save the PDF report
    """
    pdf = ViolationReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Add report information
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Video Information:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f"Filename: {video_info['filename']}", 0, 1)
    pdf.cell(0, 8, f"Processed Date: {video_info['processed_date']}", 0, 1)
    
    # Add violation summary
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Violation Summary:', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    # Count violations by type
    violation_counts = {}
    for v in violations:
        v_type = v['type']
        if v_type not in violation_counts:
            violation_counts[v_type] = 0
        violation_counts[v_type] += 1
    
    # Display violation counts
    pdf.cell(0, 8, f"Total Violations Detected: {len(violations)}", 0, 1)
    for v_type, count in violation_counts.items():
        pdf.cell(0, 8, f"{violation_type_to_string(v_type)}: {count}", 0, 1)
    
    # Add detailed violations table
    if violations:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Detailed Violations:', 0, 1)
        
        # Table header
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(10, 10, 'ID', 1, 0, 'C', 1)
        pdf.cell(50, 10, 'Violation Type', 1, 0, 'C', 1)
        pdf.cell(40, 10, 'Timestamp', 1, 0, 'C', 1)
        pdf.cell(90, 10, 'Details', 1, 1, 'C', 1)
        
        # Table data
        pdf.set_font('Arial', '', 10)
        for v in violations:
            # Format timestamp
            timestamp = format_timestamp(v['timestamp'])
            
            # Format details based on violation type
            details_text = ""
            if v['type'] == 'speeding':
                details_text = f"Speed: {v['details']['speed']} km/h (Limit: {v['details']['limit']} km/h)"
            elif v['type'] == 'red_light':
                details_text = f"Intersection ID: {v['details']['intersection_id']}"
            elif v['type'] == 'lane_violation':
                details_text = f"Improper lane change"
            elif v['type'] == 'illegal_stopping':
                details_text = f"Duration: {v['details']['duration']} in {v['details']['zone'].replace('_', ' ')} zone"
            
            pdf.cell(10, 10, str(v['id']), 1, 0, 'C')
            pdf.cell(50, 10, violation_type_to_string(v['type']), 1, 0)
            pdf.cell(40, 10, timestamp, 1, 0)
            pdf.cell(90, 10, details_text, 1, 1)
    
    # Add evidence images
    for v in violations:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Violation {v['id']}: {violation_type_to_string(v['type'])}", 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f"Timestamp: {format_timestamp(v['timestamp'])}", 0, 1)
        
        # Add original image
        pdf.ln(5)
        pdf.cell(0, 8, "Original Frame:", 0, 1)
        image_path = os.path.join(evidence_folder, v['evidence_path'])
        if os.path.exists(image_path):
            pdf.image(image_path, x=30, y=None, w=150)
        
        pdf.ln(120)  # Space for image
        
        # Add processed image with annotations
        pdf.cell(0, 8, "Detected Violation:", 0, 1)
        processed_path = os.path.join(evidence_folder, v['processed_path'])
        if os.path.exists(processed_path):
            pdf.image(processed_path, x=30, y=None, w=150)
    
    # Save the PDF
    pdf.output(output_path)
    print(f"Report generated: {output_path}")
    
    return output_path
import os
import json
from datetime import datetime
from flask import current_app
import pandas as pd
import numpy as np
from .models import Program, AdmissionQuota, Application
from werkzeug.utils import secure_filename

def calculate_admission_score(scores):
    """
    Calculate admission score based on subject scores and weights
    """
    weights = {
        'Toán': 2.0,
        'Văn': 1.0,
        'Anh': 1.0,
        'Lý': 1.5,
        'Hóa': 1.5,
        'Sinh': 1.5
    }
    
    total_score = 0
    total_weight = 0
    
    for subject, score in scores.items():
        if subject in weights:
            total_score += score * weights[subject]
            total_weight += weights[subject]
    
    return total_score / total_weight if total_weight > 0 else 0

def get_program_statistics(program_id):
    """
    Get statistical data for a specific program
    """
    program = Program.query.get(program_id)
    if not program:
        return None
    
    quotas = AdmissionQuota.query.filter_by(program_id=program_id).order_by(AdmissionQuota.year.desc()).all()
    applications = Application.query.filter_by(program_id=program_id).all()
    
    stats = {
        'name': program.name,
        'code': program.code,
        'department': program.department.name,
        'historical_data': [],
        'current_applications': len(applications),
        'gender_ratio': calculate_gender_ratio(applications),
        'geographic_distribution': get_geographic_distribution(applications)
    }
    
    for quota in quotas:
        stats['historical_data'].append({
            'year': quota.year,
            'quota': quota.quota,
            'minimum_score': quota.minimum_score,
            'actual_intake': quota.actual_intake
        })
    
    return stats

def calculate_gender_ratio(applications):
    """
    Calculate gender ratio of applicants
    """
    total = len(applications)
    if total == 0:
        return {'male': 0, 'female': 0}
    
    male_count = sum(1 for app in applications if app.applicant.gender == 'male')
    female_count = total - male_count
    
    return {
        'male': (male_count / total) * 100,
        'female': (female_count / total) * 100
    }

def get_geographic_distribution(applications):
    """
    Get geographic distribution of applicants
    """
    regions = {}
    for app in applications:
        region = app.applicant.address.split(',')[-1].strip()
        regions[region] = regions.get(region, 0) + 1
    
    return regions

def generate_admission_report(start_date, end_date):
    """
    Generate admission report for a specific period
    """
    applications = Application.query.filter(
        Application.application_date.between(start_date, end_date)
    ).all()
    
    report = {
        'total_applications': len(applications),
        'by_program': {},
        'by_status': {},
        'daily_applications': {}
    }
    
    for app in applications:
        # Count by program
        program_name = app.program.name
        report['by_program'][program_name] = report['by_program'].get(program_name, 0) + 1
        
        # Count by status
        report['by_status'][app.status] = report['by_status'].get(app.status, 0) + 1
        
        # Count daily applications
        date_str = app.application_date.strftime('%Y-%m-%d')
        report['daily_applications'][date_str] = report['daily_applications'].get(date_str, 0) + 1
    
    return report

def export_to_excel(data, filename):
    """
    Export data to Excel file
    """
    df = pd.DataFrame(data)
    excel_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    df.to_excel(excel_path, index=False)
    return excel_path

def send_notification(user_email, subject, message):
    """
    Send email notification to user
    """
    # Implementation depends on email service configuration
    pass

def validate_file_upload(file):
    """
    Validate uploaded file
    """
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}
    
    if not file:
        return False
    
    filename = file.filename
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, subfolder=''):
    """
    Save uploaded file to specified location
    """
    if file and validate_file_upload(file):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        return filepath
    return None
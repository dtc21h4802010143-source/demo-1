"""
API endpoints cho tính năng gợi ý ngành học dựa trên điểm và sở thích
"""
from flask import Blueprint, request, jsonify
from .models import db, Program, AdmissionScore, AdmissionMethod, StudentPreference
from datetime import datetime
import json

ai_recommendation_bp = Blueprint('ai_recommendation', __name__)

@ai_recommendation_bp.route('/api/admission-scores', methods=['GET'])
def get_admission_scores():
    """
    Lấy danh sách điểm chuẩn
    Query params:
    - year: Năm (2025, 2024, 2023, 2022)
    - program_name: Tên ngành (tìm kiếm gần đúng)
    - min_score: Điểm tối thiểu
    - max_score: Điểm tối đa
    """
    try:
        year = request.args.get('year', type=int)
        program_name = request.args.get('program_name', '')
        min_score = request.args.get('min_score', type=float)
        max_score = request.args.get('max_score', type=float)
        
        query = AdmissionScore.query
        
        if year:
            query = query.filter_by(year=year)
        
        if program_name:
            query = query.filter(AdmissionScore.program_name.like(f'%{program_name}%'))
        
        if min_score:
            query = query.filter(AdmissionScore.admission_score >= min_score)
        
        if max_score:
            query = query.filter(AdmissionScore.admission_score <= max_score)
        
        scores = query.order_by(AdmissionScore.year.desc(), 
                                AdmissionScore.admission_score.desc()).all()
        
        result = []
        for score in scores:
            result.append({
                'id': score.id,
                'program_name': score.program_name,
                'program_id': score.program_id,
                'year': score.year,
                'admission_score': score.admission_score,
                'notes': score.notes
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_recommendation_bp.route('/api/admission-methods', methods=['GET'])
def get_admission_methods():
    """
    Lấy danh sách phương thức xét tuyển
    Query params:
    - year: Năm
    """
    try:
        year = request.args.get('year', type=int)
        
        query = AdmissionMethod.query
        
        if year:
            query = query.filter_by(year=year)
        
        methods = query.order_by(AdmissionMethod.year.desc()).all()
        
        result = []
        for method in methods:
            result.append({
                'id': method.id,
                'method_name': method.method_name,
                'year': method.year,
                'min_score': method.min_score,
                'special_requirements': method.special_requirements,
                'description': method.description
            })
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_recommendation_bp.route('/api/recommend-programs', methods=['POST'])
def recommend_programs():
    """
    Gợi ý ngành học dựa trên điểm và sở thích
    Body:
    {
        "total_score": 21.5,
        "math_score": 8.0,
        "physics_score": 7.5,
        "english_score": 6.0,
        "subject_combination": "A00",
        "interests": ["công nghệ", "lập trình", "AI"],
        "skills": ["logic", "giải quyết vấn đề"],
        "career_goals": "Trở thành kỹ sư phần mềm"
    }
    """
    try:
        data = request.get_json()
        
        total_score = data.get('total_score')
        interests = data.get('interests', [])
        skills = data.get('skills', [])
        
        if not total_score:
            return jsonify({
                'success': False,
                'error': 'Vui lòng cung cấp tổng điểm'
            }), 400
        
        # Lưu sở thích của học sinh (optional)
        if data.get('save_preference'):
            preference = StudentPreference(
                applicant_id=data.get('applicant_id'),
                session_id=data.get('session_id'),
                math_score=data.get('math_score'),
                physics_score=data.get('physics_score'),
                chemistry_score=data.get('chemistry_score'),
                biology_score=data.get('biology_score'),
                literature_score=data.get('literature_score'),
                english_score=data.get('english_score'),
                history_score=data.get('history_score'),
                geography_score=data.get('geography_score'),
                subject_combination=data.get('subject_combination'),
                total_score=total_score,
                interests=json.dumps(interests, ensure_ascii=False),
                skills=json.dumps(skills, ensure_ascii=False),
                career_goals=data.get('career_goals')
            )
            db.session.add(preference)
            db.session.commit()
        
        # Tìm các ngành phù hợp với điểm số
        current_year = datetime.now().year
        
        # Lấy điểm chuẩn năm gần nhất
        scores_query = AdmissionScore.query.filter(
            AdmissionScore.admission_score <= total_score,
            AdmissionScore.year.in_([current_year, current_year - 1, current_year - 2])
        ).order_by(AdmissionScore.admission_score.desc()).all()
        
        recommendations = []
        
        for score in scores_query:
            # Tính điểm phù hợp
            match_score = calculate_match_score(score, total_score, interests, skills)
            
            # Lấy thông tin chương trình nếu có
            program_info = None
            if score.program_id:
                program = Program.query.get(score.program_id)
                if program:
                    program_info = {
                        'name': program.name,
                        'code': program.code,
                        'description': program.description,
                        'career_prospects': program.career_prospects,
                        'tuition_fee': program.tuition_fee
                    }
            
            recommendations.append({
                'program_name': score.program_name,
                'admission_score': score.admission_score,
                'year': score.year,
                'notes': score.notes,
                'match_score': match_score,
                'score_difference': total_score - score.admission_score,
                'probability': get_admission_probability(total_score, score.admission_score),
                'program_info': program_info
            })
        
        # Sắp xếp theo độ phù hợp
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Lấy top 10
        top_recommendations = recommendations[:10]
        
        return jsonify({
            'success': True,
            'data': {
                'total_score': total_score,
                'recommendations': top_recommendations,
                'total_matches': len(recommendations)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def calculate_match_score(score, total_score, interests, skills):
    """
    Tính điểm phù hợp dựa trên nhiều yếu tố
    Score: 0-100
    """
    match_score = 0.0
    
    # 40% dựa trên điểm số
    score_diff = total_score - score.admission_score
    if score_diff >= 3:
        match_score += 40  # Rất an toàn
    elif score_diff >= 1.5:
        match_score += 35  # An toàn
    elif score_diff >= 0.5:
        match_score += 30  # Trúng tuyển khả thi
    elif score_diff >= 0:
        match_score += 25  # Nguy hiểm
    else:
        match_score += 10  # Rất khó
    
    # 30% dựa trên sở thích
    program_name_lower = score.program_name.lower()
    interest_keywords = {
        'công nghệ': ['công nghệ', 'kỹ thuật', 'máy tính', 'phần mềm', 'mạng', 'an ninh'],
        'kinh doanh': ['kinh doanh', 'quản trị', 'marketing', 'thương mại'],
        'thiết kế': ['thiết kế', 'đồ họa', 'truyền thông', 'nghệ thuật'],
        'tài chính': ['tài chính', 'ngân hàng', 'kế toán'],
        'AI': ['AI', 'trí tuệ', 'máy học', 'dữ liệu'],
        'tự động': ['tự động', 'robot', 'điện tử', 'cơ điện']
    }
    
    interest_match = 0
    for interest in interests:
        interest_lower = interest.lower()
        if interest_lower in interest_keywords:
            for keyword in interest_keywords[interest_lower]:
                if keyword in program_name_lower:
                    interest_match += 10
                    break
    
    match_score += min(interest_match, 30)
    
    # 30% dựa trên kỹ năng
    skill_keywords = {
        'lập trình': ['phần mềm', 'công nghệ thông tin', 'máy tính'],
        'logic': ['máy tính', 'toán', 'AI'],
        'sáng tạo': ['thiết kế', 'đồ họa', 'nghệ thuật', 'truyền thông'],
        'giao tiếp': ['marketing', 'quản trị', 'kinh doanh'],
        'kỹ thuật': ['kỹ thuật', 'điện', 'tự động', 'ô tô']
    }
    
    skill_match = 0
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower in skill_keywords:
            for keyword in skill_keywords[skill_lower]:
                if keyword in program_name_lower:
                    skill_match += 10
                    break
    
    match_score += min(skill_match, 30)
    
    return round(match_score, 2)

def get_admission_probability(total_score, admission_score):
    """
    Tính xác suất trúng tuyển
    """
    diff = total_score - admission_score
    
    if diff >= 3:
        return "Rất cao (95-100%)"
    elif diff >= 1.5:
        return "Cao (80-95%)"
    elif diff >= 0.5:
        return "Trung bình (60-80%)"
    elif diff >= 0:
        return "Thấp (40-60%)"
    else:
        return "Rất thấp (<40%)"

@ai_recommendation_bp.route('/api/statistics/admission-scores', methods=['GET'])
def get_admission_statistics():
    """
    Lấy thống kê điểm chuẩn theo năm
    """
    try:
        year = request.args.get('year', type=int, default=datetime.now().year)
        
        # Thống kê cơ bản
        total_programs = AdmissionScore.query.filter_by(year=year).count()
        
        if total_programs == 0:
            return jsonify({
                'success': True,
                'data': {
                    'year': year,
                    'total_programs': 0,
                    'message': 'Chưa có dữ liệu cho năm này'
                }
            })
        
        avg_score = db.session.query(db.func.avg(AdmissionScore.admission_score))\
            .filter_by(year=year).scalar()
        max_score = db.session.query(db.func.max(AdmissionScore.admission_score))\
            .filter_by(year=year).scalar()
        min_score = db.session.query(db.func.min(AdmissionScore.admission_score))\
            .filter_by(year=year).scalar()
        
        # Top ngành có điểm cao nhất
        top_programs = AdmissionScore.query.filter_by(year=year)\
            .order_by(AdmissionScore.admission_score.desc())\
            .limit(5).all()
        
        top_list = [{
            'program_name': p.program_name,
            'admission_score': p.admission_score,
            'notes': p.notes
        } for p in top_programs]
        
        return jsonify({
            'success': True,
            'data': {
                'year': year,
                'total_programs': total_programs,
                'average_score': round(avg_score, 2) if avg_score else None,
                'max_score': max_score,
                'min_score': min_score,
                'top_programs': top_list
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

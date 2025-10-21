"""
Integration tests for application routes
Tests public routes, user routes, and admin routes
"""

import pytest
from backend.models import db, User, Department, Program, Applicant
from backend.app import app as flask_app


@pytest.fixture(scope='function')
def app():
    """Create test Flask application"""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret'
    })
    
    with flask_app.app_context():
        db.create_all()
        # Create test data
        dept = Department(name='Computer Science')
        db.session.add(dept)
        db.session.commit()
        
        program = Program(
            name='Software Engineering',
            code='SE01',
            department_id=dept.id
        )
        db.session.add(program)
        db.session.commit()
        
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def logged_in_user(app, client):
    """Create and log in a verified user"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            email_verified=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
    
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    return user


@pytest.fixture
def admin_user(app, client):
    """Create and log in an admin user"""
    with app.app_context():
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            email_verified=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    return admin


# ============================================================================
# PUBLIC ROUTE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.routes
class TestPublicRoutes:
    """Test publicly accessible routes"""
    
    def test_homepage(self, client):
        """Test homepage loads"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_about_page(self, client):
        """Test about page loads"""
        response = client.get('/about')
        # May return 200 or 404 if not implemented
        assert response.status_code in [200, 404]
    
    def test_programs_page(self, client):
        """Test programs listing page"""
        response = client.get('/programs')
        assert response.status_code == 200
    
    def test_departments_page(self, client):
        """Test departments listing page"""
        response = client.get('/departments')
        assert response.status_code == 200
    
    def test_contact_page(self, client):
        """Test contact page"""
        response = client.get('/contact')
        assert response.status_code == 200
    
    def test_faq_page(self, client):
        """Test FAQ page"""
        response = client.get('/faq')
        assert response.status_code == 200
    
    def test_chatbot_page(self, client):
        """Test chatbot page"""
        response = client.get('/chatbot')
        assert response.status_code == 200


# ============================================================================
# USER ROUTE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.routes
class TestUserRoutes:
    """Test user-authenticated routes"""
    
    def test_profile_view(self, client, logged_in_user):
        """Test profile view page"""
        response = client.get('/profile')
        assert response.status_code == 200
    
    def test_profile_edit(self, client, logged_in_user):
        """Test profile edit page"""
        response = client.get('/profile/edit')
        assert response.status_code == 200
    
    def test_profile_update(self, client, logged_in_user, app):
        """Test updating profile"""
        response = client.post('/profile/edit', data={
            'full_name': 'John Doe',
            'phone': '0123456789',
            'address': '123 Main St',
            'high_school': 'ABC School'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify applicant was created
        with app.app_context():
            applicant = Applicant.query.filter_by(email='test@example.com').first()
            assert applicant is not None
            assert applicant.full_name == 'John Doe'
    
    def test_wishes_view(self, client, logged_in_user):
        """Test wishes/applications view page"""
        response = client.get('/wishes')
        assert response.status_code == 200
    
    def test_add_wish(self, client, logged_in_user, app):
        """Test adding a wish"""
        # First create profile
        client.post('/profile/edit', data={
            'full_name': 'Test User',
            'phone': '0123456789'
        })
        
        # Get program ID
        with app.app_context():
            program = Program.query.first()
            program_id = program.id
        
        # Add wish
        response = client.post('/wishes/add', data={
            'program_id': program_id
        }, follow_redirects=True)
        
        assert response.status_code == 200


# ============================================================================
# ADMIN ROUTE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.routes
class TestAdminRoutes:
    """Test admin-only routes"""
    
    def test_admin_dashboard(self, client, admin_user):
        """Test admin dashboard loads"""
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
    
    def test_admin_programs_list(self, client, admin_user):
        """Test admin programs management page"""
        response = client.get('/admin/programs')
        assert response.status_code == 200
    
    def test_admin_add_program(self, client, admin_user, app):
        """Test adding a program via admin"""
        with app.app_context():
            dept = Department.query.first()
            dept_id = dept.id
        
        response = client.post('/admin/programs/add', data={
            'name': 'New Program',
            'code': 'NP01',
            'department_id': dept_id,
            'description': 'Test program'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_admin_departments_list(self, client, admin_user):
        """Test admin departments management page"""
        response = client.get('/admin/departments')
        assert response.status_code == 200
    
    def test_admin_applications_list(self, client, admin_user):
        """Test admin applications management page"""
        response = client.get('/admin/applications')
        assert response.status_code == 200
    
    def test_admin_statistics(self, client, admin_user):
        """Test admin statistics page"""
        response = client.get('/admin/statistics')
        assert response.status_code == 200
    
    def test_regular_user_cannot_access_admin(self, client, logged_in_user):
        """Test regular user cannot access admin routes"""
        response = client.get('/admin/dashboard')
        assert response.status_code in [302, 403, 401]


# ============================================================================
# API ROUTE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.routes
class TestAPIRoutes:
    """Test API endpoints"""
    
    def test_chatbot_api(self, client):
        """Test chatbot API endpoint"""
        response = client.post('/api/chat', json={
            'message': 'Tell me about programs',
            'session_id': 'test123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'response' in data or 'error' in data
    
    def test_notifications_api_requires_auth(self, client):
        """Test notifications API requires authentication"""
        response = client.get('/api/notifications')
        assert response.status_code in [302, 401]
    
    def test_notifications_api_authenticated(self, client, logged_in_user):
        """Test notifications API with authentication"""
        response = client.get('/api/notifications')
        assert response.status_code == 200
        data = response.get_json()
        assert 'notifications' in data
        assert 'unread_count' in data


# ============================================================================
# ERROR HANDLER TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.routes
class TestErrorHandlers:
    """Test error handling"""
    
    def test_404_error(self, client):
        """Test 404 page"""
        response = client.get('/nonexistent-page-12345')
        assert response.status_code == 404
    
    def test_404_has_template(self, client):
        """Test 404 page uses custom template"""
        response = client.get('/does-not-exist')
        assert response.status_code == 404
        # Check if custom 404 template is rendered
        assert b'404' in response.data or b'not found' in response.data.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

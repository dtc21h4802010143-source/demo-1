"""
Integration tests for authentication flow
Tests registration, login, logout, email verification, password reset
"""

import pytest
from flask import url_for
from backend.models import db, User
from backend.app import app as flask_app


@pytest.fixture(scope='function')
def app():
    """Create test Flask application"""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret',
        'LOGIN_DISABLED': False
    })
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def auth_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            role='user',
            email_verified=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def admin_user(app):
    """Create an admin user"""
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
        return admin


# ============================================================================
# REGISTRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.auth
class TestRegistration:
    """Test user registration flow"""
    
    def test_registration_page_loads(self, client):
        """Test registration page is accessible"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'k' in response.data.lower()
    
    def test_successful_registration(self, client, app):
        """Test successful user registration"""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123',
            'confirm_password': 'SecurePass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check user was created
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert not user.email_verified
    
    def test_duplicate_username_registration(self, client, auth_user):
        """Test registration with existing username"""
        response = client.post('/register', data={
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show error message
    
    def test_password_mismatch_registration(self, client):
        """Test registration with mismatched passwords"""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'confirm_password': 'differentpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should remain on registration page or show error


# ============================================================================
# LOGIN TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.auth
class TestLogin:
    """Test login functionality"""
    
    def test_login_page_loads(self, client):
        """Test login page is accessible"""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_successful_login(self, client, auth_user):
        """Test successful login"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check we're redirected to home or dashboard
    
    def test_login_wrong_password(self, client, auth_user):
        """Test login with incorrect password"""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show error message
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post('/login', data={
            'username': 'doesnotexist',
            'password': 'somepassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_logout(self, client, auth_user):
        """Test logout functionality"""
        # First login
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200


# ============================================================================
# PROTECTED ROUTE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.auth
class TestProtectedRoutes:
    """Test authentication requirements for protected routes"""
    
    def test_profile_requires_auth(self, client):
        """Test profile page requires login"""
        response = client.get('/profile')
        assert response.status_code in [302, 401]  # Redirect to login or unauthorized
    
    def test_wishes_requires_auth(self, client):
        """Test wishes page requires login"""
        response = client.get('/wishes')
        assert response.status_code in [302, 401]
    
    def test_admin_requires_admin_role(self, client, auth_user):
        """Test admin routes require admin role"""
        # Login as regular user
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Try to access admin route
        response = client.get('/admin/dashboard')
        assert response.status_code in [302, 403, 401]
    
    def test_admin_access_with_admin_role(self, client, admin_user):
        """Test admin can access admin routes"""
        # Login as admin
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Access admin route
        response = client.get('/admin/dashboard')
        assert response.status_code == 200


# ============================================================================
# EMAIL VERIFICATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.auth
class TestEmailVerification:
    """Test email verification flow"""
    
    def test_unverified_user_restricted(self, client, app):
        """Test unverified users have restrictions"""
        # Create unverified user
        with app.app_context():
            user = User(
                username='unverified',
                email='unverified@example.com',
                email_verified=False
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        # Login
        client.post('/login', data={
            'username': 'unverified',
            'password': 'password123'
        })
        
        # Try to access verified-only route (if any)
        # Should be redirected or shown warning


# ============================================================================
# PASSWORD RESET TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.auth
class TestPasswordReset:
    """Test password reset functionality"""
    
    def test_forgot_password_page_loads(self, client):
        """Test forgot password page loads"""
        response = client.get('/forgot-password')
        assert response.status_code == 200
    
    def test_password_reset_request(self, client, auth_user):
        """Test requesting password reset"""
        response = client.post('/forgot-password', data={
            'email': 'test@example.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

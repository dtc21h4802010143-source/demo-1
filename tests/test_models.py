"""
Unit tests for database models
Tests all 7 models: User, Department, Program, Applicant, Application, ChatbotInteraction, Notification
"""

import pytest
from datetime import datetime, date
from backend.models import (
    db, User, Department, Program, Applicant, Application,
    ChatbotInteraction, Notification, SiteSetting, AdmissionQuota,
    ApplicationStatusLog, ApplicantDocument, Score
)
from backend.app import app as flask_app


@pytest.fixture(scope='function')
def app():
    """Create and configure a test Flask application"""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Test client for making requests"""
    return app.test_client()


@pytest.fixture(scope='function')
def session(app):
    """Database session for tests"""
    with app.app_context():
        yield db.session


# ============================================================================
# USER MODEL TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestUserModel:
    """Test User model functionality"""
    
    def test_create_user(self, session):
        """Test creating a new user"""
        user = User(username='testuser', email='test@example.com', role='user')
        user.set_password('password123')
        session.add(user)
        session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role == 'user'
        assert user.check_password('password123')
        assert not user.email_verified
    
    def test_password_hashing(self, session):
        """Test password hashing and verification"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('secretpassword')
        
        assert user.password_hash != 'secretpassword'
        assert user.check_password('secretpassword')
        assert not user.check_password('wrongpassword')
    
    def test_user_unique_constraints(self, session):
        """Test unique constraints on username and email"""
        user1 = User(username='testuser', email='test@example.com')
        user1.set_password('pass')
        session.add(user1)
        session.commit()
        
        # Try to create user with same username
        user2 = User(username='testuser', email='different@example.com')
        user2.set_password('pass')
        session.add(user2)
        
        with pytest.raises(Exception):  # IntegrityError
            session.commit()


# ============================================================================
# DEPARTMENT MODEL TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestDepartmentModel:
    """Test Department model"""
    
    def test_create_department(self, session):
        """Test creating a department"""
        dept = Department(
            name='Computer Science',
            description='CS Department',
            head='Dr. Smith',
            contact_email='cs@university.edu'
        )
        session.add(dept)
        session.commit()
        
        assert dept.id is not None
        assert dept.name == 'Computer Science'
        assert dept.head == 'Dr. Smith'
    
    def test_department_program_relationship(self, session):
        """Test relationship between Department and Program"""
        dept = Department(name='Engineering')
        session.add(dept)
        session.commit()
        
        program = Program(
            name='Software Engineering',
            code='SE01',
            department_id=dept.id,
            description='Software development program'
        )
        session.add(program)
        session.commit()
        
        assert len(dept.programs) == 1
        assert dept.programs[0].name == 'Software Engineering'


# ============================================================================
# PROGRAM MODEL TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestProgramModel:
    """Test Program model"""
    
    def test_create_program(self, session):
        """Test creating a program"""
        dept = Department(name='Science')
        session.add(dept)
        session.commit()
        
        program = Program(
            name='Data Science',
            code='DS01',
            department_id=dept.id,
            description='Data analysis and ML',
            duration='4 years',
            tuition_fee=50000.00
        )
        session.add(program)
        session.commit()
        
        assert program.id is not None
        assert program.code == 'DS01'
        assert program.tuition_fee == 50000.00
        assert program.department.name == 'Science'
    
    def test_program_unique_code(self, session):
        """Test unique constraint on program code"""
        dept = Department(name='Engineering')
        session.add(dept)
        session.commit()
        
        program1 = Program(name='Program 1', code='P01', department_id=dept.id)
        session.add(program1)
        session.commit()
        
        program2 = Program(name='Program 2', code='P01', department_id=dept.id)
        session.add(program2)
        
        with pytest.raises(Exception):  # IntegrityError
            session.commit()


# ============================================================================
# APPLICANT MODEL TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestApplicantModel:
    """Test Applicant model"""
    
    def test_create_applicant(self, session):
        """Test creating an applicant"""
        applicant = Applicant(
            full_name='John Doe',
            email='john@example.com',
            phone='0123456789',
            date_of_birth=date(2000, 1, 15),
            address='123 Main St',
            high_school='ABC High School'
        )
        session.add(applicant)
        session.commit()
        
        assert applicant.id is not None
        assert applicant.full_name == 'John Doe'
        assert applicant.email == 'john@example.com'
        assert applicant.registration_date is not None
    
    def test_applicant_unique_email(self, session):
        """Test unique constraint on applicant email"""
        app1 = Applicant(full_name='User 1', email='test@example.com')
        session.add(app1)
        session.commit()
        
        app2 = Applicant(full_name='User 2', email='test@example.com')
        session.add(app2)
        
        with pytest.raises(Exception):
            session.commit()


# ============================================================================
# APPLICATION MODEL TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestApplicationModel:
    """Test Application (Wish) model"""
    
    def test_create_application(self, session):
        """Test creating an application"""
        # Setup
        dept = Department(name='Engineering')
        session.add(dept)
        session.commit()
        
        program = Program(name='CS', code='CS01', department_id=dept.id)
        session.add(program)
        session.commit()
        
        applicant = Applicant(full_name='Jane Doe', email='jane@example.com')
        session.add(applicant)
        session.commit()
        
        # Create application
        app = Application(
            applicant_id=applicant.id,
            program_id=program.id,
            status='Draft'
        )
        session.add(app)
        session.commit()
        
        assert app.id is not None
        assert app.status == 'Draft'
        assert app.applicant.full_name == 'Jane Doe'
        assert app.program.code == 'CS01'
    
    def test_application_relationships(self, session):
        """Test application relationships with applicant and program"""
        dept = Department(name='Dept')
        program = Program(name='Prog', code='P01', department_id=dept.id)
        applicant = Applicant(full_name='Test', email='test@example.com')
        
        session.add_all([dept, program, applicant])
        session.commit()
        
        app = Application(applicant_id=applicant.id, program_id=program.id)
        session.add(app)
        session.commit()
        
        # Test backref
        assert len(applicant.applications) == 1
        assert len(program.applications) == 1


# ============================================================================
# CHATBOT INTERACTION MODEL TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestChatbotInteractionModel:
    """Test ChatbotInteraction model"""
    
    def test_create_interaction(self, session):
        """Test creating a chatbot interaction"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('pass')
        session.add(user)
        session.commit()
        
        interaction = ChatbotInteraction(
            user_input='What programs do you offer?',
            bot_response='We offer CS, Engineering, etc.',
            user_id=user.id,
            session_id='sess123'
        )
        session.add(interaction)
        session.commit()
        
        assert interaction.id is not None
        assert interaction.user_input.startswith('What programs')
        assert interaction.timestamp is not None
    
    def test_interaction_with_feedback(self, session):
        """Test chatbot interaction with feedback"""
        interaction = ChatbotInteraction(
            user_input='Test question',
            bot_response='Test answer',
            feedback_rating=5,
            feedback_comment='Very helpful!'
        )
        session.add(interaction)
        session.commit()
        
        assert interaction.feedback_rating == 5
        assert interaction.feedback_comment == 'Very helpful!'


# ============================================================================
# NOTIFICATION MODEL TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestNotificationModel:
    """Test Notification model"""
    
    def test_create_notification(self, session):
        """Test creating a notification"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('pass')
        session.add(user)
        session.commit()
        
        notif = Notification(
            user_id=user.id,
            title='Welcome',
            message='Welcome to the system!',
            type='success',
            link='/profile'
        )
        session.add(notif)
        session.commit()
        
        assert notif.id is not None
        assert notif.title == 'Welcome'
        assert not notif.is_read
        assert notif.created_at is not None
    
    def test_notification_user_relationship(self, session):
        """Test notification relationship with user"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('pass')
        session.add(user)
        session.commit()
        
        notif1 = Notification(user_id=user.id, title='N1', message='M1')
        notif2 = Notification(user_id=user.id, title='N2', message='M2')
        session.add_all([notif1, notif2])
        session.commit()
        
        assert user.notifications.count() == 2


# ============================================================================
# SITE SETTING MODEL TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestSiteSettingModel:
    """Test SiteSetting model"""
    
    def test_create_setting(self, session):
        """Test creating a site setting"""
        setting = SiteSetting(key='contact_email', value='info@university.edu')
        session.add(setting)
        session.commit()
        
        assert setting.id is not None
        assert setting.key == 'contact_email'
    
    def test_setting_unique_key(self, session):
        """Test unique constraint on setting key"""
        setting1 = SiteSetting(key='phone', value='123-456')
        session.add(setting1)
        session.commit()
        
        setting2 = SiteSetting(key='phone', value='789-012')
        session.add(setting2)
        
        with pytest.raises(Exception):
            session.commit()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

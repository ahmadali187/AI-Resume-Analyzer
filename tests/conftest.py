import pytest
from app import create_app
from extensions import db
from models.user import User


@pytest.fixture
def app():
    """Create application instance configured for testing."""
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_user(app):
    """Fixture creating and returning a test user."""
    with app.app_context():
        user = User(name="Test User", email="test@example.com", is_admin=True)
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        return user

import pytest
from app import create_app, db
from app.models import User, AIProject, Prompt


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(app, client):
    with app.app_context():
        user = User(email='test@example.com', username='testuser')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    with client.session_transaction() as sess:
        sess['_user_id'] = '1'

    return client


class TestDashboard:
    def test_dashboard_requires_login(self, client):
        response = client.get('/dashboard/')
        assert response.status_code == 302

    def test_projects_page_requires_login(self, client):
        response = client.get('/dashboard/projects')
        assert response.status_code == 302


class TestAIEndpoints:
    def test_chat_requires_login(self, client):
        response = client.get('/ai/chat')
        assert response.status_code == 302

    def test_prompt_builder_requires_login(self, client):
        response = client.get('/ai/prompt')
        assert response.status_code == 302
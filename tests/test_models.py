import pytest
from app import create_app, db
from app.models import User


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
def runner(app):
    return app.test_cli_runner()


class TestAuth:
    def test_login_page(self, client):
        response = client.get('/login')
        assert response.status_code == 200

    def test_register_page(self, client):
        response = client.get('/register')
        assert response.status_code == 200

    def test_health_endpoint(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'


class TestUserModel:
    def test_create_user(self, app):
        with app.app_context():
            user = User(email='test@example.com', username='testuser')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

            found_user = User.query.filter_by(email='test@example.com').first()
            assert found_user is not None
            assert found_user.check_password('password123')
            assert not found_user.check_password('wrongpassword')

    def test_user_api_calls(self, app):
        with app.app_context():
            user = User(email='test2@example.com', username='testuser2', max_api_calls=10, api_calls_used=5)
            assert user.can_make_api_call()
            user.increment_api_calls()
            assert user.api_calls_used == 6
            assert user.can_make_api_call()

            user.api_calls_used = 10
            assert not user.can_make_api_call()
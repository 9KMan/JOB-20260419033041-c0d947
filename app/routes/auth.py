from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.models.user import APIKey
import secrets
import string

auth_bp = Blueprint('auth', __name__)


def generate_api_key():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))


@auth_bp.route('/')
def index():
    return render_template('index.html')


@auth_bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('auth/login.html')


@auth_bp.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = request.form.get('remember', False)

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user, remember=remember)
        user.last_login = db.func.now()
        db.session.commit()
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.index'))

    flash('Invalid email or password', 'danger')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('auth/register.html')


@auth_bp.route('/register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    terms = request.form.get('terms')

    if password != confirm_password:
        flash('Passwords do not match', 'danger')
        return redirect(url_for('auth.register'))

    if not terms:
        flash('You must accept the terms and conditions', 'danger')
        return redirect(url_for('auth.register'))

    if User.query.filter_by(email=email).first():
        flash('Email already registered', 'danger')
        return redirect(url_for('auth.register'))

    if User.query.filter_by(username=username).first():
        flash('Username already taken', 'danger')
        return redirect(url_for('auth.register'))

    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash('Account created successfully! Please log in.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')


@auth_bp.route('/profile', methods=['POST'])
@login_required
def profile_post():
    current_user.first_name = request.form.get('first_name')
    current_user.last_name = request.form.get('last_name')
    current_user.company = request.form.get('company')

    new_password = request.form.get('new_password')
    if new_password:
        current_user.set_password(new_password)

    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/api-keys')
@login_required
def api_keys():
    keys = APIKey.query.filter_by(user_id=current_user.id).all()
    return render_template('auth/api_keys.html', keys=keys)


@auth_bp.route('/api-keys/create', methods=['POST'])
@login_required
def create_api_key():
    name = request.json.get('name', 'My API Key')
    api_key = generate_api_key()

    key_record = APIKey(
        user_id=current_user.id,
        key_hash=api_key,
        name=name
    )
    db.session.add(key_record)
    db.session.commit()

    return jsonify({
        'success': True,
        'api_key': api_key,
        'id': key_record.id
    })


@auth_bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
@login_required
def delete_api_key(key_id):
    key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    if key:
        db.session.delete(key)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Not found'}), 404
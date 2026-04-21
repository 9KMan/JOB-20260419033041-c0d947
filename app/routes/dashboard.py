from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import AIProject, Prompt, AIConversation, AIMessage
from app.services.ai_service import AIService
from datetime import datetime
import json

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
ai_bp = Blueprint('ai', __name__, url_prefix='/ai')


@dashboard_bp.route('/')
@login_required
def index():
    projects = AIProject.query.filter_by(user_id=current_user.id, isarchived=False).order_by(AIProject.updated_at.desc()).all()
    recent_prompts = Prompt.query.filter_by(user_id=current_user.id).order_by(Prompt.created_at.desc()).limit(10).all()
    return render_template('dashboard/index.html', projects=projects, recent_prompts=recent_prompts)


@dashboard_bp.route('/projects')
@login_required
def projects():
    projects = AIProject.query.filter_by(user_id=current_user.id, isarchived=False).order_by(AIProject.updated_at.desc()).all()
    return render_template('dashboard/projects.html', projects=projects)


@dashboard_bp.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    project = AIProject.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    prompts = Prompt.query.filter_by(project_id=project.id).order_by(Prompt.created_at.desc()).all()
    return render_template('dashboard/project_detail.html', project=project, prompts=prompts)


@dashboard_bp.route('/project/create', methods=['POST'])
@login_required
def create_project():
    name = request.form.get('name')
    description = request.form.get('description', '')
    project_type = request.form.get('project_type', 'general')

    project = AIProject(
        user_id=current_user.id,
        name=name,
        description=description,
        project_type=project_type
    )
    db.session.add(project)
    db.session.commit()

    flash('Project created successfully!', 'success')
    return redirect(url_for('dashboard.project_detail', project_id=project.id))


@ai_bp.route('/chat')
@login_required
def chat():
    conversations = AIConversation.query.filter_by(user_id=current_user.id, isarchived=False).order_by(AIConversation.updated_at.desc()).all()
    return render_template('ai/chat.html', conversations=conversations)


@ai_bp.route('/chat/<int:conversation_id>')
@login_required
def chat_conversation(conversation_id):
    conversation = AIConversation.query.filter_by(id=conversation_id, user_id=current_user.id).first_or_404()
    messages = AIMessage.query.filter_by(conversation_id=conversation.id).order_by(AIMessage.created_at.asc()).all()
    return render_template('ai/chat_conversation.html', conversation=conversation, messages=messages)


@ai_bp.route('/prompt')
@login_required
def prompt_builder():
    projects = AIProject.query.filter_by(user_id=current_user.id, isarchived=False).all()
    return render_template('ai/prompt_builder.html', projects=projects)


@ai_bp.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    if not current_user.can_make_api_call():
        return jsonify({'error': 'API call limit reached'}), 429

    data = request.get_json()
    message = data.get('message')
    conversation_id = data.get('conversation_id')
    project_id = data.get('project_id')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        ai_service = AIService()

        if conversation_id:
            conversation = AIConversation.query.filter_by(id=conversation_id, user_id=current_user.id).first()
            if not conversation:
                conversation = AIConversation(
                    user_id=current_user.id,
                    project_id=project_id,
                    title=message[:50]
                )
                db.session.add(conversation)
                db.session.commit()
        else:
            conversation = AIConversation(
                user_id=current_user.id,
                project_id=project_id,
                title=message[:50]
            )
            db.session.add(conversation)
            db.session.commit()

        user_message = AIMessage(
            conversation_id=conversation.id,
            role='user',
            content=message
        )
        db.session.add(user_message)

        response_text, usage = ai_service.chat([{'role': 'user', 'content': message}])

        assistant_message = AIMessage(
            conversation_id=conversation.id,
            role='assistant',
            content=response_text,
            model_used=ai_service.model,
            tokens_used=usage.get('total_tokens', 0) if usage else 0
        )
        db.session.add(assistant_message)

        conversation.updated_at = datetime.utcnow()
        current_user.increment_api_calls()
        db.session.commit()

        return jsonify({
            'success': True,
            'response': response_text,
            'conversation_id': conversation.id,
            'message_id': assistant_message.id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/api/prompt', methods=['POST'])
@login_required
def api_prompt():
    if not current_user.can_make_api_call():
        return jsonify({'error': 'API call limit reached'}), 429

    data = request.get_json()
    prompt_text = data.get('prompt')
    project_id = data.get('project_id')
    title = data.get('title', 'Untitled Prompt')
    parameters = data.get('parameters', {})

    if not prompt_text:
        return jsonify({'error': 'Prompt text is required'}), 400

    try:
        ai_service = AIService()
        response, usage = ai_service.complete(prompt_text, **parameters)

        prompt = Prompt(
            project_id=project_id,
            user_id=current_user.id,
            title=title,
            prompt_text=prompt_text,
            model_used=ai_service.model,
            parameters=parameters,
            response_text=response,
            tokens_used=usage.get('total_tokens', 0) if usage else 0,
            completed_at=datetime.utcnow()
        )
        db.session.add(prompt)
        current_user.increment_api_calls()
        db.session.commit()

        return jsonify({
            'success': True,
            'response': response,
            'prompt_id': prompt.id,
            'usage': usage
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/api/models', methods=['GET'])
@login_required
def list_models():
    ai_service = AIService()
    models = ai_service.list_available_models()
    return jsonify({'models': models})
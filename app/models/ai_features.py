from datetime import datetime
from app import db


class AIProject(db.Model):
    __tablename__ = 'ai_projects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    project_type = db.Column(db.String(50))
    settings = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    isarchived = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('projects', lazy='dynamic'))
    prompts = db.relationship('Prompt', backref='project', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<AIProject {self.name}>'


class Prompt(db.Model):
    __tablename__ = 'prompts'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('ai_projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255))
    prompt_text = db.Column(db.Text, nullable=False)
    model_used = db.Column(db.String(100))
    parameters = db.Column(db.JSON, default=dict)
    response_text = db.Column(db.Text)
    tokens_used = db.Column(db.Integer, default=0)
    cost = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    user = db.relationship('User', backref=db.backref('prompts', lazy='dynamic'))
    categories = db.relationship('PromptCategory', backref='prompt', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Prompt {self.title}>'


class PromptCategory(db.Model):
    __tablename__ = 'prompt_categories'

    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.id'), nullable=False)
    name = db.Column(db.String(100))

    def __repr__(self):
        return f'<PromptCategory {self.name}>'


class AIConversation(db.Model):
    __tablename__ = 'ai_conversations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('ai_projects.id'))
    title = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    isarchived = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('conversations', lazy='dynamic'))
    messages = db.relationship('AIMessage', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<AIConversation {self.title}>'


class AIMessage(db.Model):
    __tablename__ = 'ai_messages'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('ai_conversations.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    model_used = db.Column(db.String(100))
    tokens_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AIMessage {self.role}>'
from app import create_app, db
from app.models import User, AIProject, Prompt, AIConversation, AIMessage

app = create_app('development')

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'AIProject': AIProject,
        'Prompt': Prompt,
        'AIConversation': AIConversation,
        'AIMessage': AIMessage
    }
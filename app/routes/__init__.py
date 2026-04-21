from flask import Blueprint

def register_routes(app):
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp, ai_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(ai_bp)

    @app.route('/health')
    def health():
        return {'status': 'healthy'}

    @app.route('/api/health')
    def api_health():
        return {'status': 'healthy', 'service': 'saas-app'}
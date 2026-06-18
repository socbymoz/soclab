import os
import logging
from datetime import datetime
from flask import Flask, render_template
from backend.config import Config
from backend.curriculum import MODULES
from backend.routes import main_bp

_basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_app():
    app = Flask(__name__,
        template_folder=os.path.join(_basedir, "frontend", "templates"),
        static_folder=os.path.join(_basedir, "frontend", "static")
    )

    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY
    app.config['SESSION_COOKIE_SECURE'] = Config.SESSION_COOKIE_SECURE
    app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = Config.SESSION_COOKIE_SAMESITE

    log_level = getattr(logging, Config.LOG_LEVEL, logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()]
    )

    @app.context_processor
    def inject_globals():
        return dict(CURRICULUM=MODULES, now=datetime.now, PASS_SCORE=Config.PASS_SCORE)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    app.register_blueprint(main_bp)

    return app

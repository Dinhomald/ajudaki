import os
import zlib

from flask import Flask

from blueprints.conta import conta_bp, e_quem_ajuda, e_quem_pediu
from blueprints.dashboard import dashboard_bp
from blueprints.impacto import impacto_bp
from blueprints.necessidades import necessidades_bp
from blueprints.organizacoes import organizacoes_bp
from blueprints.talentos import talentos_bp
from blueprints.territorio import territorio_bp
from blueprints.trocas import trocas_bp
from helpers import sem_ficticio, status_badge
from models import db, ensure_new_columns

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "ajudaki.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "pessoas")

AVATAR_TONES = 6


def avatar_tone(nome):
    """Cor estável do avatar a partir do nome (mesma pessoa, mesma cor)."""
    return zlib.crc32((nome or "").encode("utf-8")) % AVATAR_TONES


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB
    # usada só para as mensagens de confirmação (flash) entre uma tela e outra
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "ajudaki-dev")
    db.init_app(app)
    app.jinja_env.globals["status_badge"] = status_badge
    app.jinja_env.filters["sem_ficticio"] = sem_ficticio
    app.jinja_env.filters["avatar_tone"] = avatar_tone
    app.jinja_env.globals["e_quem_pediu"] = e_quem_pediu
    app.jinja_env.globals["e_quem_ajuda"] = e_quem_ajuda

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    with app.app_context():
        db.create_all()
        ensure_new_columns()

    app.register_blueprint(conta_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(territorio_bp)
    app.register_blueprint(talentos_bp)
    app.register_blueprint(necessidades_bp)
    app.register_blueprint(trocas_bp)
    app.register_blueprint(organizacoes_bp)
    app.register_blueprint(impacto_bp)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)

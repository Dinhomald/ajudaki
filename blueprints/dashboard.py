from flask import Blueprint, render_template

from helpers import dashboard_summary
from models import Need

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    resumo = dashboard_summary()
    pedidos_recentes = (
        Need.query.filter_by(status="aberta").order_by(Need.created_at.desc()).limit(3).all()
    )
    return render_template("dashboard.html", resumo=resumo, pedidos_recentes=pedidos_recentes)


@dashboard_bp.route("/mais")
def mais():
    return render_template("mais.html")

from flask import Blueprint, render_template

from helpers import dashboard_summary

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    resumo = dashboard_summary()
    return render_template("dashboard.html", resumo=resumo)

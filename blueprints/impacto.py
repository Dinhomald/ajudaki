from flask import Blueprint, render_template

from helpers import impact_summary

impacto_bp = Blueprint("impacto", __name__, url_prefix="/impacto")


@impacto_bp.route("")
def index():
    resumo = impact_summary()
    return render_template("impacto.html", resumo=resumo)

from flask import Blueprint, render_template

from helpers import municipality_indicators
from models import Municipality

territorio_bp = Blueprint("territorio", __name__, url_prefix="/territorio")


@territorio_bp.route("")
def list():
    municipios = Municipality.query.order_by(Municipality.name).all()
    indicadores = [municipality_indicators(m) for m in municipios]
    return render_template("territorio.html", indicadores=indicadores)


@territorio_bp.route("/<int:municipality_id>")
def detail(municipality_id):
    municipio = Municipality.query.get_or_404(municipality_id)
    indicadores = municipality_indicators(municipio)
    return render_template("territorio_detail.html", indicadores=indicadores)

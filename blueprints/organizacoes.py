from flask import Blueprint, redirect, render_template, request, url_for

from blueprints.talentos import get_or_create_skill, parse_skill_names
from helpers import organization_hours_received
from models import Municipality, Organization, OrganizationSkill, db

organizacoes_bp = Blueprint("organizacoes", __name__, url_prefix="/organizacoes")


@organizacoes_bp.route("")
def list():
    municipio_id = request.args.get("municipio", type=int)
    area = request.args.get("area", "").strip()

    query = Organization.query
    if municipio_id:
        query = query.filter(Organization.municipality_id == municipio_id)
    if area:
        query = query.filter(Organization.area_of_action.ilike(f"%{area}%"))

    organizacoes = query.order_by(Organization.name).all()
    municipios = Municipality.query.order_by(Municipality.name).all()

    return render_template(
        "organizacoes.html",
        organizacoes=organizacoes,
        municipios=municipios,
        filtro_municipio=municipio_id,
        filtro_area=area,
    )


@organizacoes_bp.route("/nova", methods=["GET", "POST"])
def nova():
    municipios = Municipality.query.order_by(Municipality.name).all()

    if request.method == "POST":
        organizacao = Organization(
            name=request.form["name"].strip(),
            municipality_id=request.form["municipality_id"],
            area_of_action=request.form.get("area_of_action", "").strip(),
            description=request.form.get("description", "").strip(),
            status="ativa",
        )
        db.session.add(organizacao)
        db.session.flush()

        for skill_name in parse_skill_names(request.form.get("needed_skills", "")):
            skill = get_or_create_skill(skill_name)
            db.session.add(OrganizationSkill(organization_id=organizacao.id, skill_id=skill.id))

        db.session.commit()
        return redirect(url_for("organizacoes.perfil", organization_id=organizacao.id))

    return render_template("organizacao_form.html", municipios=municipios)


@organizacoes_bp.route("/<int:organization_id>")
def perfil(organization_id):
    organizacao = Organization.query.get_or_404(organization_id)
    necessidades_abertas = [n for n in organizacao.needs if n.status == "aberta"]
    horas_recebidas = organization_hours_received(organization_id)
    return render_template(
        "organizacao_perfil.html",
        organizacao=organizacao,
        necessidades_abertas=necessidades_abertas,
        horas_recebidas=horas_recebidas,
    )

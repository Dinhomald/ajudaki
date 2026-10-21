from flask import Blueprint, redirect, render_template, request, url_for

from helpers import find_matches_for_need
from models import Municipality, Need, Organization, Skill, TimeTransaction, User, db

necessidades_bp = Blueprint("necessidades", __name__, url_prefix="/necessidades")


@necessidades_bp.route("")
def list():
    municipio_id = request.args.get("municipio", type=int)
    status = request.args.get("status", "")
    habilidade = request.args.get("habilidade", "").strip()

    query = Need.query

    if municipio_id:
        query = query.filter(Need.municipality_id == municipio_id)
    if status in ("aberta", "atendida", "cancelada"):
        query = query.filter(Need.status == status)
    if habilidade:
        query = query.join(Skill, isouter=True).filter(Skill.name.ilike(f"%{habilidade}%"))

    lista = query.order_by(Need.created_at.desc()).all()
    municipios = Municipality.query.order_by(Municipality.name).all()

    return render_template(
        "necessidades.html",
        necessidades=lista,
        municipios=municipios,
        filtro_municipio=municipio_id,
        filtro_status=status,
        filtro_habilidade=habilidade,
    )


@necessidades_bp.route("/nova", methods=["GET", "POST"])
def nova():
    municipios = Municipality.query.order_by(Municipality.name).all()
    pessoas = User.query.order_by(User.public_name).all()
    organizacoes = Organization.query.order_by(Organization.name).all()

    if request.method == "POST":
        need = Need(
            title=request.form["title"].strip(),
            description=request.form.get("description", "").strip(),
            hours=float(request.form.get("hours") or 1),
            municipality_id=request.form["municipality_id"],
            location=request.form.get("location", "").strip(),
            status="aberta",
            skill_id=request.form.get("skill_id") or None,
            requester_user_id=request.form.get("requester_user_id") or None,
            requester_organization_id=request.form.get("requester_organization_id") or None,
            requester_label=request.form.get("requester_label", "").strip() or None,
        )
        db.session.add(need)
        db.session.commit()
        return redirect(url_for("necessidades.detail", need_id=need.id))

    skills = Skill.query.order_by(Skill.name).all()
    return render_template(
        "necessidade_form.html",
        municipios=municipios,
        pessoas=pessoas,
        organizacoes=organizacoes,
        skills=skills,
    )


@necessidades_bp.route("/<int:need_id>")
def detail(need_id):
    need = Need.query.get_or_404(need_id)
    ajuda_combinada = pending_transaction(need)
    recomendacoes = (
        find_matches_for_need(need) if need.status == "aberta" and not ajuda_combinada else []
    )
    recomendacoes = [r for r in recomendacoes if r["pessoa"].id != need.requester_user_id]
    # Quem pediu não pode ser escolhido para ajudar a si mesmo.
    outras_pessoas = (
        User.query.filter(User.status == "ativo", User.id != (need.requester_user_id or 0))
        .order_by(User.public_name)
        .all()
    )
    return render_template(
        "necessidade_detail.html",
        need=need,
        recomendacoes=recomendacoes,
        ajuda_combinada=ajuda_combinada,
        outras_pessoas=outras_pessoas,
        erro=request.args.get("erro"),
    )


def pending_transaction(need):
    return TimeTransaction.query.filter_by(need_id=need.id, status="pendente").first()


@necessidades_bp.route("/<int:need_id>/assumir", methods=["POST"])
def assumir(need_id):
    """
    Liga o pedido a quem vai ajudar: cria uma troca pendente com as horas
    do pedido. O crédito só entra quando a troca for confirmada.
    """
    need = Need.query.get_or_404(need_id)
    provider = User.query.get_or_404(request.form.get("provider_id", type=int))

    erro = None
    if need.status != "aberta":
        erro = "Este pedido não está mais aberto."
    elif not (need.requester_user_id or need.requester_organization_id):
        erro = "Quem pediu ainda não tem cadastro. Cadastre a pessoa ou organização e vincule ao pedido."
    elif provider.id == need.requester_user_id:
        erro = "A pessoa não pode ajudar o próprio pedido."
    elif provider.status != "ativo":
        erro = "Essa pessoa está inativa."
    elif pending_transaction(need):
        erro = "Este pedido já tem alguém combinado para ajudar."

    if erro:
        return redirect(url_for("necessidades.detail", need_id=need.id, erro=erro))

    db.session.add(
        TimeTransaction(
            provider_id=provider.id,
            requester_user_id=need.requester_user_id,
            requester_organization_id=None if need.requester_user_id else need.requester_organization_id,
            need_id=need.id,
            hours=need.hours,
            description=need.title,
            status="pendente",
        )
    )
    db.session.commit()
    return redirect(url_for("necessidades.detail", need_id=need.id))


@necessidades_bp.route("/<int:need_id>/status", methods=["POST"])
def alterar_status(need_id):
    need = Need.query.get_or_404(need_id)
    novo_status = request.form.get("status")
    if novo_status in ("aberta", "atendida", "cancelada"):
        need.status = novo_status
        db.session.commit()
    return redirect(url_for("necessidades.detail", need_id=need.id))

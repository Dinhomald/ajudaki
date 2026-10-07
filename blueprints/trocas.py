from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from models import Need, Organization, TimeTransaction, User, db

trocas_bp = Blueprint("trocas", __name__, url_prefix="/trocas")


@trocas_bp.route("")
def list():
    status = request.args.get("status", "")

    query = TimeTransaction.query
    if status in ("pendente", "concluida", "cancelada"):
        query = query.filter(TimeTransaction.status == status)

    trocas = query.order_by(TimeTransaction.created_at.desc()).all()
    return render_template("trocas.html", trocas=trocas, filtro_status=status)


@trocas_bp.route("/nova", methods=["GET", "POST"])
def nova():
    pessoas = User.query.order_by(User.public_name).all()
    organizacoes = Organization.query.order_by(Organization.name).all()
    necessidades_abertas = Need.query.filter_by(status="aberta").order_by(Need.created_at.desc()).all()

    if request.method == "POST":
        requester_user_id = request.form.get("requester_user_id") or None
        requester_organization_id = request.form.get("requester_organization_id") or None

        # Exatamente um destino (pessoa OU organização) deve ser informado.
        if bool(requester_user_id) == bool(requester_organization_id):
            erro = "Selecione exatamente um solicitante: uma pessoa OU uma organização."
            return render_template(
                "troca_form.html",
                pessoas=pessoas,
                organizacoes=organizacoes,
                necessidades_abertas=necessidades_abertas,
                erro=erro,
                form=request.form,
            )

        troca = TimeTransaction(
            provider_id=request.form["provider_id"],
            requester_user_id=requester_user_id,
            requester_organization_id=requester_organization_id,
            need_id=request.form.get("need_id") or None,
            hours=float(request.form["hours"]),
            description=request.form.get("description", "").strip(),
            status="pendente",
        )
        db.session.add(troca)
        db.session.commit()
        return redirect(url_for("trocas.list"))

    return render_template(
        "troca_form.html",
        pessoas=pessoas,
        organizacoes=organizacoes,
        necessidades_abertas=necessidades_abertas,
        erro=None,
        form={},
    )


@trocas_bp.route("/<int:troca_id>/concluir", methods=["POST"])
def concluir(troca_id):
    troca = TimeTransaction.query.get_or_404(troca_id)
    if troca.status == "pendente":
        troca.status = "concluida"
        troca.completed_at = datetime.utcnow()
        if troca.need_id:
            troca.need.status = "atendida"
        db.session.commit()
    return redirect(url_for("trocas.list"))


@trocas_bp.route("/<int:troca_id>/cancelar", methods=["POST"])
def cancelar(troca_id):
    troca = TimeTransaction.query.get_or_404(troca_id)
    if troca.status == "pendente":
        troca.status = "cancelada"
        db.session.commit()
    return redirect(url_for("trocas.list"))

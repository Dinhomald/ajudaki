"""
"Entrar como": identificação simplificada para o MVP.

A pessoa (ou organização) escolhe o próprio nome e passa a agir como ela.
Não há senha: serve para mostrar quem pode ver e fazer o quê. Num produto
real, isto viraria login com senha ou código por SMS.
"""

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from helpers import sem_ficticio
from models import Organization, User

conta_bp = Blueprint("conta", __name__)

# Telas que funcionam sem ter entrado (a própria tela de entrar e o cadastro).
LIVRES = {"conta.entrar", "conta.entrar_como", "talentos.novo", "static"}


@conta_bp.before_app_request
def carregar_quem_esta_usando():
    g.usuario = User.query.get(session["user_id"]) if session.get("user_id") else None
    g.organizacao = Organization.query.get(session["org_id"]) if session.get("org_id") else None

    if not (g.usuario or g.organizacao) and request.endpoint not in LIVRES:
        return redirect(url_for("conta.entrar"))


@conta_bp.app_context_processor
def expor_quem_esta_usando():
    return {
        "usuario": g.get("usuario"),
        "organizacao_logada": g.get("organizacao"),
        "nome_logado": sem_ficticio(
            g.usuario.public_name if g.get("usuario") else (g.organizacao.name if g.get("organizacao") else "")
        ),
    }


@conta_bp.route("/entrar")
def entrar():
    pessoas = User.query.filter_by(status="ativo").order_by(User.public_name).all()
    organizacoes = Organization.query.order_by(Organization.name).all()
    # A equipe que fez o app aparece primeiro, na mesma ordem da lateral.
    equipe = sorted(
        (p for p in pessoas if (p.photo_filename or "").startswith("equipe-")), key=lambda p: p.id
    )
    pessoas = [p for p in pessoas if p not in equipe]
    return render_template("entrar.html", equipe=equipe, pessoas=pessoas, organizacoes=organizacoes)


@conta_bp.route("/entrar", methods=["POST"])
def entrar_como():
    session.clear()
    if request.form.get("tipo") == "org":
        org = Organization.query.get_or_404(request.form.get("id", type=int))
        session["org_id"] = org.id
        nome = org.name
    else:
        pessoa = User.query.get_or_404(request.form.get("id", type=int))
        session["user_id"] = pessoa.id
        nome = pessoa.public_name
    flash(f"Olá, {sem_ficticio(nome)}! Você entrou.", "celebrar")
    return redirect(url_for("dashboard.index"))


@conta_bp.route("/sair", methods=["POST"])
def sair():
    session.clear()
    return redirect(url_for("conta.entrar"))


def entrar_como_pessoa(pessoa):
    """Usado logo depois de criar a conta, para a pessoa já entrar."""
    session.clear()
    session["user_id"] = pessoa.id


def e_quem_pediu(troca_ou_pedido):
    """A pessoa/organização logada é quem recebe a ajuda?"""
    if g.get("usuario") and troca_ou_pedido.requester_user_id == g.usuario.id:
        return True
    if g.get("organizacao") and troca_ou_pedido.requester_organization_id == g.organizacao.id:
        return True
    return False


def e_quem_ajuda(troca):
    return bool(g.get("usuario")) and troca.provider_id == g.usuario.id

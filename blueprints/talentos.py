import uuid

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from helpers import user_balance
from models import Municipality, Offer, Skill, User, UserSkill, db

talentos_bp = Blueprint("talentos", __name__, url_prefix="/talentos")

ALLOWED_PHOTO_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def get_or_create_skill(name):
    name = name.strip()
    skill = Skill.query.filter(db.func.lower(Skill.name) == name.lower()).first()
    if not skill:
        skill = Skill(name=name)
        db.session.add(skill)
        db.session.flush()
    return skill


def parse_skill_names(raw_text):
    if not raw_text:
        return []
    return [s.strip() for s in raw_text.split(",") if s.strip()]


def save_photo(file_storage):
    """Salva a foto enviada com um nome seguro e único. Retorna o nome do arquivo ou None."""
    if not file_storage or not file_storage.filename:
        return None

    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    if extension not in ALLOWED_PHOTO_EXTENSIONS:
        return None

    filename = f"{uuid.uuid4().hex}.{extension}"
    file_storage.save(f"{current_app.config['UPLOAD_FOLDER']}/{filename}")
    return filename


@talentos_bp.route("")
def list():
    municipio_id = request.args.get("municipio", type=int)
    habilidade = request.args.get("habilidade", "").strip()
    status = request.args.get("status", "")

    query = User.query

    if municipio_id:
        query = query.filter(User.municipality_id == municipio_id)
    if status in ("ativo", "inativo"):
        query = query.filter(User.status == status)
    if habilidade:
        query = (
            query.join(UserSkill)
            .join(Skill)
            .filter(UserSkill.kind == "possui")
            .filter(Skill.name.ilike(f"%{habilidade}%"))
        )

    pessoas = query.order_by(User.public_name).all()
    municipios = Municipality.query.order_by(Municipality.name).all()

    return render_template(
        "talentos.html",
        pessoas=pessoas,
        municipios=municipios,
        filtro_municipio=municipio_id,
        filtro_habilidade=habilidade,
        filtro_status=status,
    )


@talentos_bp.route("/novo", methods=["GET", "POST"])
def novo():
    municipios = Municipality.query.order_by(Municipality.name).all()

    if request.method == "POST":
        user = User(
            public_name=request.form["public_name"].strip(),
            municipality_id=request.form["municipality_id"],
            neighborhood=request.form.get("neighborhood", "").strip(),
            description=request.form.get("description", "").strip(),
            current_occupation=request.form.get("current_occupation", "").strip(),
            photo_filename=save_photo(request.files.get("photo")),
            availability=request.form.get("availability", "").strip(),
            status="ativo",
        )
        db.session.add(user)
        db.session.flush()

        for skill_name in parse_skill_names(request.form.get("skills_has", "")):
            skill = get_or_create_skill(skill_name)
            db.session.add(UserSkill(user_id=user.id, skill_id=skill.id, kind="possui"))

        for skill_name in parse_skill_names(request.form.get("skills_wants", "")):
            skill = get_or_create_skill(skill_name)
            db.session.add(UserSkill(user_id=user.id, skill_id=skill.id, kind="quer_aprender"))

        db.session.commit()
        return redirect(url_for("talentos.perfil", user_id=user.id))

    return render_template("talento_form.html", municipios=municipios)


@talentos_bp.route("/<int:user_id>")
def perfil(user_id):
    pessoa = User.query.get_or_404(user_id)
    oferecidas, recebidas, saldo = user_balance(user_id)
    return render_template(
        "talento_perfil.html",
        pessoa=pessoa,
        horas_oferecidas=oferecidas,
        horas_recebidas=recebidas,
        saldo=saldo,
    )


@talentos_bp.route("/<int:user_id>/status", methods=["POST"])
def alternar_status(user_id):
    pessoa = User.query.get_or_404(user_id)
    pessoa.status = "inativo" if pessoa.status == "ativo" else "ativo"
    db.session.commit()
    return redirect(url_for("talentos.perfil", user_id=user_id))


@talentos_bp.route("/<int:user_id>/ofertas/nova", methods=["GET", "POST"])
def nova_oferta(user_id):
    pessoa = User.query.get_or_404(user_id)
    skills = pessoa.has_skills()

    if request.method == "POST":
        oferta = Offer(
            user_id=pessoa.id,
            skill_id=request.form.get("skill_id") or None,
            title=request.form["title"].strip(),
            description=request.form.get("description", "").strip(),
            hours_available=float(request.form["hours_available"]) if request.form.get("hours_available") else None,
            status="ativa",
        )
        db.session.add(oferta)
        db.session.commit()
        return redirect(url_for("talentos.perfil", user_id=pessoa.id))

    return render_template("oferta_form.html", pessoa=pessoa, skills=skills)

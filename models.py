from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Municipality(db.Model):
    __tablename__ = "municipalities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    population = db.Column(db.Integer)
    area_km2 = db.Column(db.Float)

    users = db.relationship("User", back_populates="municipality")
    organizations = db.relationship("Organization", back_populates="municipality")
    needs = db.relationship("Need", back_populates="municipality")

    def __repr__(self):
        return f"<Municipality {self.name}>"


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<Skill {self.name}>"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    public_name = db.Column(db.String(120), nullable=False)
    municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"), nullable=False)
    neighborhood = db.Column(db.String(120))
    description = db.Column(db.Text)
    current_occupation = db.Column(db.String(150))
    photo_filename = db.Column(db.String(255))
    availability = db.Column(db.String(200))
    status = db.Column(db.String(20), nullable=False, default="ativo")  # ativo | inativo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    municipality = db.relationship("Municipality", back_populates="users")
    skills = db.relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    offers = db.relationship("Offer", back_populates="user", cascade="all, delete-orphan")
    needs = db.relationship("Need", back_populates="requester_user")

    def has_skills(self):
        return [us.skill for us in self.skills if us.kind == "possui"]

    def wants_skills(self):
        return [us.skill for us in self.skills if us.kind == "quer_aprender"]

    def active_offers(self):
        return [o for o in self.offers if o.status == "ativa"]


class UserSkill(db.Model):
    __tablename__ = "user_skills"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    kind = db.Column(db.String(20), nullable=False, default="possui")  # possui | quer_aprender

    user = db.relationship("User", back_populates="skills")
    skill = db.relationship("Skill")

    __table_args__ = (db.UniqueConstraint("user_id", "skill_id", "kind", name="uq_user_skill_kind"),)


class Offer(db.Model):
    """Serviço que a pessoa está oferecendo ativamente (distinto de apenas possuir a habilidade)."""

    __tablename__ = "offers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    hours_available = db.Column(db.Float)
    status = db.Column(db.String(20), nullable=False, default="ativa")  # ativa | pausada
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="offers")
    skill = db.relationship("Skill")


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"), nullable=False)
    area_of_action = db.Column(db.String(150))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="ativa")  # ativa | inativa
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    municipality = db.relationship("Municipality", back_populates="organizations")
    needed_skills = db.relationship("OrganizationSkill", back_populates="organization", cascade="all, delete-orphan")
    needs = db.relationship("Need", back_populates="requester_organization")


class OrganizationSkill(db.Model):
    """Habilidades que a organização costuma precisar (independente de uma necessidade pontual)."""

    __tablename__ = "organization_skills"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)

    organization = db.relationship("Organization", back_populates="needed_skills")
    skill = db.relationship("Skill")

    __table_args__ = (db.UniqueConstraint("organization_id", "skill_id", name="uq_org_skill"),)


class Need(db.Model):
    __tablename__ = "needs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    hours = db.Column(db.Float, nullable=False, default=1.0)
    municipality_id = db.Column(db.Integer, db.ForeignKey("municipalities.id"), nullable=False)
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), nullable=False, default="aberta")  # aberta | atendida | cancelada
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"))
    requester_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    requester_organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"))
    requester_label = db.Column(db.String(120))  # nome livre, quando ainda não cadastrado formalmente
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    municipality = db.relationship("Municipality", back_populates="needs")
    requester_user = db.relationship("User", back_populates="needs")
    requester_organization = db.relationship("Organization", back_populates="needs")
    skill = db.relationship("Skill")
    transactions = db.relationship("TimeTransaction", back_populates="need")

    @property
    def requester_display_name(self):
        if self.requester_user:
            return self.requester_user.public_name
        if self.requester_organization:
            return self.requester_organization.name
        return self.requester_label or "Não informado"


class TimeTransaction(db.Model):
    """
    Movimentação do Banco de Tempo. 1 hora = 1 crédito.

    provider_id sempre ganha crédito quando a troca é concluída.
    O destino é exatamente um entre requester_user_id (pessoa) e
    requester_organization_id (organização). Quando o destino é uma
    organização, ela recebe horas voluntárias, mas não possui saldo
    (não existe débito para organizações).
    """

    __tablename__ = "time_transactions"

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    requester_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    requester_organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"))
    need_id = db.Column(db.Integer, db.ForeignKey("needs.id"))
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(250))
    status = db.Column(db.String(20), nullable=False, default="pendente")  # pendente | concluida | cancelada
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    provider = db.relationship("User", foreign_keys=[provider_id])
    requester_user = db.relationship("User", foreign_keys=[requester_user_id])
    requester_organization = db.relationship("Organization")
    need = db.relationship("Need", back_populates="transactions")

    @property
    def requester_display_name(self):
        if self.requester_user:
            return self.requester_user.public_name
        if self.requester_organization:
            return self.requester_organization.name
        return "Não informado"

"""
Funções de cálculo compartilhadas entre os módulos (blueprints).

Nenhum saldo ou indicador é armazenado como coluna manual: tudo é
calculado a partir das transações e dos cadastros, conforme o
princípio de modelagem do projeto (evitar dados derivados persistidos
quando eles podem ser calculados).
"""

from sqlalchemy import func

from models import (
    Municipality,
    Need,
    Offer,
    Organization,
    Skill,
    TimeTransaction,
    User,
    UserSkill,
    db,
)


# ---------- SELOS DE STATUS (cor + texto, nunca só cor) ----------
# tone aponta para uma classe .badge-<tone> no CSS (good/warning/critical/info/muted).

STATUS_META = {
    "user": {
        "ativo": {"tone": "good", "label": "Ativo"},
        "inativo": {"tone": "muted", "label": "Inativo"},
    },
    "org": {
        "ativa": {"tone": "good", "label": "Ativa"},
        "inativa": {"tone": "muted", "label": "Inativa"},
    },
    "need": {
        "aberta": {"tone": "good", "label": "Aberto"},
        "atendida": {"tone": "info", "label": "Atendido"},
        "cancelada": {"tone": "critical", "label": "Cancelado"},
    },
    "transaction": {
        "pendente": {"tone": "warning", "label": "Pendente"},
        "concluida": {"tone": "good", "label": "Concluída"},
        "cancelada": {"tone": "critical", "label": "Cancelada"},
    },
}


def status_badge(kind, value):
    return STATUS_META[kind][value]


# ---------- BANCO DE TEMPO ----------

def user_hours_offered(user_id):
    """Horas que o usuário ganhou como prestador em trocas concluídas."""
    return (
        db.session.query(func.coalesce(func.sum(TimeTransaction.hours), 0.0))
        .filter(TimeTransaction.provider_id == user_id, TimeTransaction.status == "concluida")
        .scalar()
    )


def user_hours_received(user_id):
    """Horas que o usuário gastou como solicitante em trocas concluídas."""
    return (
        db.session.query(func.coalesce(func.sum(TimeTransaction.hours), 0.0))
        .filter(TimeTransaction.requester_user_id == user_id, TimeTransaction.status == "concluida")
        .scalar()
    )


def user_balance(user_id):
    offered = user_hours_offered(user_id)
    received = user_hours_received(user_id)
    return offered, received, offered - received


def organization_hours_received(organization_id):
    return (
        db.session.query(func.coalesce(func.sum(TimeTransaction.hours), 0.0))
        .filter(
            TimeTransaction.requester_organization_id == organization_id,
            TimeTransaction.status == "concluida",
        )
        .scalar()
    )


def total_hours_completed(municipality_id=None):
    query = db.session.query(func.coalesce(func.sum(TimeTransaction.hours), 0.0)).filter(
        TimeTransaction.status == "concluida"
    )
    if municipality_id:
        query = query.join(User, TimeTransaction.provider_id == User.id).filter(
            User.municipality_id == municipality_id
        )
    return query.scalar()


def total_hours_available(municipality_id=None):
    query = db.session.query(func.coalesce(func.sum(Offer.hours_available), 0.0)).filter(
        Offer.status == "ativa"
    )
    if municipality_id:
        query = query.join(User, Offer.user_id == User.id).filter(User.municipality_id == municipality_id)
    return query.scalar()


# ---------- MATCHING (determinístico e explicável) ----------

def find_matches_for_need(need, limit=10):
    """
    Fluxo: NECESSIDADE -> BUSCA POR HABILIDADE -> PESSOAS COMPATÍVEIS -> FILTROS -> RECOMENDAÇÕES

    Critérios, em ordem de prioridade:
      1. Compatibilidade da habilidade (obrigatório, quando a necessidade tem habilidade definida)
      2. Mesmo município
      3. Disponibilidade informada
      4. Status ativo (obrigatório)
      5. Nome (desempate estável)
    """
    query = User.query.filter(User.status == "ativo")

    if need.skill_id:
        query = query.join(UserSkill).filter(
            UserSkill.kind == "possui", UserSkill.skill_id == need.skill_id
        )
    else:
        return []

    candidatos = query.all()

    resultados = []
    for pessoa in candidatos:
        mesmo_municipio = pessoa.municipality_id == need.municipality_id
        tem_disponibilidade = bool(pessoa.availability)

        motivos = [f"Possui a habilidade '{need.skill.name}'"]
        if mesmo_municipio:
            motivos.append(f"Mesmo município ({pessoa.municipality.name})")
        if tem_disponibilidade:
            motivos.append(f"Disponibilidade informada: {pessoa.availability}")
        motivos.append("Status ativo")

        resultados.append(
            {
                "pessoa": pessoa,
                "motivos": motivos,
                "sort_key": (
                    0 if mesmo_municipio else 1,
                    0 if tem_disponibilidade else 1,
                    pessoa.public_name.lower(),
                ),
            }
        )

    resultados.sort(key=lambda r: r["sort_key"])
    return resultados[:limit]


# ---------- INDICADORES ----------

def activation_index(municipality_id=None):
    """
    Índice de Ativação Comunitária = (pessoas ativas + organizações ativas)
    / (pessoas cadastradas + organizações cadastradas) * 100

    Metodologia simples e documentada, conforme item 9 do escopo do MVP.
    """
    users_q = User.query
    orgs_q = Organization.query
    if municipality_id:
        users_q = users_q.filter(User.municipality_id == municipality_id)
        orgs_q = orgs_q.filter(Organization.municipality_id == municipality_id)

    total_users = users_q.count()
    active_users = users_q.filter(User.status == "ativo").count()
    total_orgs = orgs_q.count()
    active_orgs = orgs_q.filter(Organization.status == "ativa").count()

    total = total_users + total_orgs
    active = active_users + active_orgs
    percentual = round((active / total) * 100, 1) if total else 0.0

    return {
        "percentual": percentual,
        "pessoas_cadastradas": total_users,
        "pessoas_ativas": active_users,
        "organizacoes_cadastradas": total_orgs,
        "organizacoes_ativas": active_orgs,
    }


def municipality_indicators(municipality):
    pessoas_cadastradas = User.query.filter_by(municipality_id=municipality.id).count()
    organizacoes = Organization.query.filter_by(municipality_id=municipality.id).count()
    necessidades_abertas = Need.query.filter_by(municipality_id=municipality.id, status="aberta").count()
    necessidades_atendidas = Need.query.filter_by(municipality_id=municipality.id, status="atendida").count()
    trocas_realizadas = (
        db.session.query(TimeTransaction)
        .join(User, TimeTransaction.provider_id == User.id)
        .filter(User.municipality_id == municipality.id, TimeTransaction.status == "concluida")
        .count()
    )

    return {
        "municipio": municipality,
        "pessoas_cadastradas": pessoas_cadastradas,
        "organizacoes": organizacoes,
        "horas_disponiveis": total_hours_available(municipality.id),
        "horas_trocadas": total_hours_completed(municipality.id),
        "necessidades_abertas": necessidades_abertas,
        "necessidades_atendidas": necessidades_atendidas,
        "trocas_realizadas": trocas_realizadas,
        "ativacao": activation_index(municipality.id),
    }


def top_skills_by_offer(limit=5):
    return (
        db.session.query(Skill.name, func.count(Offer.id).label("total"))
        .join(Offer, Offer.skill_id == Skill.id)
        .filter(Offer.status == "ativa")
        .group_by(Skill.name)
        .order_by(func.count(Offer.id).desc())
        .limit(limit)
        .all()
    )


def top_skills_by_need(limit=5):
    return (
        db.session.query(Skill.name, func.count(Need.id).label("total"))
        .join(Need, Need.skill_id == Skill.id)
        .group_by(Skill.name)
        .order_by(func.count(Need.id).desc())
        .limit(limit)
        .all()
    )


def trocas_por_mes(limit=6):
    rows = (
        db.session.query(
            func.strftime("%Y-%m", TimeTransaction.completed_at).label("mes"),
            func.count(TimeTransaction.id).label("total"),
            func.coalesce(func.sum(TimeTransaction.hours), 0.0).label("horas"),
        )
        .filter(TimeTransaction.status == "concluida")
        .group_by("mes")
        .order_by("mes")
        .all()
    )
    return rows[-limit:]


def dashboard_summary():
    return {
        "pessoas": User.query.count(),
        "pessoas_ativas": User.query.filter_by(status="ativo").count(),
        "organizacoes": Organization.query.count(),
        "horas_disponiveis": total_hours_available(),
        "horas_trocadas": total_hours_completed(),
        "necessidades_abertas": Need.query.filter_by(status="aberta").count(),
        "necessidades_atendidas": Need.query.filter_by(status="atendida").count(),
        "top_habilidades_ofertadas": top_skills_by_offer(),
        "top_habilidades_procuradas": top_skills_by_need(),
        "evolucao_trocas": trocas_por_mes(),
        "ativacao": activation_index(),
    }


def impact_summary():
    conexoes_realizadas = TimeTransaction.query.filter_by(status="concluida").count()
    return {
        "pessoas_conectadas": User.query.count(),
        "organizacoes": Organization.query.count(),
        "horas_oferecidas": total_hours_available(),
        "horas_trocadas": total_hours_completed(),
        "conexoes_realizadas": conexoes_realizadas,
        "necessidades_atendidas": Need.query.filter_by(status="atendida").count(),
        "evolucao_trocas": trocas_por_mes(),
    }

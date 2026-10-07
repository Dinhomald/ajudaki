"""
Popula o banco com dados FICTICIOS para desenvolvimento.
Execute: python seed.py

Nenhum numero aqui representa uma fonte oficial. Todos os registros
sao identificados como "(dado ficticio)" para deixar isso explicito
no ambiente de desenvolvimento.
"""

from datetime import datetime, timedelta

from app import create_app
from models import (
    Municipality,
    Need,
    Offer,
    Organization,
    OrganizationSkill,
    Skill,
    TimeTransaction,
    User,
    UserSkill,
    db,
)

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    caxias = Municipality(name="Caxias do Sul", population=520000, area_km2=1650.0)
    farroupilha = Municipality(name="Farroupilha", population=89000, area_km2=380.0)
    bento = Municipality(name="Bento Gonçalves", population=125000, area_km2=275.0)
    db.session.add_all([caxias, farroupilha, bento])
    db.session.flush()

    nomes_habilidades = [
        "Excel", "Power BI", "Informática", "Manutenção de computadores",
        "Inglês", "Matemática", "Design gráfico", "Redes sociais",
        "Direito básico", "Costura", "Culinária", "Marcenaria",
    ]
    skills = {nome: Skill(name=nome) for nome in nomes_habilidades}
    db.session.add_all(skills.values())
    db.session.flush()

    pessoas_mock = [
        {
            "public_name": "João (dado fictício)",
            "municipality": caxias,
            "neighborhood": "Sagrada Família",
            "description": "Técnico em informática, gosta de ensinar.",
            "availability": "Sábados à tarde",
            "status": "ativo",
            "possui": ["Excel", "Power BI", "Informática", "Manutenção de computadores"],
            "quer_aprender": ["Inglês"],
            "ofertas": [
                {"title": "Manutenção de notebooks", "skill": "Manutenção de computadores", "hours": 2},
            ],
        },
        {
            "public_name": "Maria (dado fictício)",
            "municipality": caxias,
            "neighborhood": "Centro",
            "description": "Professora aposentada, oferece aulas de Excel.",
            "availability": "Quarta-feira à noite",
            "status": "ativo",
            "possui": ["Excel", "Matemática"],
            "quer_aprender": ["Design gráfico"],
            "ofertas": [
                {"title": "Aulas de Excel", "skill": "Excel", "hours": 2},
            ],
        },
        {
            "public_name": "Ana (dado fictício)",
            "municipality": farroupilha,
            "neighborhood": "São Pelegrino",
            "description": "Designer freelancer, ajuda organizações locais.",
            "availability": "Fins de semana",
            "status": "ativo",
            "possui": ["Design gráfico", "Redes sociais"],
            "quer_aprender": ["Direito básico"],
            "ofertas": [
                {"title": "Consultoria de identidade visual", "skill": "Design gráfico", "hours": 3},
            ],
        },
        {
            "public_name": "Pedro (dado fictício)",
            "municipality": bento,
            "neighborhood": "Rondônia",
            "description": "Advogado voluntário, atua com direito de família.",
            "availability": "Terças-feiras",
            "status": "ativo",
            "possui": ["Direito básico"],
            "quer_aprender": ["Informática"],
            "ofertas": [
                {"title": "Orientação jurídica básica", "skill": "Direito básico", "hours": 1},
            ],
        },
        {
            "public_name": "Beatriz (dado fictício)",
            "municipality": caxias,
            "neighborhood": "Kayser",
            "description": "Costureira, também cozinha para eventos comunitários.",
            "availability": "Manhãs",
            "status": "ativo",
            "possui": ["Costura", "Culinária"],
            "quer_aprender": [],
            "ofertas": [
                {"title": "Aulas de costura básica", "skill": "Costura", "hours": 2},
            ],
        },
        {
            "public_name": "Carlos (dado fictício)",
            "municipality": bento,
            "neighborhood": "Centro",
            "description": "Marceneiro, atualmente sem disponibilidade.",
            "availability": "",
            "status": "inativo",
            "possui": ["Marcenaria"],
            "quer_aprender": [],
            "ofertas": [],
        },
    ]

    usuarios = {}
    for dados in pessoas_mock:
        user = User(
            public_name=dados["public_name"],
            municipality_id=dados["municipality"].id,
            neighborhood=dados["neighborhood"],
            description=dados["description"],
            availability=dados["availability"],
            status=dados["status"],
        )
        db.session.add(user)
        db.session.flush()
        for nome in dados["possui"]:
            db.session.add(UserSkill(user_id=user.id, skill_id=skills[nome].id, kind="possui"))
        for nome in dados["quer_aprender"]:
            db.session.add(UserSkill(user_id=user.id, skill_id=skills[nome].id, kind="quer_aprender"))
        for oferta in dados["ofertas"]:
            db.session.add(
                Offer(
                    user_id=user.id,
                    skill_id=skills[oferta["skill"]].id,
                    title=oferta["title"] + " (dado fictício)",
                    hours_available=oferta["hours"],
                    status="ativa",
                )
            )
        usuarios[dados["public_name"]] = user

    db.session.flush()

    organizacoes_mock = [
        {
            "name": "OSC Esperança (fictícia)",
            "municipality": caxias,
            "area_of_action": "Educação",
            "description": "Atua com educação comunitária e inclusão digital.",
            "status": "ativa",
            "needed_skills": ["Informática", "Design gráfico"],
        },
        {
            "name": "OSC Nova Geração (fictícia)",
            "municipality": bento,
            "area_of_action": "Educação",
            "description": "Reforço escolar para adolescentes.",
            "status": "ativa",
            "needed_skills": ["Matemática", "Direito básico"],
        },
        {
            "name": "Coletivo Raízes (fictício)",
            "municipality": farroupilha,
            "area_of_action": "Comunicação comunitária",
            "description": "Campanhas de arrecadação e mobilização local.",
            "status": "inativa",
            "needed_skills": ["Redes sociais"],
        },
    ]

    organizacoes = {}
    for dados in organizacoes_mock:
        org = Organization(
            name=dados["name"],
            municipality_id=dados["municipality"].id,
            area_of_action=dados["area_of_action"],
            description=dados["description"],
            status=dados["status"],
        )
        db.session.add(org)
        db.session.flush()
        for nome in dados["needed_skills"]:
            db.session.add(OrganizationSkill(organization_id=org.id, skill_id=skills[nome].id))
        organizacoes[dados["name"]] = org

    db.session.flush()

    necessidades_mock = [
        {
            "title": "Aulas básicas de informática (dado fictício)",
            "description": "Turma de idosos precisa aprender o essencial de computador.",
            "hours": 4,
            "municipality": caxias,
            "location": "Sede da OSC Esperança",
            "skill": "Informática",
            "requester_organization": "OSC Esperança (fictícia)",
            "status": "aberta",
        },
        {
            "title": "Manutenção de dois notebooks (dado fictício)",
            "description": "Notebooks lentos, precisam de formatação e limpeza.",
            "hours": 2,
            "municipality": caxias,
            "location": "Centro",
            "skill": "Manutenção de computadores",
            "requester_user": "Maria (dado fictício)",
            "status": "atendida",
        },
        {
            "title": "Professor de matemática (dado fictício)",
            "description": "Reforço escolar para adolescentes.",
            "hours": 3,
            "municipality": bento,
            "location": "Sede da OSC Nova Geração",
            "skill": "Matemática",
            "requester_organization": "OSC Nova Geração (fictícia)",
            "status": "aberta",
        },
        {
            "title": "Ajuda com redes sociais (dado fictício)",
            "description": "Organização quer divulgar campanha de arrecadação.",
            "hours": 2,
            "municipality": farroupilha,
            "location": "Sede da organização",
            "skill": "Redes sociais",
            "requester_organization": "Coletivo Raízes (fictício)",
            "status": "aberta",
        },
    ]

    needs_by_title = {}
    for dados in necessidades_mock:
        need = Need(
            title=dados["title"],
            description=dados["description"],
            hours=dados["hours"],
            municipality_id=dados["municipality"].id,
            location=dados["location"],
            status=dados["status"],
            skill_id=skills[dados["skill"]].id if dados.get("skill") else None,
            requester_user_id=usuarios[dados["requester_user"]].id if dados.get("requester_user") else None,
            requester_organization_id=(
                organizacoes[dados["requester_organization"]].id
                if dados.get("requester_organization")
                else None
            ),
        )
        db.session.add(need)
        db.session.flush()
        needs_by_title[dados["title"]] = need

    now = datetime.utcnow()

    transacoes_mock = [
        # Exemplo do próprio escopo: Maria oferece Excel, João solicita 1h -> Maria +1h, João -1h
        {
            "provider": "Maria (dado fictício)",
            "requester_user": "João (dado fictício)",
            "hours": 1,
            "description": "1h de aulas de Excel (dado fictício)",
            "status": "concluida",
            "completed_at": now - timedelta(days=20),
        },
        {
            "provider": "João (dado fictício)",
            "requester_user": "Ana (dado fictício)",
            "hours": 2,
            "description": "Manutenção de notebook (dado fictício)",
            "need_title": "Manutenção de dois notebooks (dado fictício)",
            "status": "concluida",
            "completed_at": now - timedelta(days=10),
        },
        {
            "provider": "Ana (dado fictício)",
            "requester_organization": "OSC Esperança (fictícia)",
            "hours": 2,
            "description": "Apoio com peças gráficas para campanha (dado fictício)",
            "status": "concluida",
            "completed_at": now - timedelta(days=3),
        },
        {
            "provider": "Pedro (dado fictício)",
            "requester_organization": "OSC Nova Geração (fictícia)",
            "hours": 1,
            "description": "Orientação jurídica básica (dado fictício)",
            "status": "pendente",
        },
        {
            "provider": "Beatriz (dado fictício)",
            "requester_user": "Maria (dado fictício)",
            "hours": 1,
            "description": "Aula de costura básica (dado fictício)",
            "status": "pendente",
        },
    ]

    for dados in transacoes_mock:
        db.session.add(
            TimeTransaction(
                provider_id=usuarios[dados["provider"]].id,
                requester_user_id=usuarios[dados["requester_user"]].id if dados.get("requester_user") else None,
                requester_organization_id=(
                    organizacoes[dados["requester_organization"]].id
                    if dados.get("requester_organization")
                    else None
                ),
                need_id=needs_by_title[dados["need_title"]].id if dados.get("need_title") else None,
                hours=dados["hours"],
                description=dados["description"],
                status=dados["status"],
                completed_at=dados.get("completed_at"),
            )
        )

    db.session.commit()
    print("Banco populado com dados ficticios em ajudaki.db")

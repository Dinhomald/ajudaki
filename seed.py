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
    garibaldi = Municipality(name="Garibaldi", population=35000, area_km2=169.0)
    flores = Municipality(name="Flores da Cunha", population=31000, area_km2=273.0)
    db.session.add_all([caxias, farroupilha, bento, garibaldi, flores])
    db.session.flush()

    nomes_habilidades = [
        "Excel", "Power BI", "Informática", "Manutenção de computadores",
        "Inglês", "Matemática", "Design gráfico", "Redes sociais",
        "Direito básico", "Costura", "Culinária", "Marcenaria",
        "Violão", "Jardinagem", "Português", "Fotografia",
        "Elétrica básica", "Cuidados com idosos",
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

    # Mais pessoas, em formato compacto, para os indicadores variarem entre cidades:
    # (nome, cidade, bairro, descrição, disponibilidade, status, possui, quer aprender, ofertas)
    pessoas_extra = [
        ("Lucas", caxias, "Pio X", "Estudante de Letras, dá aulas particulares.", "Sábados de manhã", "ativo",
         ["Inglês", "Português"], ["Violão"], [("Conversação em inglês", "Inglês", 3), ("Reforço de português", "Português", 2)]),
        ("Fernanda", caxias, "Exposição", "Analista de dados, adora planilhas.", "Segundas à noite", "ativo",
         ["Excel", "Power BI"], ["Fotografia"], [("Excel para pequenos negócios", "Excel", 2), ("Planilha de controle de doações", "Excel", 2)]),
        ("Rafael", caxias, "São Pelegrino", "Eletricista, ajuda em reformas comunitárias.", "Domingos", "ativo",
         ["Elétrica básica", "Marcenaria"], [], [("Pequenos reparos elétricos", "Elétrica básica", 4)]),
        ("Juliana", caxias, "Cinquentenário", "Enfermeira, cuida de idosos no bairro.", "Quintas à tarde", "ativo",
         ["Cuidados com idosos", "Culinária"], ["Inglês"], [("Acompanhamento de idosos", "Cuidados com idosos", 3)]),
        ("Thiago", caxias, "Santa Catarina", "Fotógrafo, registra eventos de ONGs.", "Fins de semana", "ativo",
         ["Fotografia", "Redes sociais"], ["Power BI"], [("Fotos para campanhas", "Fotografia", 3)]),
        ("Patrícia", caxias, "Desvio Rizzo", "Cozinheira, organiza almoços beneficentes.", "", "inativo",
         ["Culinária"], [], []),
        ("Gabriel", farroupilha, "Centro", "Estudante de engenharia, monta e conserta computadores.", "Sextas à tarde", "ativo",
         ["Informática", "Manutenção de computadores", "Matemática"], ["Inglês"], [("Formatação de computadores", "Manutenção de computadores", 2)]),
        ("Helena", farroupilha, "Volta Grande", "Jardineira, cuida de hortas comunitárias.", "Manhãs", "ativo",
         ["Jardinagem", "Culinária"], ["Redes sociais"], [("Montagem de horta", "Jardinagem", 4)]),
        ("Marcos", farroupilha, "Imigrante", "Músico, ensina violão para crianças.", "", "inativo",
         ["Violão"], [], []),
        ("Camila", bento, "Cidade Alta", "Professora de matemática e português.", "Terças e quintas", "ativo",
         ["Matemática", "Português"], ["Excel"], [("Reforço de matemática", "Matemática", 3)]),
        ("Diego", bento, "Botafogo", "Designer, faz identidade visual para ONGs.", "Noites", "ativo",
         ["Design gráfico", "Fotografia"], [], [("Logos para projetos sociais", "Design gráfico", 2)]),
        ("Sofia", bento, "Juventude", "Aposentada, costura para doação.", "Tardes", "ativo",
         ["Costura"], ["Informática"], [("Ajustes de roupas", "Costura", 2)]),
        ("Eduardo", garibaldi, "Centro", "Agricultor, ensina técnicas de plantio.", "Domingos", "ativo",
         ["Jardinagem"], ["Informática"], [("Oficina de plantio", "Jardinagem", 3)]),
        ("Larissa", garibaldi, "São José", "Estudante, ajuda com celular e redes sociais.", "", "inativo",
         ["Redes sociais", "Informática"], [], []),
        ("Roberto", garibaldi, "Champagne", "Eletricista aposentado.", "", "inativo",
         ["Elétrica básica"], [], []),
        ("Vitória", flores, "Centro", "Cuidadora de idosos.", "Fins de semana", "ativo",
         ["Cuidados com idosos"], ["Culinária"], [("Visitas a idosos", "Cuidados com idosos", 4)]),
        ("André", flores, "São Cristóvão", "Professor de violão e inglês.", "Quartas à noite", "ativo",
         ["Violão", "Inglês"], [], [("Aulas de violão", "Violão", 2)]),
    ]
    for nome, cidade, bairro, descricao, disp, status, possui, quer, ofertas in pessoas_extra:
        pessoas_mock.append(
            {
                "public_name": f"{nome} (dado fictício)",
                "municipality": cidade,
                "neighborhood": bairro,
                "description": descricao,
                "availability": disp,
                "status": status,
                "possui": possui,
                "quer_aprender": quer,
                "ofertas": [{"title": t, "skill": s, "hours": h} for t, s, h in ofertas],
            }
        )

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
        {
            "name": "Lar dos Idosos Bem Viver (fictício)",
            "municipality": caxias,
            "area_of_action": "Assistência a idosos",
            "description": "Acolhe idosos e organiza atividades de convivência.",
            "status": "ativa",
            "needed_skills": ["Cuidados com idosos", "Culinária", "Fotografia"],
        },
        {
            "name": "Horta Comunitária Garibaldi (fictícia)",
            "municipality": garibaldi,
            "area_of_action": "Meio ambiente",
            "description": "Horta coletiva parada desde o último inverno.",
            "status": "inativa",
            "needed_skills": ["Jardinagem"],
        },
        {
            "name": "Projeto Música na Praça (fictício)",
            "municipality": flores,
            "area_of_action": "Cultura",
            "description": "Aulas de música gratuitas na praça central.",
            "status": "ativa",
            "needed_skills": ["Violão", "Redes sociais", "Fotografia"],
        },
        {
            "name": "Associação de Moradores do Centro (fictícia)",
            "municipality": bento,
            "area_of_action": "Moradia e bairro",
            "description": "Cuida do salão comunitário e de melhorias no bairro.",
            "status": "ativa",
            "needed_skills": ["Elétrica básica", "Marcenaria"],
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

    # Mais pedidos: (título, descrição, horas, cidade, local, habilidade, quem pede, status).
    # "Quem pede" é o nome curto de uma pessoa ou o nome completo de uma organização.
    lar = "Lar dos Idosos Bem Viver (fictício)"
    musica = "Projeto Música na Praça (fictício)"
    necessidades_extra = [
        ("Curso de Excel para mães empreendedoras", "Controle de vendas e estoque em planilha.", 6, caxias,
         "Sede da OSC Esperança", "Excel", "OSC Esperança (fictícia)", "aberta"),
        ("Ajuda com planilha de doações", "Organizar entradas e saídas de doações.", 2, caxias,
         "Cinquentenário", "Excel", "Juliana", "aberta"),
        ("Fotos para campanha do agasalho", "Registrar a entrega de cobertores.", 3, caxias,
         "Lar Bem Viver", "Fotografia", lar, "atendida"),
        ("Companhia para idosos aos domingos", "Conversa e passeio com os moradores do lar.", 4, caxias,
         "Lar Bem Viver", "Cuidados com idosos", lar, "aberta"),
        ("Almoço beneficente de inverno", "Preparar almoço para 80 pessoas.", 5, caxias,
         "Salão paroquial", "Culinária", lar, "atendida"),
        ("Formatar computador da escola", "Computador do laboratório não liga direito.", 2, farroupilha,
         "Escola municipal", "Manutenção de computadores", "Helena", "atendida"),
        ("Oficina de informática para jovens", "Primeiros passos com computador e e-mail.", 4, farroupilha,
         "Centro comunitário", "Informática", "Coletivo Raízes (fictício)", "aberta"),
        ("Inclusão digital para agricultores", "Usar celular para vender a produção.", 4, garibaldi,
         "Sindicato rural", "Informática", "Eduardo", "aberta"),
        ("Revitalizar horta comunitária", "Preparar canteiros e replantar.", 6, garibaldi,
         "Horta Comunitária", "Jardinagem", "Horta Comunitária Garibaldi (fictícia)", "aberta"),
        ("Reparos elétricos no salão", "Trocar tomadas e lâmpadas do salão.", 3, bento,
         "Salão comunitário", "Elétrica básica", "Associação de Moradores do Centro (fictícia)", "aberta"),
        ("Reforço de português", "Leitura e redação para o 9º ano.", 4, bento,
         "Sede da OSC Nova Geração", "Português", "OSC Nova Geração (fictícia)", "atendida"),
        ("Aulas de inglês para adolescentes", "Turma de sábado, nível básico.", 3, bento,
         "Sede da OSC Nova Geração", "Inglês", "OSC Nova Geração (fictícia)", "cancelada"),
        ("Aulas de violão na praça", "Turma infantil aos sábados.", 4, flores,
         "Praça central", "Violão", musica, "aberta"),
        ("Divulgação do festival de música", "Posts e stories para o festival de verão.", 2, flores,
         "Praça central", "Redes sociais", musica, "aberta"),
    ]
    for titulo, descricao, horas, cidade, local, habilidade, quem, status in necessidades_extra:
        pedido = {
            "title": f"{titulo} (dado fictício)",
            "description": descricao,
            "hours": horas,
            "municipality": cidade,
            "location": local,
            "skill": habilidade,
            "status": status,
        }
        if quem in organizacoes:
            pedido["requester_organization"] = quem
        else:
            pedido["requester_user"] = f"{quem} (dado fictício)"
        necessidades_mock.append(pedido)

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

    # Mais trocas, espalhadas pelos últimos meses (a rede crescendo):
    # (quem ajudou, quem recebeu, horas, descrição, status, dias atrás, pedido relacionado)
    trocas_extra = [
        ("Fernanda", "OSC Esperança (fictícia)", 2, "Oficina de Excel", "concluida", 165, None),
        ("Lucas", "Camila", 1, "Conversação em inglês", "concluida", 150, None),
        ("Juliana", lar, 3, "Acompanhamento de idosos", "concluida", 130, None),
        ("Gabriel", "Helena", 2, "Formatação do computador da escola", "concluida", 120, "Formatar computador da escola"),
        ("Thiago", lar, 3, "Fotos da campanha do agasalho", "concluida", 100, "Fotos para campanha do agasalho"),
        ("Beatriz", lar, 4, "Almoço beneficente de inverno", "concluida", 90, "Almoço beneficente de inverno"),
        ("Camila", "OSC Nova Geração (fictícia)", 4, "Reforço de português", "concluida", 75, "Reforço de português"),
        ("Rafael", "Associação de Moradores do Centro (fictícia)", 3, "Troca de tomadas", "concluida", 70, None),
        ("Diego", musica, 2, "Cartaz do festival", "concluida", 60, None),
        ("Helena", "Eduardo", 3, "Oficina de compostagem", "concluida", 50, None),
        ("Ana", "Diego", 1, "Dicas de redes sociais", "concluida", 40, None),
        ("Vitória", lar, 4, "Visitas aos idosos", "concluida", 30, None),
        ("André", musica, 2, "Aula de violão aberta", "concluida", 22, None),
        ("Maria", "Juliana", 1, "Excel básico", "concluida", 18, None),
        ("João", "OSC Esperança (fictícia)", 3, "Configuração da sala de informática", "concluida", 12, None),
        ("Lucas", "OSC Esperança (fictícia)", 2, "Inglês para crianças", "concluida", 1, None),
        ("Sofia", "OSC Nova Geração (fictícia)", 2, "Ajuste de uniformes", "concluida", 2, None),
        ("André", musica, 4, "Aulas de violão na praça", "pendente", None, "Aulas de violão na praça"),
        ("Juliana", lar, 2, "Companhia para idosos", "pendente", None, None),
        ("Lucas", "OSC Nova Geração (fictícia)", 3, "Aulas de inglês", "cancelada", None, "Aulas de inglês para adolescentes"),
    ]
    for quem, para, horas, descricao, status, dias, pedido in trocas_extra:
        troca = {
            "provider": f"{quem} (dado fictício)",
            "hours": horas,
            "description": f"{descricao} (dado fictício)",
            "status": status,
        }
        if dias is not None:
            troca["completed_at"] = now - timedelta(days=dias)
        if pedido:
            troca["need_title"] = f"{pedido} (dado fictício)"
        if para in organizacoes:
            troca["requester_organization"] = para
        else:
            troca["requester_user"] = f"{para} (dado fictício)"
        transacoes_mock.append(troca)

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
                # data de criação coerente com a conclusão, para a lista ficar em ordem
                created_at=dados["completed_at"] - timedelta(days=2) if dados.get("completed_at") else now,
            )
        )

    db.session.commit()
    print("Banco populado com dados ficticios em ajudaki.db")

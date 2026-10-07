# Ajudaki — MVP

Projeto desenvolvido dentro do SESI para apresentação.

Rede de Recursos Comunitários. Backend em Python (Flask + SQLAlchemy +
SQLite), visualização em HTML/CSS renderizado no servidor (Jinja2).

## Como rodar

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed.py                 # popula dados fictícios de desenvolvimento
python app.py                  # http://127.0.0.1:5000
```

## Estrutura

```
app.py            # cria a aplicação Flask e registra os blueprints
models.py         # modelo de dados (SQLAlchemy)
helpers.py        # cálculos: saldo, matching, indicadores
blueprints/       # uma rota por módulo de funcionalidade
templates/        # HTML (Jinja2)
static/css/       # CSS
seed.py           # dados fictícios para desenvolvimento
```

## Funcionalidades implementadas

- **Talentos**: cadastro de pessoas, habilidades (possui/deseja aprender),
  ofertas de serviço, busca por habilidade/município/status.
- **Necessidades**: publicação por pessoa ou organização, busca/filtros,
  matching determinístico e explicável (habilidade → município →
  disponibilidade → status ativo).
- **Banco de Tempo**: solicitar/concluir/cancelar trocas (1h = 1 crédito).
  Saldo sempre calculado a partir das transações concluídas, nunca
  armazenado manualmente.
- **Organizações**: cadastro, habilidades geralmente necessárias,
  necessidades publicadas, horas voluntárias recebidas.
- **Território**: indicadores por município (pessoas, organizações, horas
  disponíveis/trocadas, necessidades) e Índice de Ativação Comunitária.
- **Dashboard e Impacto**: visão geral agregada e evolução mensal das
  trocas concluídas.

## Fora deste MVP (deferido para uma fase futura)

- Mapa interativo (Leaflet/GeoJSON).
- Índice de Privatização Territorial com fonte de dados real (o
  documento de origem exige registrar fonte, metodologia e limitações
  antes de apresentar esse indicador — não faz sentido simulá-lo).
- Autenticação/autorização completa.

Todos os dados de pessoas, organizações, ofertas e necessidades são
fictícios e claramente identificados como tal (sufixo "dado fictício").

# 🛡️ Churn Prediction Pipeline

![CI](https://github.com/Diego-Math1/projeto_sql/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![dbt](https://img.shields.io/badge/dbt-1.12-orange)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![MLflow](https://img.shields.io/badge/MLflow-3.17-blue)

Um pipeline completo de Engenharia e Ciência de Dados construído de ponta a ponta para prever o cancelamento de clientes (Churn). O projeto vai desde a ingestão de dados brutos e modelagem SQL até o treinamento, versionamento do modelo e disponibilização via API.

## 🎯 O Problema de Negócio
Em empresas de assinatura, reter um cliente é muito mais barato do que adquirir um novo. O objetivo deste projeto é prever quais clientes têm alta probabilidade de cancelar o serviço, permitindo que o time de retenção aja de forma proativa com ofertas e atendimento focado.

## 🏗️ Arquitetura da Solução

O pipeline foi desenhado seguindo as melhores práticas de engenharia, com separação clara de responsabilidades:

```text
[ Python / Faker ] ──> Gera dados sintéticos (1000 clientes)
       │
       ▼
[ PostgreSQL ] ───────> Armazena os dados brutos (raw_clientes, raw_compras, raw_eventos)
       │
       ▼
[ dbt (Data Build Tool) ] ──> Transformação em camadas (Staging -> Intermediate -> Marts)
       │
       ▼
[ Scikit-Learn ] ─────> Treinamento do modelo preditivo (Random Forest)
       │
       ▼
[ MLflow ] ───────────> Rastreamento de experimentos e Model Registry (versionamento)
       │
       ▼
[ FastAPI ] ──────────> Serving do modelo via API RESTful

🛠️ Tecnologias Utilizadas
Infraestrutura: Docker, Docker Compose

Banco de Dados: PostgreSQL 16

Transformação de Dados (ELT): dbt-core

Machine Learning: Scikit-Learn, Pandas, Numpy

MLOps: MLflow (Tracking & Model Registry)

API: FastAPI, Uvicorn, Pydantic

CI/CD: GitHub Actions, Ruff (Linter)

📊 Modelagem e Resultados
Algoritmo: Random Forest Classifier (100 árvores, max_depth=10).

Métricas no conjunto de teste: Acurácia 98.5%, Precisão 100%, Recall 96.4%, ROC-AUC 1.000.

⚠️ Nota sobre os dados sintéticos: O dataset foi gerado com uma regra determinística de churn embutida no comportamento dos clientes (ex: clientes com alta recência e muitos tickets são churn). Por isso, as métricas atingiram a perfeição. Em dados reais de mercado, o esperado para este tipo de problema é um ROC-AUC entre 0.75 e 0.85.

🚀 Como Executar o Projeto
1. Pré-requisitos
Python 3.11+

Docker e Docker Compose instalados e rodando.
2. Clonar e Preparar o Ambiente
```bash
git clone https://github.com/Diego-Math1/projeto_sql.git
cd projeto_sql
python -m venv .venv
source .venv/Scripts/activate  # No Windows (Git Bash)
# source .venv/bin/activate    # No Linux/Mac
pip install -r requirements.txt
```
3. Subir a Infraestrutura e Gerar os Dados
```bash
# Sobe o banco e o MLflow
docker compose up -d

# Gera os dados sintéticos e popula o Postgres
python ingestion/seed.py
```

4. Transformar os Dados com dbt
```bash
cd dbt_project
dbt run   # Cria as views e tabelas
dbt test  # Roda os testes de qualidade de dados
cd ..
```
5. Treinar e Registrar o Modelo
```bash
python ml/train.py
```
6. Rodar a API e Previsão
```bash
uvicorn api.main:app --reload
```
Acesse a documentação interativa (Swagger UI) em: http://localhost:8000/docs

```text
├── .github/workflows/  # Pipeline de CI (Ruff + dbt test)
├── api/                # API FastAPI para servir o modelo
├── dbt_project/        # Modelagem SQL (Staging, Intermediate, Marts)
├── ingestion/          # Script gerador de dados sintéticos
├── ml/                 # Script de treino e registro no MLflow
├── tests/              # Testes Python
├── docker-compose.yml  # Orquestração do Postgres e MLflow
└── requirements.txt    # Dependências do projeto
```
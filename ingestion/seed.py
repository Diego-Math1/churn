import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker
from sqlalchemy import create_engine

random.seed(42)
Faker.seed(42)

fake = Faker("pt_BR") #Gera nomes/emails/endereços brasileiros, não americanos

# Conexão com o Postgres do Docker
# Formato: postgresql://usuario:senha@host:porta/banco
DB_URL = "postgresql://churn:churn@localhost:5432/churn"
engine = create_engine(DB_URL) #SQLAlchemy cuida da conexão. não precisa abrir/fechar conexão manualmente

# Constantes do cenário
N_CLIENTES = 1000
DATA_HOJE = datetime(2026, 10, 9)  # ponto de referência pra calcular recência

def gerar_clientes(n):
    clientes = []
    for i in range(1, n + 1):
        # Data de cadastro: entre 2 anos atrás e hoje
        dias_atras = random.randint(30, 730)
        data_cadastro = DATA_HOJE - timedelta(days=dias_atras)

        # Plano: distribuição realista (mais gente no básico)
        plano = random.choices(
            ["basico", "padrao", "premium"],
            weights=[50, 35, 15],  # 50% básico, 35% padrão, 15% premium
            k=1,
        )[0]

        clientes.append({
            "id_cliente": i,
            "nome": fake.name(),
            "email": fake.email(),
            "cidade": fake.city(),
            "estado": fake.state_abbr(),
            "data_cadastro": data_cadastro.date(),
            "plano": plano,
        })

    return pd.DataFrame(clientes)

def gerar_compras(clientes, data_hoje):
    compras = []
    id_compra = 1

    for _, cliente in clientes.iterrows():
        id_cliente = cliente["id_cliente"]
        plano = cliente["plano"]

        # Quantas compras esse cliente faz no total?
        if plano == "premium":
            n_compras = random.randint(10, 40)
        elif plano == "padrao":
            n_compras = random.randint(5, 25)
        else:
            n_compras = random.randint(0, 15)

        # Sorteia se esse cliente vai dar churn (30% de chance base)
        vai_dar_churn = random.random() < 0.30

        # Se der churn, para de comprar há X dias
        if vai_dar_churn:
            dias_ultima_compra = random.randint(60, 180)
        else:
            dias_ultima_compra = random.randint(0, 30)

        # Gera as compras distribuídas ANTES da última compra
        for _ in range(n_compras):
            dias_atras = random.randint(dias_ultima_compra, dias_ultima_compra + 365)
            data_compra = data_hoje - timedelta(days=dias_atras)

            # Valor depende do plano
            if plano == "premium":
                valor = round(random.uniform(200, 800), 2)
            elif plano == "padrao":
                valor = round(random.uniform(80, 300), 2)
            else:
                valor = round(random.uniform(20, 100), 2)

            compras.append({
                "id_compra": id_compra,
                "id_cliente": id_cliente,
                "data_compra": data_compra.date(),
                "valor": valor,
            })
            id_compra += 1

    return pd.DataFrame(compras)

def gerar_eventos(clientes, data_hoje):
    eventos = []
    id_evento = 1

    for _, cliente in clientes.iterrows():
        id_cliente = cliente["id_cliente"]

        # Quantos tickets de suporte?
        n_tickets = random.choices(
            [0, 1, 2, 3, 5, 10],
            weights=[40, 25, 15, 10, 7, 3],
            k=1,
        )[0]

        for _ in range(n_tickets):
            dias_atras = random.randint(0, 180)
            data_evento = data_hoje - timedelta(days=dias_atras)

            eventos.append({
                "id_evento": id_evento,
                "id_cliente": id_cliente,
                "data_evento": data_evento.date(),
                "tipo": "ticket_suporte",
                "valor": None,
            })
            id_evento += 1

        # Quantos logins por mês?
        n_logins = random.randint(0, 60)

        for _ in range(n_logins):
            dias_atras = random.randint(0, 90)
            data_evento = data_hoje - timedelta(days=dias_atras)

            eventos.append({
                "id_evento": id_evento,
                "id_cliente": id_cliente,
                "data_evento": data_evento.date(),
                "tipo": "login",
                "valor": None,
            })
            id_evento += 1

    return pd.DataFrame(eventos)

def calcular_churn(clientes, compras, eventos, data_hoje):
    resultado = []

    for _, cliente in clientes.iterrows():
        id_cliente = cliente["id_cliente"]

        # Compras desse cliente
        compras_cliente = compras[compras["id_cliente"] == id_cliente]
        n_compras = len(compras_cliente)

        # Recência: dias desde a última compra
        if n_compras > 0:
            ultima_compra = pd.to_datetime(compras_cliente["data_compra"].max())
            dias_sem_comprar = (data_hoje - ultima_compra).days
        else:
            dias_sem_comprar = 999  # nunca comprou

        # Tickets de suporte
        eventos_cliente = eventos[eventos["id_cliente"] == id_cliente]
        n_tickets = len(eventos_cliente[eventos_cliente["tipo"] == "ticket_suporte"])

        # Regra de churn (o "padrão oculto" que o ML vai aprender)
        churn = 0
        if dias_sem_comprar > 90 or (dias_sem_comprar > 60 and n_tickets >= 3) or n_compras == 0:
            churn = 1

        resultado.append({
            "id_cliente": id_cliente,
            "churn": churn,
        })

    return pd.DataFrame(resultado)

def gravar_no_banco(df_clientes, df_compras, df_eventos):
    # if_exists="replace" → recria a tabela toda vez que rodar
    df_clientes.to_sql("raw_clientes", engine, if_exists="replace", index=False)
    df_compras.to_sql("raw_compras", engine, if_exists="replace", index=False)
    df_eventos.to_sql("raw_eventos", engine, if_exists="replace", index=False)

    print(f"✅ {len(df_clientes)} clientes gravados")
    print(f"✅ {len(df_compras)} compras gravadas")
    print(f"✅ {len(df_eventos)} eventos gravados")


if __name__ == "__main__":
    print("Gerando clientes...")
    df_clientes = gerar_clientes(N_CLIENTES)

    print("Gerando compras...")
    df_compras = gerar_compras(df_clientes, DATA_HOJE)

    print("Gerando eventos...")
    df_eventos = gerar_eventos(df_clientes, DATA_HOJE)

    print("Calculando churn...")
    df_churn = calcular_churn(df_clientes, df_compras, df_eventos, DATA_HOJE)

    # Junta churn aos clientes
    df_clientes = df_clientes.merge(df_churn, on="id_cliente")

    print("Gravando no Postgres...")
    gravar_no_banco(df_clientes, df_compras, df_eventos)

    print("\n📊 Distribuição de churn:")
    print(df_clientes["churn"].value_counts(normalize=True).round(3))
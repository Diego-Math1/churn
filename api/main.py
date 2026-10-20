import os
import mlflow
import mlflow.sklearn
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Configuração do MLflow
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_URI)

app = FastAPI(
    title="API de Predição de Churn",
    description="Recebe dados de um cliente e retorna a probabilidade de churn.",
    version="1.0.0"
)

# ⚠️ COLE O SEU RUN_ID AQUI
RUN_ID = "13be38f364014757b129048dcd345b3e"

# Variável global para guardar o modelo na memória
modelo = None

@app.on_event("startup")
def carregar_modelo():
    """Carrega o modelo do MLflow quando a API inicia."""
    global modelo
    try:
        print(f"Carregando modelo do MLflow (Run ID: {RUN_ID})...")
        #MODEL_URI = "models:/m-4cfd127ea5a14d3a99769578e752f74c" # Cole o valor do passo 1 aqui
        modelo = mlflow.sklearn.load_model("models:/churn_classifier/latest")
        print("✅ Modelo carregado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        raise e

# Define o contrato de dados (o que a API espera receber)
class ClienteInput(BaseModel):
    dias_desde_ultima_compra: int
    total_compras: int
    valor_total_gasto: float
    ticket_medio: float
    dias_como_cliente: int
    total_tickets: int
    total_logins: int
    tickets_ultimos_90d: int
    dias_desde_ultimo_login: int
    plano: str

@app.get("/")
def health_check():
    return {"status": "ok", "modelo_carregado": modelo is not None}

@app.post("/predict")
def prever_churn(cliente: ClienteInput):
    if modelo is None:
        raise HTTPException(status_code=500, detail="Modelo não carregado.")
    
    # 1. Converte o input para DataFrame
    df = pd.DataFrame([cliente.model_dump()])
    
    # 2. Aplica One-Hot Encoding na coluna plano
    df = pd.get_dummies(df, columns=["plano"], prefix="plano")
    
    # 3. Garante que TODAS as colunas do treino existam (mesmo as que viraram 0)
    colunas_treino = [
        'dias_desde_ultima_compra', 'total_compras', 'valor_total_gasto',
        'ticket_medio', 'dias_como_cliente', 'total_tickets', 'total_logins',
        'tickets_ultimos_90d', 'dias_desde_ultimo_login',
        'plano_basico', 'plano_padrao', 'plano_premium'
    ]
    # O reindex preenche com 0 as colunas que não existem no df do input
    df = df.reindex(columns=colunas_treino, fill_value=0)
    
    # 4. Faz a previsão
    # predict_proba retorna [prob_classe_0, prob_classe_1]
    probabilidade = float(modelo.predict_proba(df)[0][1])
    previsao = int(probabilidade > 0.5)
    
    # 5. Monta a resposta
    return {
        "churn_previsto": previsao,
        "probabilidade_churn": round(probabilidade, 4),
        "acao_recomendada": "Enviar oferta de retenção" if previsao == 1 else "Nenhuma ação necessária"
    }
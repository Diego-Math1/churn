"""
Treina um modelo de classificação para prever churn.

Pipeline:
    1. Lê a tabela fct_features_churn do Postgres
    2. Separa features (X) e target (y)
    3. Divide em treino/teste
    4. Treina RandomForest
    5. Avalia
    6. Registra no MLflow
"""

import os

import mlflow
import mlflow.sklearn
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine

# Carrega variáveis do .env (DATABASE_URL, MLFLOW_TRACKING_URI)
load_dotenv()

# Configurações do experimento
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://churn:churn@localhost:5432/churn",
)
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

EXPERIMENT_NAME = "churn-prediction"
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Conexão com o banco
engine = create_engine(DATABASE_URL)

def carregar_dados():
    """
        Lê a tabela fct_features_churn do Postgres e prepara X e y.
        
        Retorna:
            X: DataFrame com as fratures (sem id, sem data, sem target)
            y: Series com target (churn)
    """

    query = "SELECT * FROM public.fct_features_churn"
    df = pd.read_sql(query, engine)

    print (f"Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")

    # Separa o target (o que queremos prever)
    y = df["churn"]

    #separa as features (o que o modelo usa para prever)
    #Remove: id (não preditivo), data_cadastro (já virou dias_como_cliente), churn (é o target)
    colunas_excluir = ["id_cliente","data_cadastro","churn"]
    X = df.drop(columns=colunas_excluir)

    #One-hot encoding do 'plano'
    X=pd.get_dummies(X,columns=["plano"], prefix="plano")

    print(f"Features após encoding: {list(X.columns)}")
    print(f"Target: {y.value_counts().to_dict()}")
    return X, y

def treinar_modelo(X, y):
    """
    Divide os dados em treino/teste e treina o Random Forest.
    """
    print("\n✂️  Dividindo dados em treino e teste...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,  # mantém a proporção de churn no treino e no teste
    )
    print(f"   Treino: {len(X_train)} amostras")
    print(f"   Teste:  {len(X_test)} amostras")

    print("\n🌲 Treinando Random Forest...")
    modelo = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=RANDOM_STATE,
        n_jobs=-1,  # usa todos os núcleos da CPU
    )

    import time
    inicio = time.time()
    modelo.fit(X_train, y_train)
    duracao = time.time() - inicio
    print(f"   ✅ Modelo treinado em {duracao:.2f}s")

    return modelo, X_train, X_test, y_train, y_test

def avaliar_modelo(modelo, X_test, y_test):
    """
    Faz previsões no conjunto de teste e calcula as métricas.
    """
    print("\n📏 Avaliando o modelo no conjunto de teste...")

    # O modelo faz as previsões
    y_pred = modelo.predict(X_test)
    
    # Probabilidades (útil pro ROC-AUC)
    y_proba = modelo.predict_proba(X_test)[:, 1]

    # Calcula as métricas
    acuracia = accuracy_score(y_test, y_pred)
    precisao = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)

    print(f"   Acurácia:  {acuracia:.3f}")
    print(f"   Precisão:  {precisao:.3f}")
    print(f"   Recall:    {recall:.3f}")
    print(f"   F1-Score:  {f1:.3f}")
    print(f"   ROC-AUC:   {roc_auc:.3f}")

    # Matriz de confusão
    print("\n🧩 Matriz de Confusão:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"   TN={cm[0][0]:3d}  FP={cm[0][1]:3d}")
    print(f"   FN={cm[1][0]:3d}  TP={cm[1][1]:3d}")

    return {
        "accuracy": acuracia,
        "precision": precisao,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
    }

def registrar_no_mlflow(modelo, metricas):
    """
    Registra params, métricas e o modelo no MLflow.
    """
    print("\n📦 Registrando experimento no MLflow...")
    
    # Aponta para o servidor do MLflow (Docker)
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    # Abre um "run" no MLflow
    with mlflow.start_run():
        # 1. Registra os parâmetros do modelo
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("max_depth", 10)
        mlflow.log_param("test_size", TEST_SIZE)
        mlflow.log_param("random_state", RANDOM_STATE)

        # 2. Registra as métricas
        mlflow.log_metrics(metricas)

        # 3. Registra o modelo treinado em si
        mlflow.sklearn.log_model(modelo, "random_forest_churn")

        print("   ✅ Experimento registrado com sucesso!")
        print(f"   🔗 Acesse: {MLFLOW_URI}")

if __name__ == "__main__":
    X, y = carregar_dados()
    modelo, X_train, X_test, y_train, y_test = treinar_modelo(X, y)
    metricas = avaliar_modelo(modelo, X_test, y_test)
    registrar_no_mlflow(modelo, metricas)
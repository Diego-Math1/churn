SELECT
    id_cliente,
    nome,
    email,
    cidade,
    estado,
    CAST(data_cadastro AS DATE) AS data_cadastro,
    plano,
    churn
FROM {{ source('raw', 'clientes') }}

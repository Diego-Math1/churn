WITH compras_por_cliente AS (
    SELECT
        id_cliente,
        COUNT(*) AS total_compras,
        SUM(valor) AS valor_total_gasto,
        AVG(valor) AS ticket_medio,
        MAX(data_compra) AS ultima_compra,
        MIN(data_compra) AS primeira_compra
    FROM {{ ref('stg_compras') }}
    GROUP BY id_cliente
)

SELECT
    c.id_cliente,
    c.plano,
    c.data_cadastro,
    -- Recência: dias desde a última compra (Postgres já retorna inteiro)
    CASE
        WHEN cp.ultima_compra IS NULL THEN 999
        ELSE CURRENT_DATE - cp.ultima_compra
    END AS dias_desde_ultima_compra,
    -- Frequência
    COALESCE(cp.total_compras, 0) AS total_compras,
    -- Monetário
    COALESCE(cp.valor_total_gasto, 0) AS valor_total_gasto,
    COALESCE(cp.ticket_medio, 0) AS ticket_medio,
    -- Tempo como cliente (em dias) — mesma correção
    CURRENT_DATE - c.data_cadastro AS dias_como_cliente
FROM {{ ref('stg_clientes') }} c
LEFT JOIN compras_por_cliente cp ON cp.id_cliente = c.id_cliente

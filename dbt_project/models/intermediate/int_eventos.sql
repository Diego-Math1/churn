WITH eventos_por_cliente AS (
    SELECT
        id_cliente,
        COUNT(*) FILTER (WHERE tipo = 'ticket_suporte') AS total_tickets,
        COUNT(*) FILTER (WHERE tipo = 'login') AS total_logins,
        COUNT(*) FILTER (
            WHERE tipo = 'ticket_suporte'
            AND data_evento >= CURRENT_DATE - INTERVAL '90 days'
        ) AS tickets_ultimos_90d,
        MAX(CASE WHEN tipo = 'login' THEN data_evento END) AS ultimo_login
    FROM {{ ref('stg_eventos') }}
    GROUP BY id_cliente
)

SELECT
    c.id_cliente,
    COALESCE(e.total_tickets, 0) AS total_tickets,
    COALESCE(e.total_logins, 0) AS total_logins,
    COALESCE(e.tickets_ultimos_90d, 0) AS tickets_ultimos_90d,
    CASE
        WHEN e.ultimo_login IS NULL THEN 999
        ELSE CURRENT_DATE - e.ultimo_login
    END AS dias_desde_ultimo_login
FROM {{ ref('stg_clientes') }} c
LEFT JOIN eventos_por_cliente e ON e.id_cliente = c.id_cliente

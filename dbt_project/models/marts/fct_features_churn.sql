SELECT
    c.id_cliente,
    c.plano,
    c.data_cadastro,

    -- === Features RFM ===
    r.dias_desde_ultima_compra,
    r.total_compras,
    ROUND(r.valor_total_gasto, 2) AS valor_total_gasto,
    ROUND(r.ticket_medio, 2) AS ticket_medio,
    r.dias_como_cliente,

    -- === Features de Eventos ===
    e.total_tickets,
    e.total_logins,
    e.tickets_ultimos_90d,
    e.dias_desde_ultimo_login,

    -- === Target ===
    c.churn

FROM {{ ref('stg_clientes') }} c
LEFT JOIN {{ ref('int_rfm') }} r ON r.id_cliente = c.id_cliente
LEFT JOIN {{ ref('int_eventos') }} e ON e.id_cliente = c.id_cliente

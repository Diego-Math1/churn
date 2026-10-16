SELECT
    id_compra,
    id_cliente,
    CAST(data_compra AS DATE) AS data_compra,
    CAST(valor AS NUMERIC(10, 2)) AS valor
FROM {{ source('raw', 'compras') }}

SELECT
    id_evento,
    id_cliente,
    CAST(data_evento AS DATE) AS data_evento,
    tipo
FROM {{ source('raw', 'eventos') }}

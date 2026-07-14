
QUERY_ACTIVE_SERVICES = """
    SELECT 
        RAZON_SOCIAL AS [Razón Social],
        ANCHODEBANDA AS [Capacidad],
        TARIFA AS [Tarifa],
        TARIFA / CAPACIDADBPS AS [Vlr x Mbps],
        FECHA_FIN_PERMANENCIA AS [Fecha Fin Permanencia]
    FROM [DTM].[SF_SERVICE_LEGV2]
    WHERE ESTADO_SER NOT IN (
        'Cancelado',
        'Error',
        'En Proceso',
        'Declinado'
    ) AND [PLAN] IN (
        'CANAL NACIONAL ETHERNET',
        'IRU DE CAPACIDAD',
        'CANAL NACIONAL ETHERNET SIN UK',
        'ID CORPORATIVO',
        'INTERNET DEDICADO SIN UK',
        'INTERNET DEDICADO SIN UK BURST',
        'INTERNET DEDICADO EMPRESARIAL',
        'RED IP',
        'TRELUS INTERNET DEDICADO',
        'INTERNET SIMETRICO EMPRESARIAL',
        'BA CORPORATIVA',
        'INTERNET + ALTO VALOR ESTRATO(1-3)',
        'INTERNET + ALTO VALOR ESTRATO(4-6)',
        'INTERNET +'
    )
    AND SegmentacionIVR = 'ISPs'
    AND TARIFA <> 0
    AND CAPACIDADBPS >= ?
    AND [Codigo DANE] = ?
    ORDER BY TARIFA DESC
        """

QUERY_SERVICES_REFERENCE_MUN = """
WITH Servicios AS
(
    SELECT *,
           CASE
               WHEN DIGITO_VERIFICACION IS NULL
                   THEN CAST(NRO_IDENTIFICACION AS varchar(20))
               ELSE CONCAT(NRO_IDENTIFICACION, '-', DIGITO_VERIFICACION)
           END AS NIT
    FROM DTM.SF_SERVICE_LEGV2
)

SELECT 
        DEPARTAMENTO,
        MUNICIPIO,
        CAPACIDADBPS AS CAPACIDAD_MBPS,
        TARIFA,
        TARIFA * 1.0 / CAPACIDADBPS AS VLR_MBPS
    FROM Servicios
    WHERE ESTADO_SER NOT IN (
        'Cancelado',
        'Error',
        'En Proceso',
        'Declinado'
    ) AND [PLAN] IN (
        'CANAL NACIONAL ETHERNET',
        'IRU DE CAPACIDAD',
        'CANAL NACIONAL ETHERNET SIN UK',
        'ID CORPORATIVO',
        'INTERNET DEDICADO SIN UK',
        'INTERNET DEDICADO SIN UK BURST',
        'INTERNET DEDICADO EMPRESARIAL',
        'RED IP',
        'TRELUS INTERNET DEDICADO',
        'INTERNET SIMETRICO EMPRESARIAL',
        'BA CORPORATIVA',
        'INTERNET + ALTO VALOR ESTRATO(1-3)',
        'INTERNET + ALTO VALOR ESTRATO(4-6)',
        'INTERNET +'
    )
    AND NIT NOT IN (
        '800136835-1',
        '800153993-7',
        '800255754-1',
        '806009543-2',
        '811021654-9',
        '819006966-8',
        '830053800-4',
        '830058677-7',
        '830078515-8',
        '830114921-1',
        '830122566-1',
        '890905065-2',
        '899999115-8',
        '900092385-9',
        '900195679-1',
        '900258177-8',
        '901354361-1'
    )
    AND TARIFA > 10
    AND CAPACIDADBPS <> 0
    AND [Codigo DANE] = ?
    ORDER BY TARIFA DESC
"""

QUERY_SERVICES_REFERENCE_DEPT = """
WITH Servicios AS
(
    SELECT *,
           CASE
               WHEN DIGITO_VERIFICACION IS NULL
                   THEN CAST(NRO_IDENTIFICACION AS varchar(20))
               ELSE CONCAT(NRO_IDENTIFICACION, '-', DIGITO_VERIFICACION)
           END AS NIT
    FROM DTM.SF_SERVICE_LEGV2
)

SELECT 
        DEPARTAMENTO,
        MUNICIPIO,
        CAPACIDADBPS AS CAPACIDAD_MBPS,
        TARIFA,
        TARIFA * 1.0 / CAPACIDADBPS AS VLR_MBPS
    FROM Servicios
    WHERE ESTADO_SER NOT IN (
        'Cancelado',
        'Error',
        'En Proceso',
        'Declinado'
    ) AND [PLAN] IN (
        'CANAL NACIONAL ETHERNET',
        'IRU DE CAPACIDAD',
        'CANAL NACIONAL ETHERNET SIN UK',
        'ID CORPORATIVO',
        'INTERNET DEDICADO SIN UK',
        'INTERNET DEDICADO SIN UK BURST',
        'INTERNET DEDICADO EMPRESARIAL',
        'RED IP',
        'TRELUS INTERNET DEDICADO',
        'INTERNET SIMETRICO EMPRESARIAL',
        'BA CORPORATIVA',
        'INTERNET + ALTO VALOR ESTRATO(1-3)',
        'INTERNET + ALTO VALOR ESTRATO(4-6)',
        'INTERNET +'
    )
    AND NIT NOT IN (
        '800136835-1',
        '800153993-7',
        '800255754-1',
        '806009543-2',
        '811021654-9',
        '819006966-8',
        '830053800-4',
        '830058677-7',
        '830078515-8',
        '830114921-1',
        '830122566-1',
        '890905065-2',
        '899999115-8',
        '900092385-9',
        '900195679-1',
        '900258177-8',
        '901354361-1'
    )
    AND TARIFA > 10
    AND CAPACIDADBPS <> 0
    AND DEPARTAMENTO = ?
    ORDER BY TARIFA DESC
"""

QUERY_SERVICES_REFERENCE_NATIONAL = """
WITH Servicios AS
(
    SELECT *,
           CASE
               WHEN DIGITO_VERIFICACION IS NULL
                   THEN CAST(NRO_IDENTIFICACION AS varchar(20))
               ELSE CONCAT(NRO_IDENTIFICACION, '-', DIGITO_VERIFICACION)
           END AS NIT
    FROM DTM.SF_SERVICE_LEGV2
)

SELECT 
        DEPARTAMENTO,
        MUNICIPIO,
        CAPACIDADBPS AS CAPACIDAD_MBPS,
        TARIFA,
        TARIFA * 1.0 / CAPACIDADBPS AS VLR_MBPS
    FROM Servicios
    WHERE ESTADO_SER NOT IN (
        'Cancelado',
        'Error',
        'En Proceso',
        'Declinado'
    ) AND [PLAN] IN (
        'CANAL NACIONAL ETHERNET',
        'IRU DE CAPACIDAD',
        'CANAL NACIONAL ETHERNET SIN UK',
        'ID CORPORATIVO',
        'INTERNET DEDICADO SIN UK',
        'INTERNET DEDICADO SIN UK BURST',
        'INTERNET DEDICADO EMPRESARIAL',
        'RED IP',
        'TRELUS INTERNET DEDICADO',
        'INTERNET SIMETRICO EMPRESARIAL',
        'BA CORPORATIVA',
        'INTERNET + ALTO VALOR ESTRATO(1-3)',
        'INTERNET + ALTO VALOR ESTRATO(4-6)',
        'INTERNET +'
    )
    AND NIT NOT IN (
        '800136835-1',
        '800153993-7',
        '800255754-1',
        '806009543-2',
        '811021654-9',
        '819006966-8',
        '830053800-4',
        '830058677-7',
        '830078515-8',
        '830114921-1',
        '830122566-1',
        '890905065-2',
        '899999115-8',
        '900092385-9',
        '900195679-1',
        '900258177-8',
        '901354361-1'
    )
    AND TARIFA > 10
    AND CAPACIDADBPS <> 0
    ORDER BY TARIFA DESC
"""
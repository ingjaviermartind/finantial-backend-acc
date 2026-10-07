
QUERY_ACTIVE_SERVICES = """
WITH Servicios AS 
(
    SELECT *, 
        CASE 
            WHEN DIGITO_VERIFICACION IS NULL 
                THEN CAST(NRO_IDENTIFICACION AS varchar(20)) 
            ELSE CONCAT(NRO_IDENTIFICACION, '-', DIGITO_VERIFICACION) 
        END AS NIT 
    FROM DTM.SF_SERVICE_LEGV2 
),

ServiciosActivos AS
(
    SELECT *
    FROM Servicios s
    WHERE s.ESTADO_SER NOT IN ( 
        'Cancelado', 
        'Error', 
        'En Proceso', 
        'Declinado' 
    )
    AND s.TARIFA > 1
),

TarifaCliente AS
(
    SELECT
        NIT,
        SUM(TARIFA) AS TARIFA_TOTAL_CLIENTE
    FROM ServiciosActivos
    GROUP BY NIT
)

SELECT  
    s.NIT, 
    s.RAZON_SOCIAL AS [Razón Social], 
    s.ANCHODEBANDA AS [Capacidad], 
    s.CAPACIDADBPS, 
    s.TARIFA AS [Tarifa], 
    s.TARIFA / s.CAPACIDADBPS AS [Vlr x Mbps], 
    s.FECHA_FIN_PERMANENCIA AS [Fecha Fin Permanencia],
    s.PRODUCTO AS Producto,
    tc.TARIFA_TOTAL_CLIENTE AS [Tarifa Total Cliente]

FROM ServiciosActivos s

LEFT JOIN TarifaCliente tc
    ON s.NIT = tc.NIT

WHERE
    s.SER NOT IN ('SER-280627') 
    AND s.[PLAN] IN (
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
    AND s.CAPACIDADBPS >= :min_cap
    AND s.[Codigo DANE] = :dane 

ORDER BY s.CAPACIDADBPS DESC;
        """

QUERY_ACTIVE_SERVICES_V2 = """
WITH ServiciosActivos AS 
(
    SELECT 
		s.SER,
		s.Departamento,
		s.Municipio,
		s.[Codigo DANE],
		s.TIPO_TECNOLOGIA,
		ciclo.ULT_CICLO_FACT as Ciclo,
		s.RAZON_SOCIAL,
		s.ANCHODEBANDA,
		s.CAPACIDADBPS,
		s.TARIFA, 
		s.FECHA_FIN_PERMANENCIA,
		s.TARIFA / NULLIF(s.CAPACIDADBPS, 0) AS [Vlr x Mbps], 
		s.FAMILIA_PRODUCTOS,
		s.PRODUCTO,
		s.[PLAN],
		s.TIPO_PRODUCTO,
        s.TipodePunto,
        s.NvoSubsegmento,
        CASE 
            WHEN s.DIGITO_VERIFICACION IS NULL 
                THEN CAST(s.NRO_IDENTIFICACION AS varchar(20)) 
            ELSE CONCAT(s.NRO_IDENTIFICACION, '-', s.DIGITO_VERIFICACION) 
        END AS NIT
    FROM DTM.SF_SERVICE_LEGV2 s
	LEFT JOIN DTM.CICLO_SERV_ACTIVOS_PLANTA ciclo
		ON ciclo.SERVICIO = s.SER
	WHERE s.ESTADO_SER NOT IN 
	( 
        'Cancelado', 
        'Error', 
        'En Proceso', 
        'Declinado' 
    )
),
TarifaCliente AS
(
    SELECT
        NIT,
        SUM(TARIFA) AS TARIFA_TOTAL_CLIENTE
    FROM ServiciosActivos
    GROUP BY NIT
)
SELECT  
	s.SER,
	s.Ciclo,
	s.Departamento,
	s.Municipio,
	s.[Codigo DANE],
    s.NIT,
    s.RAZON_SOCIAL AS [Razón Social], 
	tc.TARIFA_TOTAL_CLIENTE AS [Tarifa Total Cliente],
    s.ANCHODEBANDA AS [Capacidad], 
    s.CAPACIDADBPS,
    s.TARIFA AS [Tarifa], 
    s.[Vlr x Mbps],
    s.FECHA_FIN_PERMANENCIA AS [Fecha Fin Permanencia],
	s.FAMILIA_PRODUCTOS,
    s.PRODUCTO AS Producto,
	s.[PLAN] AS [Plan],
	s.TIPO_TECNOLOGIA,
    s.NvoSubsegmento as Subsegmento
FROM ServiciosActivos s
LEFT JOIN TarifaCliente tc
    ON s.NIT = tc.NIT
WHERE s.TIPO_PRODUCTO IN 
(
	'L2',
	'L3'
)
AND (
    s.TipodePunto NOT IN 
    ( 
        'Interconexion',
        'Interconexión - IRU',
        'Interconexion Backup'
    )
    OR s.TipodePunto IS NULL
)
AND s.TARIFA > 1
AND s.SER <> 'SER-280627' 
AND s.[Codigo DANE] IN :danes
AND 
(
	:filter_product_family = 0
	OR s.FAMILIA_PRODUCTOS IN :product_families
)
AND 
(
	:filter_product = 0
	OR s.PRODUCTO IN :products
)
AND
(
	:filter_plan = 0
	OR s.[PLAN] IN :plans
)
AND 
(
    :capacity_max IS NULL
    OR s.CAPACIDADBPS <= :capacity_max
)
AND (
    :capacity_min IS NULL
    OR s.CAPACIDADBPS >= :capacity_min
)
AND 
(
	:filter_client = 0
	OR s.NIT IN :clients
)
AND 
(
    :filter_subsegment = 0
    OR s.NvoSubsegmento IN :subsegments
)
ORDER BY s.CAPACIDADBPS DESC;
"""

QUERY_ACTIVE_CLIENTS = """
WITH ServiciosActivos AS 
(
    SELECT 
		s.RAZON_SOCIAL,
        CASE 
            WHEN s.DIGITO_VERIFICACION IS NULL 
                THEN CAST(s.NRO_IDENTIFICACION AS varchar(20)) 
            ELSE CONCAT(s.NRO_IDENTIFICACION, '-', s.DIGITO_VERIFICACION) 
        END AS NIT
    FROM DTM.SF_SERVICE_LEGV2 s
	WHERE s.ESTADO_SER NOT IN 
	( 
        'Cancelado', 
        'Error', 
        'En Proceso', 
        'Declinado' 
    )
)
SELECT DISTINCT
NIT,
RAZON_SOCIAL
FROM ServiciosActivos;
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
    AND SER NOT IN  ('SER-280627')
    AND [Codigo DANE] = :dane
    AND CAPACIDADBPS >= :min_cap
    AND CAPACIDADBPS <= :max_cap
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
    AND SER NOT IN  ('SER-280627')
    AND DEPARTAMENTO = :department
    AND CAPACIDADBPS >= :min_cap
    AND CAPACIDADBPS <= :max_cap
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
    AND SER NOT IN  ('SER-280627')
    AND CAPACIDADBPS >= :min_cap
    AND CAPACIDADBPS <= :max_cap
    ORDER BY TARIFA DESC
"""
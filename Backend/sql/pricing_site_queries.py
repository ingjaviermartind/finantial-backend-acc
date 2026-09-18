QUERY_PRICED_SITES_COUNT = """
WITH Sedes AS
(
    SELECT
        s.[Consecutivo de Sede],
        s.Departamento,
        s.Municipio,
        s.DANE_Mpio,
        s.Producto,
        s.[Plan],
        s.[Familia_Producto_Sede],
        CASE
            WHEN s.[Ancho de banda] IS NULL THEN 0
            WHEN LOWER(LTRIM(RTRIM(s.[Ancho de banda]))) LIKE '%gbps%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        LOWER(LTRIM(RTRIM(s.[Ancho de banda]))),
                        CHARINDEX(
                            'gbps',
                            LOWER(LTRIM(RTRIM(s.[Ancho de banda])))
                        ) - 1
                    )
                ) * 1000
            WHEN LOWER(LTRIM(RTRIM(s.[Ancho de banda]))) LIKE '%gb%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        LOWER(LTRIM(RTRIM(s.[Ancho de banda]))),
                        CHARINDEX(
                            'gb',
                            LOWER(LTRIM(RTRIM(s.[Ancho de banda])))
                        ) - 1
                    )
                ) * 1000
            WHEN LOWER(LTRIM(RTRIM(s.[Ancho de banda]))) LIKE '%mbps%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        LOWER(LTRIM(RTRIM(s.[Ancho de banda]))),
                        CHARINDEX(
                            'mbps',
                            LOWER(LTRIM(RTRIM(s.[Ancho de banda])))
                        ) - 1
                    )
                )
            WHEN LOWER(LTRIM(RTRIM(s.[Ancho de banda]))) LIKE '%kbps%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        LOWER(LTRIM(RTRIM(s.[Ancho de banda]))),
                        CHARINDEX(
                            'kbps',
                            LOWER(LTRIM(RTRIM(s.[Ancho de banda])))
                        ) - 1
                    )
                ) / 1000
            ELSE TRY_CONVERT(
                DECIMAL(18,4),
                LTRIM(RTRIM(s.[Ancho de banda]))
            )
        END AS [Ancho de banda (Nro)]
    FROM SFDC.DM_PRICING_SEDE s
),
PricingPromedioSede AS
(
    SELECT
        p.[Sede]
    FROM SFDC.DM_PRICING_X_SEDE p
    WHERE p.[Pricing por Sede On/Off] = 'SI'
    GROUP BY
        p.[Sede]
),
Funnels AS
(
    SELECT
        f.[FUNNEL],
        f.[SEDE],
        f.[FechaCreacion],
        f.[NOMBRE_COMERCIAL_FUNNEL],
        f.[ESTADO_FUNNEL],
        CASE
            WHEN NULLIF(
                LTRIM(RTRIM(
                    CAST(f.[DIGITO_VERIFICACION_FUNNEL] AS VARCHAR(20))
                )),
                ''
            ) IS NULL
            THEN LTRIM(RTRIM(
                CAST(
                    f.[NRO_IDENTIFICACION_CLIENTE_FUNNEL]
                    AS VARCHAR(50)
                )
            ))
            ELSE CONCAT(
                LTRIM(RTRIM(
                    CAST(
                        f.[NRO_IDENTIFICACION_CLIENTE_FUNNEL]
                        AS VARCHAR(50)
                    )
                )),
                '-',
                LTRIM(RTRIM(
                    CAST(
                        f.[DIGITO_VERIFICACION_FUNNEL]
                        AS VARCHAR(20)
                    )
                ))
            )
        END AS [NIT_CONCATENADO]
    FROM DTM.SF_FUNNELV2 f
),
FilteredData AS
(
    SELECT
        f.[FUNNEL],
        f.[FechaCreacion],
        f.[ESTADO_FUNNEL],
        f.[NIT_CONCATENADO],
        s.[Consecutivo de Sede],
        s.[Departamento],
        s.[Municipio],
        s.[DANE_Mpio],
        s.[Producto],
        s.[Plan],
        s.[Familia_Producto_Sede],
        s.[Ancho de banda (Nro)]
    FROM Funnels f
    INNER JOIN Sedes s
        ON f.[SEDE] = s.[Consecutivo de Sede]
    INNER JOIN PricingPromedioSede ps
        ON s.[Consecutivo de Sede] = ps.[Sede]
    WHERE 1 = 1
      AND (
          :fecha_inicio IS NULL
          OR f.[FechaCreacion] >= :fecha_inicio
      )
      AND (
          :capacity_min IS NULL
          OR s.[Ancho de banda (Nro)] >= :capacity_min
      )
      AND (
          :capacity_max IS NULL
          OR s.[Ancho de banda (Nro)] <= :capacity_max
      )
      AND (
          :filter_funnel_status = 0
          OR f.[ESTADO_FUNNEL] IN :funnel_statuses
      )
      AND (
          :filter_department = 0
          OR s.[Departamento] IN :departments
      )
      AND (
          :filter_municipality = 0
          OR s.[Municipio] IN :municipalities
      )
      AND (
          :filter_dane = 0
          OR s.[DANE_Mpio] IN :danes
      )
      AND (
          :filter_product = 0
          OR s.[Producto] IN :products
      )
      AND (
          :filter_plan = 0
          OR s.[Plan] IN :plans
      )
      AND (
          :filter_product_family = 0
          OR s.[Familia_Producto_Sede] IN :product_families
      )
      AND (
          :filter_client = 0
          OR f.[NIT_CONCATENADO] IN :clients
      )
)
SELECT
    COUNT(*) AS TOTAL_SEDES,
    COUNT(DISTINCT [FUNNEL]) AS TOTAL_FUNNELS
FROM FilteredData;
"""

QUERY_PRICED_SITES = """
WITH Sedes AS
(
    SELECT
        s.[Consecutivo de Sede],
        s.Departamento,
        s.Municipio,
        s.DANE_Mpio,
        s.Producto,
        s.[Plan],
        s.[Familia_Producto_Sede],
        s.[Ultimo kilometro (UK)],
        s.[Distancia FO Red ACC],
        s.[Tipo de Tecnologia],
        s.[Ancho de banda],
        CASE
            WHEN s.[Ancho de banda] IS NULL THEN 0
            WHEN LOWER(LTRIM(RTRIM(s.[Ancho de banda]))) LIKE '%gbps%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        LOWER(LTRIM(RTRIM(s.[Ancho de banda]))),
                        CHARINDEX(
                            'gbps',
                            LOWER(LTRIM(RTRIM(s.[Ancho de banda])))
                        ) - 1
                    )
                ) * 1000
            WHEN LOWER(LTRIM(RTRIM(s.[Ancho de banda]))) LIKE '%gb%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        LOWER(LTRIM(RTRIM(s.[Ancho de banda]))),
                        CHARINDEX(
                            'gb',
                            LOWER(LTRIM(RTRIM(s.[Ancho de banda])))
                        ) - 1
                    )
                ) * 1000
            WHEN LOWER(LTRIM(RTRIM(s.[Ancho de banda]))) LIKE '%mbps%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        LOWER(LTRIM(RTRIM(s.[Ancho de banda]))),
                        CHARINDEX(
                            'mbps',
                            LOWER(LTRIM(RTRIM(s.[Ancho de banda])))
                        ) - 1
                    )
                )
            WHEN LOWER(LTRIM(RTRIM(s.[Ancho de banda]))) LIKE '%kbps%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        LOWER(LTRIM(RTRIM(s.[Ancho de banda]))),
                        CHARINDEX(
                            'kbps',
                            LOWER(LTRIM(RTRIM(s.[Ancho de banda])))
                        ) - 1
                    )
                ) / 1000
            ELSE TRY_CONVERT(
                DECIMAL(18,4),
                LTRIM(RTRIM(s.[Ancho de banda]))
            )
        END AS [Ancho de banda (Nro)]
    FROM SFDC.DM_PRICING_SEDE s
),
PricingPromedioSede AS
(
    SELECT
        p.[Sede],
        COUNT(DISTINCT p.[Pricing]) AS NUM_PRICINGS,
        AVG(ISNULL(p.[Recurrente Mes], 0)) AS MRC_PROMEDIO,
        AVG(ISNULL(p.[No Recurrente Mes], 0)) AS NRC_PROMEDIO
    FROM SFDC.DM_PRICING_X_SEDE p
    WHERE p.[Pricing por Sede On/Off] = 'SI'
    GROUP BY
        p.[Sede]
),
Funnels AS
(
    SELECT
        f.[FUNNEL],
        f.[SEDE],
        f.[FechaCreacion],
        f.[NOMBRE_COMERCIAL_FUNNEL],
        f.[ESTADO_FUNNEL],
        f.TARGET_MRC_GRUPAL_FUNNEL,
        CASE
            WHEN NULLIF(
                LTRIM(RTRIM(
                    CAST(f.[DIGITO_VERIFICACION_FUNNEL] AS VARCHAR(20))
                )),
                ''
            ) IS NULL
            THEN LTRIM(RTRIM(
                CAST(
                    f.[NRO_IDENTIFICACION_CLIENTE_FUNNEL]
                    AS VARCHAR(50)
                )
            ))
            ELSE CONCAT(
                LTRIM(RTRIM(
                    CAST(
                        f.[NRO_IDENTIFICACION_CLIENTE_FUNNEL]
                        AS VARCHAR(50)
                    )
                )),
                '-',
                LTRIM(RTRIM(
                    CAST(
                        f.[DIGITO_VERIFICACION_FUNNEL]
                        AS VARCHAR(20)
                    )
                ))
            )
        END AS [NIT_CONCATENADO]
    FROM DTM.SF_FUNNELV2 f
),
FilteredData AS
(
    SELECT
        f.[FUNNEL],
        f.[FechaCreacion],
        f.[NOMBRE_COMERCIAL_FUNNEL],
        f.[ESTADO_FUNNEL],
        f.[NIT_CONCATENADO],
        f.TARGET_MRC_GRUPAL_FUNNEL,

        s.[Consecutivo de Sede],
        s.[Departamento],
        s.[Municipio],
        s.[DANE_Mpio],
        s.[Producto],
        s.[Plan],
        s.[Familia_Producto_Sede],
        s.[Ancho de banda],
        s.[Ancho de banda (Nro)],
        s.[Ultimo kilometro (UK)],
        s.[Distancia FO Red ACC],
        s.[Tipo de Tecnologia],

        ps.NUM_PRICINGS,
        ps.MRC_PROMEDIO,
        ps.NRC_PROMEDIO,
        ps.MRC_PROMEDIO / NULLIF(s.[Ancho de banda (Nro)], 0) AS VLR_MBPS

    FROM Funnels f
    INNER JOIN Sedes s
        ON f.[SEDE] = s.[Consecutivo de Sede]
    INNER JOIN PricingPromedioSede ps
        ON s.[Consecutivo de Sede] = ps.[Sede]
    WHERE 1 = 1
      AND (
          :fecha_inicio IS NULL
          OR f.[FechaCreacion] >= :fecha_inicio
      )
      AND (
          :capacity_min IS NULL
          OR s.[Ancho de banda (Nro)] >= :capacity_min
      )
      AND (
          :capacity_max IS NULL
          OR s.[Ancho de banda (Nro)] <= :capacity_max
      )
      AND (
          :filter_funnel_status = 0
          OR f.[ESTADO_FUNNEL] IN :funnel_statuses
      )
      AND (
          :filter_department = 0
          OR s.[Departamento] IN :departments
      )
      AND (
          :filter_municipality = 0
          OR s.[Municipio] IN :municipalities
      )
      AND (
          :filter_dane = 0
          OR s.[DANE_Mpio] IN :danes
      )
      AND (
          :filter_product = 0
          OR s.[Producto] IN :products
      )
      AND (
          :filter_plan = 0
          OR s.[Plan] IN :plans
      )
      AND (
          :filter_product_family = 0
          OR s.[Familia_Producto_Sede] IN :product_families
      )
      AND (
          :filter_client = 0
          OR f.[NIT_CONCATENADO] IN :clients
      )
),
FunnelUnique AS
(
    SELECT
        [FUNNEL],
        MAX([FechaCreacion]) AS [FechaCreacion],
        MAX([NOMBRE_COMERCIAL_FUNNEL]) AS [NOMBRE_COMERCIAL_FUNNEL],
        MAX([ESTADO_FUNNEL]) AS [ESTADO_FUNNEL],
        MAX([NIT_CONCATENADO]) AS [NIT_CONCATENADO],
        MAX(TARGET_MRC_GRUPAL_FUNNEL) AS TARGET_MRC_GRUPAL_FUNNEL,
        SUM([MRC_PROMEDIO]) AS SUM_MRC
    FROM FilteredData
    GROUP BY
        [FUNNEL]
),

FunnelPage AS
(
    SELECT
        [FUNNEL],
        [FechaCreacion],
        [NOMBRE_COMERCIAL_FUNNEL],
        [ESTADO_FUNNEL],
        [NIT_CONCATENADO],
        [TARGET_MRC_GRUPAL_FUNNEL],
        SUM_MRC
    FROM FunnelUnique
    ORDER BY
        SUM_MRC DESC,
        [FechaCreacion] DESC
    OFFSET :offset ROWS
    FETCH NEXT :page_size ROWS ONLY
)
SELECT
    fp.[FUNNEL],
    fp.[FechaCreacion],
    fp.[NOMBRE_COMERCIAL_FUNNEL],
    fp.[ESTADO_FUNNEL],
    fp.[NIT_CONCATENADO],
    fp.[TARGET_MRC_GRUPAL_FUNNEL],

    fd.[Consecutivo de Sede],
    fd.[Departamento],
    fd.[Municipio],
    fd.[DANE_Mpio],
    fd.[Producto],
    fd.[Plan],
    fd.[Familia_Producto_Sede],
    fd.[Ultimo kilometro (UK)],
    fd.[Distancia FO Red ACC],
    fd.[Tipo de Tecnologia],
    fd.[Ancho de banda],
    fd.[Ancho de banda (Nro)],
    fd.[VLR_MBPS],

    fd.NUM_PRICINGS,
    fd.MRC_PROMEDIO,
    fd.NRC_PROMEDIO

FROM FunnelPage fp

INNER JOIN FilteredData fd
    ON fp.[FUNNEL] = fd.[FUNNEL]

ORDER BY
    fp.[FechaCreacion] DESC,
    fp.[FUNNEL] ASC,
    fd.[Consecutivo de Sede] ASC;
"""

QUERY_FILTER_OPTIONS_CREATE_BASE = """
CREATE TABLE #Base
(
    [FUNNEL] NVARCHAR(80) NULL,
    [FechaCreacion] DATETIME NULL,
    [NOMBRE_COMERCIAL_FUNNEL] NVARCHAR(255) NULL,
    [ESTADO_FUNNEL] NVARCHAR(255) NULL,
    [NIT_CONCATENADO] NVARCHAR(50) NULL,

    [Consecutivo de Sede] NVARCHAR(80) NULL,
    [Departamento] NVARCHAR(100) NULL,
    [Municipio] NVARCHAR(100) NULL,
    [DANE_Mpio] NVARCHAR(20) NULL,

    [Producto] NVARCHAR(255) NULL,
    [Plan] NVARCHAR(80) NULL,
    [Familia_Producto_Sede] NVARCHAR(50) NULL,

    [Ancho de banda (Nro)] DECIMAL(18,4) NULL
);
"""

QUERY_FILTER_OPTIONS_INSERT_BASE = """
WITH Sedes AS
(
    SELECT
        s.[Consecutivo de Sede],
        s.Departamento,
        s.Municipio,
        s.DANE_Mpio,
        s.Producto,
        s.[Plan],
        s.[Familia_Producto_Sede],
        CASE
            WHEN s.[Ancho de banda] IS NULL THEN 0
            WHEN LOWER(LTRIM(RTRIM(s.[Ancho de banda]))) LIKE '%gbps%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        s.[Ancho de banda],
                        CHARINDEX('gbps', LOWER(s.[Ancho de banda])) - 1
                    )
                ) * 1000
            WHEN LOWER(LTRIM(RTRIM(s.[Ancho de banda]))) LIKE '%gb%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        s.[Ancho de banda],
                        CHARINDEX('gb', LOWER(s.[Ancho de banda])) - 1
                    )
                ) * 1000
            WHEN LOWER(LTRIM(RTRIM(s.[Ancho de banda]))) LIKE '%mbps%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        s.[Ancho de banda],
                        CHARINDEX('mbps', LOWER(s.[Ancho de banda])) - 1
                    )
                )
            WHEN LOWER(LTRIM(RTRIM(s.[Ancho de banda]))) LIKE '%kbps%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        s.[Ancho de banda],
                        CHARINDEX('kbps', LOWER(s.[Ancho de banda])) - 1
                    )
                ) / 1000
            ELSE TRY_CONVERT(
                DECIMAL(18,4),
                LTRIM(RTRIM(s.[Ancho de banda]))
            )
        END AS [Ancho de banda (Nro)]
    FROM SFDC.DM_PRICING_SEDE s
),
PricingPromedioSede AS
(
    SELECT
        p.[Sede]
    FROM SFDC.DM_PRICING_X_SEDE p
    WHERE p.[Pricing por Sede On/Off] = 'SI'
    GROUP BY
        p.[Sede]
),
Funnels AS
(
    SELECT
        f.[FUNNEL],
        f.[SEDE],
        f.[FechaCreacion],
        f.[NOMBRE_COMERCIAL_FUNNEL],
        f.[ESTADO_FUNNEL],
        CASE
            WHEN NULLIF(
                LTRIM(RTRIM(
                    CAST(f.[DIGITO_VERIFICACION_FUNNEL] AS VARCHAR(20))
                )),
                ''
            ) IS NULL
            THEN LTRIM(RTRIM(
                CAST(
                    f.[NRO_IDENTIFICACION_CLIENTE_FUNNEL]
                    AS VARCHAR(50)
                )
            ))
            ELSE CONCAT(
                LTRIM(RTRIM(
                    CAST(
                        f.[NRO_IDENTIFICACION_CLIENTE_FUNNEL]
                        AS VARCHAR(50)
                    )
                )),
                '-',
                LTRIM(RTRIM(
                    CAST(
                        f.[DIGITO_VERIFICACION_FUNNEL]
                        AS VARCHAR(20)
                    )
                ))
            )
        END AS [NIT_CONCATENADO]
    FROM DTM.SF_FUNNELV2 f
)
INSERT INTO #Base
(
    [FUNNEL],
    [FechaCreacion],
    [NOMBRE_COMERCIAL_FUNNEL],
    [ESTADO_FUNNEL],
    [NIT_CONCATENADO],
    [Consecutivo de Sede],
    [Departamento],
    [Municipio],
    [DANE_Mpio],
    [Producto],
    [Plan],
    [Familia_Producto_Sede],
    [Ancho de banda (Nro)]
)
SELECT
    f.[FUNNEL],
    f.[FechaCreacion],
    f.[NOMBRE_COMERCIAL_FUNNEL],
    f.[ESTADO_FUNNEL],
    f.[NIT_CONCATENADO],
    s.[Consecutivo de Sede],
    s.[Departamento],
    s.[Municipio],
    s.[DANE_Mpio],
    s.[Producto],
    s.[Plan],
    s.[Familia_Producto_Sede],
    s.[Ancho de banda (Nro)]
FROM Funnels f
INNER JOIN Sedes s
    ON f.[SEDE] = s.[Consecutivo de Sede]
INNER JOIN PricingPromedioSede ps
    ON s.[Consecutivo de Sede] = ps.[Sede]
WHERE 1 = 1
    AND (:fecha_inicio IS NULL
         OR f.[FechaCreacion] >= :fecha_inicio)
    AND (:capacity_min IS NULL
         OR s.[Ancho de banda (Nro)] >= :capacity_min)
    AND (:capacity_max IS NULL
         OR s.[Ancho de banda (Nro)] <= :capacity_max)
    AND (:filter_funnel_status = 0
         OR f.[ESTADO_FUNNEL] IN :funnel_statuses)
    AND (:filter_department = 0
         OR s.[Departamento] IN :departments)
    AND (:filter_municipality = 0
         OR s.[Municipio] IN :municipalities)
    AND (:filter_dane = 0
         OR s.[DANE_Mpio] IN :danes)
    AND (:filter_product = 0
         OR s.[Producto] IN :products)
    AND (:filter_plan = 0
         OR s.[Plan] IN :plans)
    AND (:filter_product_family = 0
         OR s.[Familia_Producto_Sede] IN :product_families)
    AND (:filter_client = 0
         OR f.[NIT_CONCATENADO] IN :clients);
"""

QUERY_FILTER_OPTIONS_SUMMARY = """
SELECT
    COUNT(DISTINCT [Consecutivo de Sede]) AS TOTAL_SEDES
FROM #Base;
"""

QUERY_FILTER_OPTIONS_CLIENTS = """
SELECT DISTINCT
    [NIT_CONCATENADO] AS NIT,
    [NOMBRE_COMERCIAL_FUNNEL] AS BUSINESS_NAME
FROM #Base
WHERE [NIT_CONCATENADO] IS NOT NULL
ORDER BY
    [NIT_CONCATENADO],
    [NOMBRE_COMERCIAL_FUNNEL];
"""

QUERY_FILTER_OPTIONS_STATUSES = """
SELECT DISTINCT
    [ESTADO_FUNNEL] AS STATUS
FROM #Base
WHERE [ESTADO_FUNNEL] IS NOT NULL
ORDER BY
    [ESTADO_FUNNEL];
"""

QUERY_FILTER_OPTIONS_LOCATIONS = """
SELECT DISTINCT
    [Departamento] AS DEPARTMENT,
    [Municipio] AS MUNICIPALITY,
    [DANE_Mpio] AS DANE
FROM #Base
WHERE [Departamento] IS NOT NULL
ORDER BY
    [Departamento],
    [Municipio],
    [DANE_Mpio];
"""

QUERY_FILTER_OPTIONS_PRODUCTS = """
SELECT DISTINCT
    [Familia_Producto_Sede] AS FAMILY,
    [Producto] AS PRODUCT,
    [Plan] AS [PLAN]
FROM #Base
WHERE [Familia_Producto_Sede] IS NOT NULL
ORDER BY
    [Familia_Producto_Sede],
    [Producto],
    [Plan];
"""

#
# EOF
#
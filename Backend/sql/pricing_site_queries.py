QUERY_PRICED_SITES_COUNT = """
WITH Funnels AS
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
                    CAST(
                        f.[DIGITO_VERIFICACION_FUNNEL]
                        AS VARCHAR(20)
                    )
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

    WHERE 1=1
    AND (
        :fecha_inicio IS NULL
        OR f.[FechaCreacion] >= :fecha_inicio
    )
    AND (
        :filter_funnel = 0
        OR f.[FUNNEL] IN :funnels
    )
    AND (
        :filter_funnel_status = 0
        OR f.[ESTADO_FUNNEL] = :funnel_statuses
    )
		
),
ClientFunnels AS 
(
    SELECT
        *
    FROM Funnels f
    WHERE 1 = 1
    AND (
        :filter_client = 0
        OR f.[NIT_CONCATENADO] IN :clients
    )
),
Sedes AS 
(
    SELECT
        s.Funnel,
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
        END AS [Ancho de banda (Nro)],
        CONCAT(
            UPPER(LTRIM(RTRIM(s.Departamento))), '_',
            UPPER(LTRIM(RTRIM(s.Municipio))), '_',
            COALESCE(
                LTRIM(RTRIM(CAST(s.Latitud AS VARCHAR(50)))),
                'NULL'
            ), '_',
            COALESCE(
                LTRIM(RTRIM(CAST(s.Longitud AS VARCHAR(50)))),
                'NULL'
            ), '_',
            UPPER(
                LTRIM(
                    RTRIM(
                        COALESCE(s.[Direccion Sede], 'NULL')
                    )
                )
            ), '_',
            UPPER(
                LTRIM(
                    RTRIM(
                        COALESCE(s.Producto, 'NULL')
                    )
                )
            ), '_',
            UPPER(
                LTRIM(
                    RTRIM(
                        COALESCE(s.[Plan], 'NULL')
                    )
                )
            )
        ) AS [ID_Ubicacion_Producto_Plan]
    FROM SFDC.DM_PRICING_SEDE s
    INNER JOIN ClientFunnels cf
        ON s.[Consecutivo de Sede] = cf.SEDE
    WHERE 1 = 1
    AND (
        :filter_department = 0
        OR s.[Departamento] IN :departments
    )
    AND (
        :filter_municipality = 0
        OR s.Municipio IN :municipalities
    )
    AND (
        :filter_dane = 0
        OR s.[DANE_Mpio] IN :danes
    )
    AND (
        :filter_product_family = 0
        OR s.Familia_Producto_Sede IN :product_families
    )
    AND (
        :filter_product = 0
        OR s.Producto IN :products
    )
    AND (
        :filter_plan = 0
        or s.[Plan] IN :plans
    )
),
CapSedes AS 
(
    SELECT
        fs.*
    FROM Sedes fs
    WHERE 1 = 1
    AND (
        :capacity_max IS NULL
        OR fs.[Ancho de banda (Nro)] <= :capacity_max
    )
    AND (
        :capacity_min IS NULL
        OR fs.[Ancho de banda (Nro)] >= :capacity_min
    )
),
PricingPromedioSede AS
(
    SELECT
        p.[Sede],
        AVG(ISNULL(p.[Recurrente Mes], 0)) AS MRC_PROMEDIO
    FROM SFDC.DM_PRICING_X_SEDE p
    INNER JOIN CapSedes fs
        ON p.Sede = fs.[Consecutivo de Sede]
    WHERE p.[Pricing por Sede On/Off] = 'SI'
    GROUP BY
        p.[Sede]
),
MRC_Ubicacion AS
(
    SELECT
        s.[ID_Ubicacion_Producto_Plan],
        MAX(ps.MRC_PROMEDIO) AS MRC_MAX_UBICACION
    FROM CapSedes s
    INNER JOIN PricingPromedioSede ps
        ON s.[Consecutivo de Sede] = ps.[Sede]
    GROUP BY
        s.[ID_Ubicacion_Producto_Plan]
),
FunnelUbicaciones AS
(
    SELECT DISTINCT
        [FUNNEL],
        [ID_Ubicacion_Producto_Plan]
    FROM CapSedes
),
FunnelMRC AS
(
    SELECT
        fu.[FUNNEL],
        SUM(mu.MRC_MAX_UBICACION) AS MRC_FUNNEL
    FROM FunnelUbicaciones fu
    INNER JOIN MRC_Ubicacion mu
        ON fu.[ID_Ubicacion_Producto_Plan]
         = mu.[ID_Ubicacion_Producto_Plan]
    GROUP BY
        fu.[FUNNEL]
)
SELECT
    (
        SELECT COUNT(DISTINCT sed.[Consecutivo de Sede])
        FROM CapSedes sed
        INNER JOIN PricingPromedioSede psd
            ON sed.[Consecutivo de Sede] = psd.Sede
    ) AS TOTAL_SEDES,
    (
        SELECT COUNT(DISTINCT sed.[FUNNEL])
        FROM CapSedes sed
        INNER JOIN PricingPromedioSede psd
            ON sed.[Consecutivo de Sede] = psd.Sede
    ) AS TOTAL_FUNNELS,
    COALESCE(
        (
            SELECT SUM(MRC_FUNNEL)
            FROM FunnelMRC
        ),
        0
    ) AS TOTAL_MRC;
"""

QUERY_PRICED_SITES = """
WITH Funnels AS
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
                    CAST(
                        f.[DIGITO_VERIFICACION_FUNNEL]
                        AS VARCHAR(20)
                    )
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

    WHERE 1=1
    AND (
        :fecha_inicio IS NULL
        OR f.[FechaCreacion] >= :fecha_inicio
    )
    AND (
        :filter_funnel = 0
        OR f.[FUNNEL] IN :funnels
    )
    AND (
        :filter_funnel_status = 0
        OR f.[ESTADO_FUNNEL] = :funnel_statuses
    )
		
),
ClientFunnels AS 
(
    SELECT
        *
    FROM Funnels f
    WHERE 1 = 1
    AND (
        :filter_client = 0
        OR f.[NIT_CONCATENADO] IN :clients
    )
),
Sedes AS 
(
    SELECT
        s.Funnel,
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
        END AS [Ancho de banda (Nro)],
        CONCAT(
            UPPER(LTRIM(RTRIM(s.Departamento))), '_',
            UPPER(LTRIM(RTRIM(s.Municipio))), '_',
            COALESCE(
                LTRIM(RTRIM(CAST(s.Latitud AS VARCHAR(50)))),
                'NULL'
            ), '_',
            COALESCE(
                LTRIM(RTRIM(CAST(s.Longitud AS VARCHAR(50)))),
                'NULL'
            ), '_',
            UPPER(
                LTRIM(
                    RTRIM(
                        COALESCE(s.[Direccion Sede], 'NULL')
                    )
                )
            ), '_',
            UPPER(
                LTRIM(
                    RTRIM(
                        COALESCE(s.Producto, 'NULL')
                    )
                )
            ), '_',
            UPPER(
                LTRIM(
                    RTRIM(
                        COALESCE(s.[Plan], 'NULL')
                    )
                )
            )
        ) AS [ID_Ubicacion_Producto_Plan]
    FROM SFDC.DM_PRICING_SEDE s

    INNER JOIN ClientFunnels cf
        ON s.[Consecutivo de Sede] = cf.SEDE

    WHERE 1 = 1
    AND (
        :filter_department = 0
        OR s.[Departamento] IN :departments
    )
    AND (
        :filter_municipality = 0
        OR s.Municipio IN :municipalities
    )
    AND (
        :filter_dane = 0
        OR s.[DANE_Mpio] IN :danes
    )
    AND (
        :filter_product_family = 0
        OR s.Familia_Producto_Sede IN :product_families
    )
    AND (
        :filter_product = 0
        OR s.Producto IN :products
    )
    AND (
        :filter_plan = 0
        or s.[Plan] IN :plans
    )
),
CapSedes AS 
(
    SELECT
        fs.*
    FROM Sedes fs
    WHERE 1 = 1
    AND (
        :capacity_max IS NULL
        OR fs.[Ancho de banda (Nro)] <= :capacity_max
    )
    AND (
        :capacity_min IS NULL
        OR fs.[Ancho de banda (Nro)] >= :capacity_min
    )
),
PricingPromedioSede AS
(
    SELECT
        p.[Sede],
        COUNT(DISTINCT p.[Pricing]) AS NUM_PRICINGS,
        AVG(ISNULL(p.[Recurrente Mes], 0)) AS MRC_PROMEDIO,
        AVG(ISNULL(p.[No Recurrente Mes], 0)) AS NRC_PROMEDIO
    FROM SFDC.DM_PRICING_X_SEDE p
    INNER JOIN CapSedes fs
        ON p.Sede = fs.[Consecutivo de Sede]
    WHERE p.[Pricing por Sede On/Off] = 'SI'
    GROUP BY
        p.[Sede]
),
MRC_Ubicacion AS
(
    SELECT
        s.[ID_Ubicacion_Producto_Plan],
        MAX(ps.MRC_PROMEDIO) AS MRC_MAX_UBICACION
    FROM CapSedes s
    INNER JOIN PricingPromedioSede ps
        ON s.[Consecutivo de Sede] = ps.[Sede]
    GROUP BY
        s.[ID_Ubicacion_Producto_Plan]
),
FunnelUbicaciones AS
(
    SELECT DISTINCT
        [FUNNEL],
        [ID_Ubicacion_Producto_Plan]
    FROM CapSedes
),
FunnelMRC AS
(
    SELECT
        fu.[FUNNEL],
        SUM(mu.MRC_MAX_UBICACION) AS MRC_FUNNEL
    FROM FunnelUbicaciones fu
    INNER JOIN MRC_Ubicacion mu
        ON fu.[ID_Ubicacion_Producto_Plan]
         = mu.[ID_Ubicacion_Producto_Plan]
    GROUP BY
        fu.[FUNNEL]
),
FunnelUnique AS
(
    SELECT
        f.[FUNNEL],
        MAX([FechaCreacion]) AS [FechaCreacion],
        MAX([NOMBRE_COMERCIAL_FUNNEL]) AS [NOMBRE_COMERCIAL_FUNNEL],
        MAX([ESTADO_FUNNEL]) AS [ESTADO_FUNNEL],
        MAX([NIT_CONCATENADO]) AS [NIT_CONCATENADO],
        MAX(TARGET_MRC_GRUPAL_FUNNEL) AS TARGET_MRC_GRUPAL_FUNNEL,
        MAX(fm.MRC_FUNNEL) AS MRC_FUNNEL
    FROM ClientFunnels f
    INNER JOIN FunnelMRC fm
        ON f.[FUNNEL] = fm.[FUNNEL]
    GROUP BY
        f.[FUNNEL]
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
        MRC_FUNNEL
    FROM FunnelUnique
    ORDER BY
        MRC_FUNNEL DESC,
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
    fp.MRC_FUNNEL,
    sed.[Consecutivo de Sede],
    sed.Departamento,
    sed.Municipio,
    sed.DANE_Mpio,
    sed.Producto,
    sed.[Plan],
    sed.[Familia_Producto_Sede],
    sed.[Ultimo kilometro (UK)],
    sed.[Distancia FO Red ACC],
    sed.[Tipo de Tecnologia],
    sed.[Ancho de banda],
    sed.[Ancho de banda (Nro)],
    psd.NUM_PRICINGS,
    psd.MRC_PROMEDIO,
    psd.NRC_PROMEDIO,
    psd.MRC_PROMEDIO / NULLIF(sed.[Ancho de banda (Nro)], 0) AS VLR_MBPS
FROM FunnelPage fp
INNER JOIN CapSedes sed
    ON fp.FUNNEL = sed.Funnel
INNER JOIN PricingPromedioSede psd
    ON sed.[Consecutivo de Sede] = psd.Sede
ORDER BY
    fp.[FechaCreacion] DESC,
    fp.[FUNNEL] ASC,
    sed.[Consecutivo de Sede] ASC;
"""

QUERY_PRICED_SITES_CREATE_BASE = """
CREATE TABLE #PricingBase
(
    [FUNNEL] NVARCHAR(80),
    [FechaCreacion] DATETIME,
    [NOMBRE_COMERCIAL_FUNNEL] NVARCHAR(255),
    [ESTADO_FUNNEL] NVARCHAR(255),
    [NIT_CONCATENADO] NVARCHAR(100),
    [TARGET_MRC_GRUPAL_FUNNEL] DECIMAL(18,4),
    [TipoOferta] NVARCHAR(30),
    [MRC_FUNNEL] DECIMAL(18,4),

    [Consecutivo de Sede] NVARCHAR(100),
    [Departamento] NVARCHAR(255),
    [Municipio] NVARCHAR(255),
    [DANE_Mpio] NVARCHAR(50),
    [Producto] NVARCHAR(255),
    [Plan] NVARCHAR(255),
    [Familia_Producto_Sede] NVARCHAR(255),
    [Ultimo kilometro (UK)] NVARCHAR(255),
    [Distancia FO Red ACC] DECIMAL(18,4),
    [Tipo de Tecnologia] NVARCHAR(255),
    [Ancho de banda] NVARCHAR(255),
    [Ancho de banda (Nro)] DECIMAL(18,4),

    [ID_Ubicacion_Producto_Plan] NVARCHAR(MAX),

    [NUM_PRICINGS] INT,
    [MRC_PROMEDIO] DECIMAL(18,4),
    [NRC_PROMEDIO] DECIMAL(18,4),
    [VLR_MBPS] DECIMAL(18,6)
);
"""

QUERY_PRICED_SITES_INSERT_BASE = """
WITH Funnels AS
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
                    CAST(
                        f.[DIGITO_VERIFICACION_FUNNEL]
                        AS VARCHAR(20)
                    )
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

    WHERE 1=1
    AND f.[FechaCreacion] >= :fecha_inicio
    AND (
        :filter_funnel = 0
        OR f.[FUNNEL] IN :funnels 
    )
    AND (
        :filter_funnel_status = 0
        OR f.[ESTADO_FUNNEL] = :funnel_statuses
    )
		
),
ClientFunnels AS 
(
    SELECT
        *
    FROM Funnels f
    WHERE 1 = 1
    AND (
        :filter_client = 0
        OR f.[NIT_CONCATENADO] IN :clients
    )
),
Sedes AS 
(
    SELECT
        s.Funnel,
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
        END AS [Ancho de banda (Nro)],
        CONCAT(
            UPPER(LTRIM(RTRIM(s.DANE_Mpio))), '_',
            COALESCE(
                LTRIM(RTRIM(CAST(s.Latitud AS VARCHAR(50)))),
                'NULL'
            ), '_',
            COALESCE(
                LTRIM(RTRIM(CAST(s.Longitud AS VARCHAR(50)))),
                'NULL'
            ), '_',
            UPPER(
                LTRIM(
                    RTRIM(
                        COALESCE(s.[Direccion Sede], 'NULL')
                    )
                )
            ), '_',
            UPPER(
                LTRIM(
                    RTRIM(
                        COALESCE(s.Producto, 'NULL')
                    )
                )
            ), '_',
            UPPER(
                LTRIM(
                    RTRIM(
                        COALESCE(s.[Plan], 'NULL')
                    )
                )
            )
        ) AS [ID_Ubicacion_Producto_Plan]
    FROM SFDC.DM_PRICING_SEDE s

    INNER JOIN ClientFunnels cf
        ON s.[Consecutivo de Sede] = cf.SEDE

    WHERE 1 = 1
    AND (
        :filter_department = 0
        OR s.[Departamento] IN :departments
    )
    AND (
        :filter_municipality = 0
        OR s.Municipio IN :municipalities
    )
    AND (
        :filter_dane = 0
        OR s.[DANE_Mpio] IN :danes
    )
    AND (
        :filter_product_family = 0
        OR s.Familia_Producto_Sede IN :product_families
    )
    AND (
        :filter_product = 0
        OR s.Producto IN :products
    )
    AND (
        :filter_plan = 0
        OR s.[Plan] IN :plans
    )
),
CapSedes AS 
(
    SELECT
        fs.*
    FROM Sedes fs
    WHERE 1 = 1
    AND (
        :capacity_max IS NULL
        OR fs.[Ancho de banda (Nro)] <= :capacity_max
    )
    AND (
        :capacity_min IS NULL
        OR fs.[Ancho de banda (Nro)] >= :capacity_min
    )
),
PricingPromedioSede AS
(
    SELECT
        p.[Sede],
        COUNT(DISTINCT p.[Pricing]) AS NUM_PRICINGS,
        AVG(ISNULL(p.[Recurrente Mes], 0)) AS MRC_PROMEDIO,
        AVG(ISNULL(p.[No Recurrente Mes], 0)) AS NRC_PROMEDIO
    FROM SFDC.DM_PRICING_X_SEDE p
    INNER JOIN CapSedes fs
        ON p.Sede = fs.[Consecutivo de Sede]
    WHERE p.[Pricing por Sede On/Off] = 'SI'
    GROUP BY
        p.[Sede]
),
MRC_Ubicacion AS
(
    SELECT
        s.[ID_Ubicacion_Producto_Plan],
        MAX(ps.MRC_PROMEDIO) AS MRC_MAX_UBICACION
    FROM CapSedes s
    INNER JOIN PricingPromedioSede ps
        ON s.[Consecutivo de Sede] = ps.[Sede]
    GROUP BY
        s.[ID_Ubicacion_Producto_Plan]
),
FunnelUbicaciones AS
(
    SELECT DISTINCT
        [FUNNEL],
        [ID_Ubicacion_Producto_Plan]
    FROM CapSedes
),
FunnelMRC AS
(
    SELECT
        fu.[FUNNEL],
        SUM(mu.MRC_MAX_UBICACION) AS MRC_FUNNEL
    FROM FunnelUbicaciones fu
    INNER JOIN MRC_Ubicacion mu
        ON fu.[ID_Ubicacion_Producto_Plan]
         = mu.[ID_Ubicacion_Producto_Plan]
    GROUP BY
        fu.[FUNNEL]
)
INSERT INTO #PricingBase
(
    [FUNNEL],
    [FechaCreacion],
    [NOMBRE_COMERCIAL_FUNNEL],
    [ESTADO_FUNNEL],
    [NIT_CONCATENADO],
    [TARGET_MRC_GRUPAL_FUNNEL],
    [MRC_FUNNEL],
    [Consecutivo de Sede],
    [Departamento],
    [Municipio],
    [DANE_Mpio],
    [Producto],
    [Plan],
    [Familia_Producto_Sede],
    [Ultimo kilometro (UK)],
    [Distancia FO Red ACC],
    [Tipo de Tecnologia],
    [Ancho de banda],
    [Ancho de banda (Nro)],
    [ID_Ubicacion_Producto_Plan],
    [NUM_PRICINGS],
    [MRC_PROMEDIO],
    [NRC_PROMEDIO],
    [VLR_MBPS]
)
SELECT
    cf.[FUNNEL],
    cf.[FechaCreacion],
    cf.[NOMBRE_COMERCIAL_FUNNEL],
    cf.[ESTADO_FUNNEL],
    cf.[NIT_CONCATENADO],
    cf.[TARGET_MRC_GRUPAL_FUNNEL],
    fm.MRC_FUNNEL,
    sed.[Consecutivo de Sede],
    sed.Departamento,
    sed.Municipio,
    sed.DANE_Mpio,
    sed.Producto,
    sed.[Plan],
    sed.[Familia_Producto_Sede],
    sed.[Ultimo kilometro (UK)],
    sed.[Distancia FO Red ACC],
    sed.[Tipo de Tecnologia],
    sed.[Ancho de banda],
    sed.[Ancho de banda (Nro)],
    sed.[ID_Ubicacion_Producto_Plan],
    psd.NUM_PRICINGS,
    psd.MRC_PROMEDIO,
    psd.NRC_PROMEDIO,
    psd.MRC_PROMEDIO
        / NULLIF(
            sed.[Ancho de banda (Nro)],
            0
        ) AS VLR_MBPS

FROM ClientFunnels cf

INNER JOIN CapSedes sed
    ON cf.[Sede] = sed.[Consecutivo de Sede]

INNER JOIN PricingPromedioSede psd
    ON sed.[Consecutivo de Sede] = psd.[Sede]

INNER JOIN FunnelMRC fm
    ON cf.[FUNNEL] = fm.[FUNNEL];
"""

QUERY_PRICED_SITES_INSERT_BASE_V2 = """
WITH Funnels AS
(
	SELECT
		f.[FUNNEL],
        f.[SEDE],
        f.[FechaCreacion],
        f.[NOMBRE_COMERCIAL_FUNNEL],
        f.[ESTADO_FUNNEL],
        f.TARGET_MRC_GRUPAL_FUNNEL,
        f.TipoOferta,
        CASE
            WHEN NULLIF(
                LTRIM(RTRIM(
                    CAST(
                        f.[DIGITO_VERIFICACION_FUNNEL]
                        AS VARCHAR(20)
                    )
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

    WHERE 1=1
    AND f.[FechaCreacion] >= :fecha_inicio
    AND (
        :filter_funnel = 0
        OR f.[FUNNEL] IN :funnels 
    )
    AND (
        :filter_funnel_status = 0
        OR f.[ESTADO_FUNNEL] = :funnel_statuses
    )
		
),
ClientFunnels AS 
(
    SELECT
        *
    FROM Funnels f
    WHERE 1 = 1
    AND (
        :filter_client = 0
        OR f.[NIT_CONCATENADO] IN :clients
    )
),
Sedes AS 
(
    SELECT
        s.Funnel,
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
    INNER JOIN ClientFunnels cf
        ON s.[Consecutivo de Sede] = cf.SEDE
    WHERE 1 = 1
    AND (
        :filter_department = 0
        OR s.[Departamento] IN :departments
    )
    AND (
        :filter_municipality = 0
        OR s.Municipio IN :municipalities
    )
    AND (
        :filter_dane = 0
        OR s.[DANE_Mpio] IN :danes
    )
    AND (
        :filter_product_family = 0
        OR s.Familia_Producto_Sede IN :product_families
    )
    AND (
        :filter_product = 0
        OR s.Producto IN :products
    )
    AND (
        :filter_plan = 0
        OR s.[Plan] IN :plans
    )
),
CapSedes AS 
(
    SELECT
        fs.*
    FROM Sedes fs
    WHERE 1 = 1
    AND (
        :capacity_max IS NULL
        OR fs.[Ancho de banda (Nro)] <= :capacity_max
    )
    AND (
        :capacity_min IS NULL
        OR fs.[Ancho de banda (Nro)] >= :capacity_min
    )
),
PricingPromedioSede AS
(
    SELECT
        p.[Sede],
        COUNT(DISTINCT p.[Pricing]) AS NUM_PRICINGS,
        AVG(ISNULL(p.[Recurrente Mes], 0)) AS MRC_PROMEDIO,
        AVG(ISNULL(p.[No Recurrente Mes], 0)) AS NRC_PROMEDIO
    FROM SFDC.DM_PRICING_X_SEDE p
    INNER JOIN CapSedes fs
        ON p.Sede = fs.[Consecutivo de Sede]
    WHERE p.[Pricing por Sede On/Off] = 'SI'
    GROUP BY
        p.[Sede]
),
FunnelMRC AS
(
    SELECT
        cf.[FUNNEL],
        SUM(psd.MRC_PROMEDIO) AS MRC_FUNNEL
    FROM ClientFunnels cf
    INNER JOIN PricingPromedioSede psd
        ON cf.[SEDE] = psd.[Sede]
    GROUP BY
        cf.[FUNNEL]
)
INSERT INTO #PricingBase
(
    [FUNNEL],
    [FechaCreacion],
    [NOMBRE_COMERCIAL_FUNNEL],
    [ESTADO_FUNNEL],
    [NIT_CONCATENADO],
    [TARGET_MRC_GRUPAL_FUNNEL],
    [TipoOferta],
    [MRC_FUNNEL],
    [Consecutivo de Sede],
    [Departamento],
    [Municipio],
    [DANE_Mpio],
    [Producto],
    [Plan],
    [Familia_Producto_Sede],
    [Ultimo kilometro (UK)],
    [Distancia FO Red ACC],
    [Tipo de Tecnologia],
    [Ancho de banda],
    [Ancho de banda (Nro)],
    [NUM_PRICINGS],
    [MRC_PROMEDIO],
    [NRC_PROMEDIO],
    [VLR_MBPS]
)
SELECT
    cf.[FUNNEL],
    cf.[FechaCreacion],
    cf.[NOMBRE_COMERCIAL_FUNNEL],
    cf.[ESTADO_FUNNEL],
    cf.[NIT_CONCATENADO],
    cf.[TARGET_MRC_GRUPAL_FUNNEL],
    cf.[TipoOferta],
    fm.MRC_FUNNEL,
    sed.[Consecutivo de Sede],
    sed.Departamento,
    sed.Municipio,
    sed.DANE_Mpio,
    sed.Producto,
    sed.[Plan],
    sed.[Familia_Producto_Sede],
    sed.[Ultimo kilometro (UK)],
    sed.[Distancia FO Red ACC],
    sed.[Tipo de Tecnologia],
    sed.[Ancho de banda],
    sed.[Ancho de banda (Nro)],
    psd.NUM_PRICINGS,
    psd.MRC_PROMEDIO,
    psd.NRC_PROMEDIO,
    psd.MRC_PROMEDIO
        / NULLIF(
            sed.[Ancho de banda (Nro)],
            0
        ) AS VLR_MBPS
FROM ClientFunnels cf
INNER JOIN CapSedes sed
    ON cf.[Sede] = sed.[Consecutivo de Sede]
INNER JOIN PricingPromedioSede psd
    ON sed.[Consecutivo de Sede] = psd.[Sede]
INNER JOIN FunnelMRC fm
    ON cf.[FUNNEL] = fm.[FUNNEL];
"""

QUERY_PRICED_SITES_MEASURES = """
SELECT
    COUNT(DISTINCT [Consecutivo de Sede]) AS TOTAL_SEDES,
    COUNT(DISTINCT [FUNNEL]) AS TOTAL_FUNNELS,
    COALESCE(
        (
            SELECT SUM(MRC_FUNNEL)
            FROM
            (
                SELECT
                    [FUNNEL],
                    MAX(MRC_FUNNEL) AS MRC_FUNNEL
                FROM #PricingBase
                GROUP BY [FUNNEL]
            ) f
        ),
        0
    ) AS TOTAL_MRC
FROM #PricingBase;
"""

QUERY_PRICED_SITES_EXPORT = """
SELECT
    [FUNNEL],
    [ESTADO_FUNNEL],
    [TipoOferta],
    [NIT_CONCATENADO],
    [NOMBRE_COMERCIAL_FUNNEL],
    [FechaCreacion],
    [Consecutivo de Sede],
    [Departamento],
    [Municipio],
    [DANE_Mpio],
    [Plan],
    [Ancho de banda (Nro)],
    [NUM_PRICINGS],
    [MRC_PROMEDIO],
    [NRC_PROMEDIO],
    [VLR_MBPS]
FROM #PricingBase
"""

QUERY_PRICED_SITES_PAGINATION = """
WITH FunnelPage AS
(
    SELECT
        [FUNNEL],
        MAX([FechaCreacion]) AS [FechaCreacion],
        MAX([NOMBRE_COMERCIAL_FUNNEL]) AS [NOMBRE_COMERCIAL_FUNNEL],
        MAX([ESTADO_FUNNEL]) AS [ESTADO_FUNNEL],
        MAX([NIT_CONCATENADO]) AS [NIT_CONCATENADO],
        MAX([TARGET_MRC_GRUPAL_FUNNEL]) AS [TARGET_MRC_GRUPAL_FUNNEL],
        MAX([MRC_FUNNEL]) AS [MRC_FUNNEL],
        MAX([TipoOferta]) AS [TipoOferta]
    FROM #PricingBase
    GROUP BY
        [FUNNEL]
    ORDER BY
        MAX([MRC_FUNNEL]) DESC,
        MAX([FechaCreacion]) DESC
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
    fp.[TipoOferta],
    fp.[MRC_FUNNEL],
    sed.[Consecutivo de Sede],
    sed.Departamento,
    sed.Municipio,
    sed.DANE_Mpio,
    sed.Producto,
    sed.[Plan],
    sed.[Familia_Producto_Sede],
    sed.[Ultimo kilometro (UK)],
    sed.[Distancia FO Red ACC],
    sed.[Tipo de Tecnologia],
    sed.[Ancho de banda],
    sed.[Ancho de banda (Nro)],
    sed.[NUM_PRICINGS],
    sed.[MRC_PROMEDIO],
    sed.[NRC_PROMEDIO],
    sed.[VLR_MBPS]
FROM FunnelPage fp
INNER JOIN #PricingBase sed
    ON fp.[FUNNEL] = sed.[FUNNEL]
;
--ORDER BY
--    fp.[FechaCreacion] DESC,
--    fp.[FUNNEL] ASC,
--    sed.[Consecutivo de Sede] ASC;
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

QUERY_FILTER_OPTIONS_FUNNELS = """
SELECT DISTINCT
    [FUNNEL] AS FUNNEL
FROM #Base
WHERE [FUNNEL] IS NOT NULL
ORDER BY
    [FUNNEL];
"""
#
# EOF
#
QUERY_LOCATIONS_TRACKER_CREATE_BASE_V1 = """
CREATE TABLE #LocationTrackerBase
(
    [Consecutivo de Sede] NVARCHAR(80),
    FechaCreacion DATETIME,
    Funnel NVARCHAR(80),
    ESTADO_FUNNEL NVARCHAR(80),
    NOMBRE_COMERCIAL_FUNNEL NVARCHAR(255),
    NIT NVARCHAR(27),
    Vendedor NVARCHAR(100),
    Familia_Producto_Sede NVARCHAR(50),
    Producto NVARCHAR(255),
    [Plan] NVARCHAR(80),
    [Ancho de banda (Nro)] DECIMAL(18,2),
    Departamento NVARCHAR(100),
    Municipio NVARCHAR(100),
    DANE_Mpio NVARCHAR(20),
    Longitud FLOAT,
    Latitud FLOAT,
    [Direccion] NVARCHAR(1300),
    [Viabilidad Positiva] VARCHAR(2),
    [Distancia Total Viabilidad] FLOAT,
    [Total por un punto (USD) Viabilidad] FLOAT
);
"""

QUERY_LOCATIONS_TRACKER_INSERT_BASE_V1 = """
WITH FunnelsRanked AS
(
    SELECT 
        FUNNEL,
        SEDE,
        ESTADO_FUNNEL,
        NOMBRE_COMERCIAL_FUNNEL,
        CASE 
            WHEN DIGITO_VERIFICACION_FUNNEL IS NULL 
                THEN CAST(NRO_IDENTIFICACION_CLIENTE_FUNNEL AS NVARCHAR(20))
            ELSE CONCAT(
                NRO_IDENTIFICACION_CLIENTE_FUNNEL,
                '-',
                DIGITO_VERIFICACION_FUNNEL
            )
        END AS NIT,
        TARGET_MRC_GRUPAL_FUNNEL,
        TipoOferta,
        CLAVE_VENDEDOR_FUNNEL,
        FechaCreacion,
        ROW_NUMBER() OVER (
            PARTITION BY SEDE
            ORDER BY FechaCreacion DESC
        ) AS RN
    FROM DTM.SF_FUNNELV2
    WHERE FechaCreacion >= DATEADD(MONTH, -3, GETDATE())
      AND ESTADO_FUNNEL NOT IN
      (
          'Cliente Acepta',
          'Cliente no acepta',
          'Gestionado mesa de control'
      )
),
Funnels AS
(
    SELECT 
    f1.*,
    f2.Vendedor
    FROM FunnelsRanked f1
    INNER JOIN SFDC.DM_PRICING_FUNNEL f2
        ON f1.FUNNEL = f2.FUNNEL
    WHERE RN = 1
),
Sedes AS 
(
    SELECT 
        sed.[Consecutivo de Sede],
        sed.Funnel,
        f.ESTADO_FUNNEL,
        f.FechaCreacion,
        f.NOMBRE_COMERCIAL_FUNNEL,
        f.Vendedor,
        f.NIT,
        sed.Familia_Producto_Sede,
        sed.Producto,
        sed.[Plan],
        CASE
            WHEN sed.[Ancho de banda] IS NULL THEN 0

            WHEN LOWER(LTRIM(RTRIM(sed.[Ancho de banda]))) LIKE '%gbps%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        LOWER(LTRIM(RTRIM(sed.[Ancho de banda]))),
                        CHARINDEX('gbps', LOWER(LTRIM(RTRIM(sed.[Ancho de banda])))) - 1
                    )
                ) * 1000

            WHEN LOWER(LTRIM(RTRIM(sed.[Ancho de banda]))) LIKE '%gb%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        LOWER(LTRIM(RTRIM(sed.[Ancho de banda]))),
                        CHARINDEX('gb', LOWER(LTRIM(RTRIM(sed.[Ancho de banda])))) - 1
                    )
                ) * 1000

            WHEN LOWER(LTRIM(RTRIM(sed.[Ancho de banda]))) LIKE '%mbps%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        LOWER(LTRIM(RTRIM(sed.[Ancho de banda]))),
                        CHARINDEX('mbps', LOWER(LTRIM(RTRIM(sed.[Ancho de banda])))) - 1
                    )
                )

            WHEN LOWER(LTRIM(RTRIM(sed.[Ancho de banda]))) LIKE '%kbps%'
                THEN TRY_CONVERT(
                    DECIMAL(18,4),
                    LEFT(
                        LOWER(LTRIM(RTRIM(sed.[Ancho de banda]))),
                        CHARINDEX('kbps', LOWER(LTRIM(RTRIM(sed.[Ancho de banda])))) - 1
                    )
                ) / 1000

            ELSE TRY_CONVERT(
                DECIMAL(18,4),
                LTRIM(RTRIM(sed.[Ancho de banda]))
            )
        END AS [Ancho de banda (Nro)],
        sed.Departamento,
        sed.Municipio,
        sed.DANE_Mpio,
        sed.Longitud,
        sed.Latitud,
        sed.[Direccion Sede] AS Direccion,
        sed.[Viabilidad Positiva],
        sed.[Distancia Total Viabilidad],
        sed.[Total por un punto (USD) Viabilidad]
    FROM SFDC.DM_PRICING_SEDE sed
    INNER JOIN Funnels f
        ON sed.[Consecutivo de Sede] = f.SEDE
    WHERE 
        (
            sed.Producto NOT IN ('IP PÚBLICA')
            OR sed.Producto IS NULL
        )
        AND
        (
            sed.Familia_Producto_Sede IN ('Datos', 'Internet')
            OR sed.Familia_Producto_Sede IS NULL
        )
)
INSERT INTO #LocationTrackerBase
(
    [Consecutivo de Sede],
    Funnel,
    FechaCreacion,
    ESTADO_FUNNEL,
    NOMBRE_COMERCIAL_FUNNEL,
    NIT,
    Vendedor,
    Familia_Producto_Sede,
    Producto,
    [Plan],
    [Ancho de banda (Nro)],
    Departamento,
    Municipio,
    DANE_Mpio,
    Longitud,
    Latitud,
    [Direccion],
    [Viabilidad Positiva],
    [Distancia Total Viabilidad],
    [Total por un punto (USD) Viabilidad]
)
SELECT
    [Consecutivo de Sede],
    Funnel,
    FechaCreacion,
    ESTADO_FUNNEL,
    NOMBRE_COMERCIAL_FUNNEL,
    NIT,
    Vendedor,
    Familia_Producto_Sede,
    Producto,
    [Plan],
    [Ancho de banda (Nro)],
    Departamento,
    Municipio,
    DANE_Mpio,
    Longitud,
    Latitud,
    [Direccion],
    [Viabilidad Positiva],
    [Distancia Total Viabilidad],
    [Total por un punto (USD) Viabilidad]
FROM Sedes;
"""

QUERY_LOCATIONS_TRACKER_MEASURES_V1 = """
SELECT
    COUNT(*) AS Total_Sedes,
    SUM(
        CASE
            WHEN [Total por un punto (USD) Viabilidad] <> 0
            THEN 1
            ELSE 0
        END
    ) AS Sedes_Viables,
    SUM(
        CASE
            WHEN [Total por un punto (USD) Viabilidad] = 0
              OR [Total por un punto (USD) Viabilidad] IS NULL
            THEN 1
            ELSE 0
        END
    ) AS Sedes_No_Viables,
    CAST(
        100.0 * SUM(
            CASE
                WHEN [Total por un punto (USD) Viabilidad] <> 0
                THEN 1
                ELSE 0
            END
        ) / NULLIF(COUNT(*), 0)
        AS DECIMAL(6,2)
    ) AS Razon_Viabilidad_Pct,
    SUM(
        CASE
            WHEN [Total por un punto (USD) Viabilidad] <> 0
             AND Longitud IS NOT NULL
             AND Latitud IS NOT NULL
             AND Longitud <> 0
             AND Latitud <> 0
            THEN 1
            ELSE 0
        END
    ) AS Sedes_Viables_Con_Coordenadas,
    CAST(
        100.0 * SUM(
            CASE
                WHEN [Total por un punto (USD) Viabilidad] <> 0
                 AND Longitud IS NOT NULL
                 AND Latitud IS NOT NULL
                 AND Longitud <> 0
                 AND Latitud <> 0
                THEN 1
                ELSE 0
            END
        ) / NULLIF(
            SUM(
                CASE
                    WHEN [Total por un punto (USD) Viabilidad] <> 0
                    THEN 1
                    ELSE 0
                END
            ), 0
        )
        AS DECIMAL(6,2)
    ) AS Razon_Viables_Con_Coordenadas_Pct
FROM #LocationTrackerBase;
"""

QUERY_LOCATIONS_TRACKER_SED_COORDINATES_V1 = """
SELECT *
FROM #LocationTrackerBase
WHERE [Total por un punto (USD) Viabilidad] <> 0
  AND [Total por un punto (USD) Viabilidad] IS NOT NULL
  AND Longitud <> 0
  AND Latitud <> 0
  AND Longitud IS NOT NULL
  AND Latitud IS NOT NULL;
"""

QUERY_LOCATIONS_TRACKER_NO_COORDINATES_V1 = """
SELECT *
FROM #LocationTrackerBase
WHERE [Total por un punto (USD) Viabilidad] <> 0
  AND [Total por un punto (USD) Viabilidad] IS NOT NULL
  AND (
      Longitud IS NULL
      OR Latitud IS NULL
      OR Longitud = 0
      OR Latitud = 0
  );
"""

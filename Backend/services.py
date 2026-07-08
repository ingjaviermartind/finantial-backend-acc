from . import models
from django.db.models import Max
from django.db import transaction

import pyodbc
import pandas as pd

def calculate_costs(capacity, time, sensitivity = 1.65):
    # Opex
    ethernet_output = (models.FinancialVariable.objects.get(key='TRM').value or 0)
    ethernet_output *= (models.FinancialVariable.objects.get(key='ETH_OUT').value or 0)
    ethernet_output *= capacity
    costo_oym = (models.Department.objects.aggregate(Max('avg_rate_pf'))['avg_rate_pf__max'] or 0)
    renta_postes = (models.FinancialVariable.objects.get(key='POSTERIA').value or 0)
    renta_ducto = (models.FinancialVariable.objects.get(key='TRM').value or 0)
    renta_ducto *= (models.FinancialVariable.objects.get(key='DUCT_RENTAL').value or 0)
    call_atencion = (models.FinancialVariable.objects.get(key='CALL').value or 0)
    comision_recaudo = (models.FinancialVariable.objects.get(key='COLL_COMM').value or 0)
    distribucion = (models.FinancialVariable.objects.get(key='DIS').value or 0)
    total_opex = ethernet_output + costo_oym + renta_postes + renta_ducto + call_atencion + comision_recaudo + distribucion
    # Capex
    capex_red = (models.FinancialVariable.objects.get(key='TRM').value or 0)
    capex_red *= (models.FinancialVariable.objects.get(key='WEB_CAPEX').value or 0)
    capex_red *= capacity
    capex_red *= time
    # total
    total_opex_capex = ( (total_opex*time) + capex_red ) / time
    monthly_price = total_opex_capex
    monthly_price *= (models.FinancialVariable.objects.get(key='MARG') or 0)
    monthly_price *= sensitivity
    calculated_sensitivity = 1 if capacity == 0 else monthly_price/capacity

def calculate_financials(price, user, data):
    with transaction.atomic():
        last_version = price.versions.filter(
            horizon=data["horizon"]
        ).first()
        version_number = (last_version.version_number + 1) if last_version else 1
        price.versions.filter(
            is_current=True,
            horizon=data["horizon"]
        ).update(is_current=False)
        version = models.PriceVersion.objects.create(
            price=price,
            horizon=data['horizon'],
            payment_type=data['payment_type'],
            version_number=version_number,
            is_current=True,
            created_by=user
        )
        inputs = models.FinancialInputs.objects.create(
            version=version,
            inicial_income=data.get('inicial_income', 0) or 0,
            # horizon=data['horizon'],
            capex=data['capex'],
            opex=data['opex'],
            wacc=data['wacc'],
            factor=data['factor'],
            sensitivity=data.get('sensitivity', 1.0),
            # payment_type=data['payment_type'],
            # payment_duration=data.get('payment_duration')
        )
        
        price_monthly = ((inputs.capex + inputs.opex) / version.horizon) * inputs.sensitivity * inputs.factor
        
        vpn = 0
        income_vpn = 0
        payback = None
        ebitda_t = 0
        fcl_km1 = 0
        total_income = 0
        monthly_wacc = inputs.wacc/version.horizon

        for t in range (0, version.horizon + 1):
            if version.payment_type == "one time":
                income = price_monthly if t == 1 else inputs.inicial_income if inputs.inicial_income != 0 else 0
            else:
                duration = version.horizon
                income = price_monthly if t <= duration and t != 0 else inputs.inicial_income if inputs.inicial_income != 0 else 0
            
            capex = inputs.capex if t == 0 else 0
            monthly_opex = inputs.opex / version.horizon if t > 0 else 0
            ebitda = income - monthly_opex if t > 0 else 0
            fcl = ebitda - capex if t == 0 else fcl_km1 + ebitda
            discount_factor = ((1 + monthly_wacc) ** t)
            fcl_discounted = fcl / discount_factor
            i_vpn = income / discount_factor

            models.CashFlow.objects.create(
                version=version,
                period=t,
                income=income,
                opex=monthly_opex,
                ebitda=ebitda,
                capex=capex,
                fcl=fcl,
                discount_factor=discount_factor,
                fcl_discounted=fcl_discounted
            )

            fcl_km1 = fcl
            vpn += fcl_discounted
            income_vpn += i_vpn
            total_income += income

            if fcl > 0 and payback is None:
                payback = t

            ebitda_t += ebitda
        
        contribution = (ebitda_t / (version.horizon * price_monthly)) if price_monthly else 0
        net_margin = vpn / income_vpn
        models.FinancialResults.objects.create(
            version=version,
            vpn=vpn,
            income_vpn=income_vpn,
            payback=payback or 0,
            contribution_percent=contribution,
            ebitda_total=ebitda_t,
            net_margin=net_margin,
            price=price_monthly
    )
        return version



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

@staticmethod
def get_services_by_municipality(key, min_cap = 100):
    municipality = models.Municipality.objects.get(id=key)
    conn = pyodbc.connect(
        r"DRIVER={ODBC Driver 17 for SQL Server};"
        r"SERVER=10.142.16.246\accdwh;"
        r"DATABASE=Azteca_Staging;"
        r"Trusted_Connection=yes;"
    )
    try:
        df_active_services = pd.read_sql(
            QUERY_ACTIVE_SERVICES, 
            conn,
            params=[min_cap,municipality.dane]
        )
    finally:
        conn.close()
    return df_active_services.to_dict(orient="records")

#
# EOF
#
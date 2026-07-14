from Backend import models
from django.db import transaction

import pyodbc
import pandas as pd



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

#
# EOF
#
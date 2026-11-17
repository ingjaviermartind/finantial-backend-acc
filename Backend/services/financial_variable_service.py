from Backend.dtos import FinancialVariables
from Backend import models

class FinancialVariableService:

    @staticmethod
    def get_variables(area) -> FinancialVariables:
        variables = {
            item.key: float(item.value)
            for item in models.FinancialVariable.objects.filter(
                area=area
            )
        }

        return FinancialVariables(
            trm=variables["TRM"],
            eth_output_mbps=variables["ETH_OUT"],
            oym=variables["OYM_COST"],
            poles=variables["POSTERIA"],
            ducts=variables["DUCT_RENTAL"],
            call_center=variables["CALL"],
            distribution=variables["DIS"],
            collection=variables["COLL_COMM"],
            web_capex=variables["WEB_CAPEX"],
            margin_factor=variables["MARG"],
            gmf=variables["_4x1000"] / 100,
            fontic=variables["FONTIC"] / 100,
            ica=variables["ICA"] / 100,
            cartera=variables["PORTF"],
            monthly_wacc=variables["WACC_M"] / 100,
            wacc=variables["WACC_A"] / 100,
            min_vpn=variables['VPN_MIN'],
            min_margin=variables['MARGIN_MIN'] / 100,
            max_payback=variables['PAYBACK_MAX_RATIO'] / 100
        )
# VPN_MIN MARGIN_MIN PAYBACK_MAX_RATIO
    @staticmethod
    def update_variable(key: str, value: float, area):
        variable = models.FinancialVariable.objects.get(
            key=key,
            area=area
        )

        variable.value = value
        variable.save(update_fields=["value", "updated_at"])

        return variable

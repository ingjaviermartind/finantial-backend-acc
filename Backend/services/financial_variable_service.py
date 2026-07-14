from Backend.dtos.FinancialVariables import FinancialVariables
from Backend import models

class FinancialVariableService():
    @staticmethod
    def get_variables() -> FinancialVariables:
        variables = {
            item.key: float(item.value)
            for item in models.FinancialVariable.objects.all()
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
            gmf=variables["_4x1000"]/100,
            fontic=variables["FONTIC"]/100,
            ica=variables["ICA"]/100,
            cartera=variables["PORTF"],
            monthly_wacc=variables["WACC_M"]/100
        )
    @staticmethod
    def update_variable(key: str, value: float):
        variable = models.FinancialVariable.objects.get(
            key=key
        )
        variable.value = value
        variable.save()
        return variable
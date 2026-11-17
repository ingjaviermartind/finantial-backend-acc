from Backend.dtos import Project, PricingRecommendation, MarketReference


from Backend.services.ml_services import predict_vlr_mbps_nw
from Backend.services.active_ser_service import get_services_reference_by_municipality
from Backend.services.financial_variable_service import FinancialVariableService
from Backend.services.optimize_service import PricingOptimizer
from Backend.services.financial_engine import financial_engine
from Backend.services.reference_price_service import get_ref_price
from Backend import models

import logging


logger = logging.getLogger(__name__)


class PricingService:

    CAPACITY_GROUPS = [
        (2, 15),
        (16, 74),
        (75, 349),
        (350, 1199),
        (1200, 2999),
        (3000, 10000000)
    ]


    @staticmethod
    def get_capacity_group(capacity):
        for minimo, maximo in PricingService.CAPACITY_GROUPS:
            if minimo <= capacity <= maximo:
                return minimo, maximo
        if capacity > PricingService.CAPACITY_GROUPS[-1][1]:
            return PricingService.CAPACITY_GROUPS[-1]
        return PricingService.CAPACITY_GROUPS[0]

    @staticmethod
    def evaluate(municipality_id, prj : Project, area : str) -> PricingRecommendation:
        municipality = models.Municipality.objects.select_related("department").get(id=municipality_id)
        vars_ev = FinancialVariableService.get_variables(area)
        logger.info(
            "Factor de margen (MARG): %s | Área: %s",
            vars_ev.margin_factor,
            area
        )
        predicted_price_mpbs = predict_vlr_mbps_nw(prj.capacity_mbps, municipality, prj.contract_time, prj.product_type, prj.product, prj.subsegment)
        predicted_result = financial_engine.evaluate_price_per_mbps(prj,vars_ev,predicted_price_mpbs)
        floor_result = PricingOptimizer.find_floor(prj,vars_ev)
        min_cap, max_cap = PricingService.get_capacity_group(prj.capacity_mbps)
        market : MarketReference = get_services_reference_by_municipality(
            municipality, 
            min_cap, 
            max_cap,
            prj.subsegment,
            prj.product
        )
        reference_price = get_ref_price(
            municipality,
            prj.capacity_mbps,
            prj.subsegment
        ) 
        return PricingRecommendation(
            suggested=predicted_result if predicted_result.approved else floor_result,
            floor=floor_result,
            predicted=predicted_result,
            mean_price_mbps=market.mean_price_mbps,
            median_price_mbps=market.median_price_mbps,
            market_std=market.std_price_mbps,
            market_sample=market.sample_size,
            market_source=market.source,
            monthly_wacc=vars_ev.monthly_wacc,
            wacc=vars_ev.wacc,
            ref_price_mbps=reference_price.get("BASE"),
            ref_price_mbps_dis=reference_price.get("DISCOUNT"),
            ref_price_mbps_special=reference_price.get("SPECIAL"),
        )

    @staticmethod
    def evaluate_price(prj: Project, vlr_mbps, area : str):
        vars_price = FinancialVariableService.get_variables(area)
        logger.info(
            "Factor de margen (MARG): %s | Área: %s",
            vars_price.margin_factor,
            area
        )
        result = financial_engine.evaluate_price_per_mbps(prj, vars_price, vlr_mbps)
        return result

        
        
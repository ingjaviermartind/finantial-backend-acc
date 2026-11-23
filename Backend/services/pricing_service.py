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
    def build_price_comparison(
        floor_price,
        ml_price=None,
        suggested_price=None,
        evaluated_price=None,
        market=None,
        reference_price=None
    ):
        reference_price = reference_price or {}

        return {
            "breakeven": floor_price,
            "ml_price": ml_price,
            "suggested_price": suggested_price,
            "sample_size": market.sample_size,
            "source": market.source,
            "market_average": market.mean_price_mbps if market else None,
            "market_median": market.median_price_mbps if market else None,
            "tariff_base": reference_price.get("BASE"),
            "tariff_discount": reference_price.get("DISCOUNT"),
            "tariff_special": reference_price.get("SPECIAL"),
        }

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
        suggested = (predicted_result if predicted_result.approved else floor_result)
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
            # prj.subsegment
        ) 
        price_comparison = PricingService.build_price_comparison(
            floor_price=floor_result.price_per_mbps,
            ml_price=predicted_result.price_per_mbps,
            suggested_price=suggested.price_per_mbps,
            market=market,
            reference_price=reference_price
        )
        return PricingRecommendation(
            suggested=predicted_result if predicted_result.approved else floor_result,
            floor=floor_result,
            predicted=predicted_result,
            price_comparison=price_comparison,
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

        
        
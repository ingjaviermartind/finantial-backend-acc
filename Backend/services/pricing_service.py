from Backend.dtos import Project, PricingRecommendation, MarketReference


from Backend.services.ml_services import predict_vlr_mbps
from Backend.services.active_ser_service import get_services_reference_by_municipality
from Backend.services.financial_variable_service import FinancialVariableService
from Backend.services.optimize_service import PricingOptimizer
from Backend.services.financial_engine import financial_engine
from Backend.services.reference_price_service import get_ref_price
from Backend import models
from Backend.utils import to_decimal
import logging

from Backend.utils import ZERO, to_decimal

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
    def get_price_per_mbps(result, project):
        if project.capacity_mbps <= ZERO:
            return ZERO
        return result.monthly_income / project.capacity_mbps

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
        market=None,
        reference_price=None
    ):
        reference_price = reference_price or {}

        return {
            "breakeven": floor_price,
            "ml_price": ml_price,
            "sample_size": market.sample_size if market else None,
            "source": market.source if market else None,
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
        predicted_price_mbps = to_decimal(
            predict_vlr_mbps(
                prj.capacity_mbps,
                municipality,
                prj.contract_time,
                prj.product_type,
                prj.product,
                prj.subsegment
            )
        )
        predicted_monthly_income = ( to_decimal(predicted_price_mbps) * to_decimal(prj.capacity_mbps))
        predicted_result = financial_engine.evaluate_project(
            prj,
            vars_ev,
            monthly_income=predicted_monthly_income
        )
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
        floor_price = PricingService.get_price_per_mbps(
            floor_result,
            prj
        )
        ml_price = PricingService.get_price_per_mbps(
            predicted_result,
            prj
        )
        price_comparison = PricingService.build_price_comparison(
            floor_price=floor_price,
            ml_price=ml_price,
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
        monthly_income = (
            to_decimal(vlr_mbps)
            * to_decimal(prj.capacity_mbps)
        )
        return financial_engine.evaluate_project(
            prj,
            vars_price,
            monthly_income=monthly_income
        )

        
        
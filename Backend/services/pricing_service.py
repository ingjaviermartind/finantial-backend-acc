from Backend.dtos.Project import Project
from Backend.dtos.PricingRecommendation import PricingRecommendation
from Backend.dtos.MarketReference import MarketReference
from Backend.services.ml_services import predict_vlr_mbps
from Backend.services.active_ser_service import get_services_reference_by_municipality
from Backend.services.financial_variable_service import FinancialVariableService
from Backend.services.optimize_service import PricingOptimizer
from Backend.services.financial_engine import financial_engine
from Backend.services.reference_price_service import get_reference_price
from Backend import models

class PricingService:
    @staticmethod
    def evaluate(
        municipality_id, 
        prj : Project
    ) -> PricingRecommendation:
        municipality = models.Municipality.objects.select_related(
            "department"
        ).get(id=municipality_id)

        vars = FinancialVariableService.get_variables()
        predicted_price_mpbs = predict_vlr_mbps(prj.capacity_mbps, municipality)
        predicted_result = financial_engine.evaluate_price_per_mbps(prj,vars,predicted_price_mpbs)
        floor_result = PricingOptimizer.find_floor(prj,vars)
        market : MarketReference = (get_services_reference_by_municipality(municipality))
        reference_price = get_reference_price(
            municipality.region,
            prj.capacity_mbps
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
            reference_price_mbps=reference_price
        )


        
        
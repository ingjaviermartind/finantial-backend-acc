from sqlalchemy import text, bindparam

from Backend.sql.database import engine
from Backend.sql import pricing_site_queries

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

import time
import io
import pandas as pd

class PricingSiteService:

    @staticmethod
    def get_priced_sites(filters):
        fecha_inicio = PricingSiteService._get_start_date(filters)
        offset = (filters.page - 1) * filters.page_size
        params = {
            "fecha_inicio": fecha_inicio,
            'capacity_min': filters.capacity_min,
            'capacity_max': filters.capacity_max,

            'filter_funnel': 1 if filters.funnels else 0,
            'funnels': filters.funnels,

            'filter_funnel_status': 1 if filters.funnel_statuses else 0,
            'funnel_statuses': filters.funnel_statuses,

            'filter_department' : 1 if filters.departments else 0,
            'departments' : filters.departments,

            'filter_municipality' : 1 if filters.municipalities else 0,
            'municipalities' : filters.municipalities,

            'filter_dane' : 1 if filters.danes else 0,
            'danes' : filters.danes,

            'filter_product' : 1 if filters.products else 0,
            'products' : filters.products,

            'filter_plan' : 1 if filters.plans else 0,
            'plans' : filters.plans,

            'filter_product_family' : 1 if filters.product_families else 0,
            'product_families' : filters.product_families,

            'filter_client': 1 if filters.clients else 0,
            'clients' : filters.clients,

            'offset' : offset,
            'page_size' : filters.page_size
        }
        expanding_params = [
            "funnels",
            "funnel_statuses",
            "departments",
            "municipalities",
            "danes",
            "products",
            "plans",
            "product_families",
            "clients",
        ]
        query_create = text(
        pricing_site_queries.QUERY_PRICED_SITES_CREATE_BASE
        )
        query_insert = text(
            pricing_site_queries.QUERY_PRICED_SITES_INSERT_BASE_V2
        ).bindparams(
            *[
                bindparam(param, expanding=True)
                for param in expanding_params
            ]
        )
        query_measures = text(
            pricing_site_queries.QUERY_PRICED_SITES_MEASURES
        )

        query_pagination = text(
            pricing_site_queries.QUERY_PRICED_SITES_PAGINATION
        )

        with engine.connect() as connection:
            total_start = time.perf_counter()
            start = time.perf_counter()
            connection.execute(query_create)
            # print(
            #     f"[PRICING SITES] CREATE: "
            #     f"{time.perf_counter() - start:.3f} s"
            # )
            start = time.perf_counter()
            connection.execute(
                query_insert,
                params
            )
            # print(
            #     f"[PRICING SITES] INSERT BASE: "
            #     f"{time.perf_counter() - start:.3f} s"
            # )
            start = time.perf_counter()
            measures_result = connection.execute(
                query_measures
            )
            # print(
            #     f"[PRICING SITES] MEASURES EXECUTE: "
            #     f"{time.perf_counter() - start:.3f} s"
            # )
            start = time.perf_counter()
            measures_row = measures_result.mappings().one()
            # print(
            #     f"[PRICING SITES] MEASURES FETCH: "
            #     f"{time.perf_counter() - start:.3f} s"
            # )
            total_funnel_count = measures_row["TOTAL_FUNNELS"]
            total_sede_count = measures_row["TOTAL_SEDES"]
            total_mrc = measures_row["TOTAL_MRC"]
            start = time.perf_counter()
            result = connection.execute(
                query_pagination,
                {
                    "offset": offset,
                    "page_size": filters.page_size,
                }
            )
            # print(
            #     f"[PRICING SITES] PAGINATION EXECUTE: "
            #     f"{time.perf_counter() - start:.3f} s"
            # )
            start = time.perf_counter()
            rows = result.mappings().all()
            # print(
            #     f"[PRICING SITES] ROWS FETCHED: {len(rows)}"
            # )
            # print(
            #     f"[PRICING SITES] PAGINATION FETCH: "
            #     f"{time.perf_counter() - start:.3f} s"
            # )
            start = time.perf_counter()
            results = [
                dict(row)
                for row in rows
            ]
            # print(
            #     f"[PRICING SITES] RESULTS BUILD: "
            #     f"{time.perf_counter() - start:.3f} s"
            # )
            # print(
            #     f"[PRICING SITES] TOTAL SERVICE SQL/BACKEND: "
            #     f"{time.perf_counter() - total_start:.3f} s"
            # )
            return {
                "funnel count": total_funnel_count,
                "sedes count": total_sede_count,
                "mrc total": total_mrc,
                "page": filters.page,
                "page_size": filters.page_size,
                "total_pages": (
                    (total_funnel_count + filters.page_size - 1)
                    // filters.page_size
                ),
                "results": results,
            }


    @staticmethod
    def export_priced_sites(filters):
        fecha_inicio = PricingSiteService._get_start_date(filters)
        params = {
            "fecha_inicio": fecha_inicio,
            'capacity_min': filters.capacity_min,
            'capacity_max': filters.capacity_max,

            'filter_funnel': 1 if filters.funnels else 0,
            'funnels': filters.funnels,

            'filter_funnel_status': 1 if filters.funnel_statuses else 0,
            'funnel_statuses': filters.funnel_statuses,

            'filter_department' : 1 if filters.departments else 0,
            'departments' : filters.departments,

            'filter_municipality' : 1 if filters.municipalities else 0,
            'municipalities' : filters.municipalities,

            'filter_dane' : 1 if filters.danes else 0,
            'danes' : filters.danes,

            'filter_product' : 1 if filters.products else 0,
            'products' : filters.products,

            'filter_plan' : 1 if filters.plans else 0,
            'plans' : filters.plans,

            'filter_product_family' : 1 if filters.product_families else 0,
            'product_families' : filters.product_families,

            'filter_client': 1 if filters.clients else 0,
            'clients' : filters.clients,
        }
        expanding_params = [
            "funnels",
            "funnel_statuses",
            "departments",
            "municipalities",
            "danes",
            "products",
            "plans",
            "product_families",
            "clients",
        ]
        query_create = text(
        pricing_site_queries.QUERY_PRICED_SITES_CREATE_BASE
        )
        query_insert = text(
            pricing_site_queries.QUERY_PRICED_SITES_INSERT_BASE_V2
        ).bindparams(
            *[
                bindparam(param, expanding=True)
                for param in expanding_params
            ]
        )
        total_start = time.perf_counter()
        with engine.connect() as connection:
            start = time.perf_counter()
            connection.execute(query_create)
            # print(
            #     f"[PRICING SITES] CREATE: "
            #     f"{time.perf_counter() - start:.3f} s"
            # )
            start = time.perf_counter()
            connection.execute(
                query_insert,
                params
            )
            # print(
            #     f"[PRICING SITES] INSERT BASE: "
            #     f"{time.perf_counter() - start:.3f} s"
            # )
            start = time.perf_counter()
            result = connection.execute(
                text(pricing_site_queries.QUERY_PRICED_SITES_EXPORT)
            )
            # print(
            #     f"[PRICING SITES] SELECT FROM BASE: "
            #     f"{time.perf_counter() - start:.3f} s"
            # )
            rows = result.mappings().all()
        start = time.perf_counter()
        df = pd.DataFrame(rows)
        # print(
        #     f"[PRICING SITES] CONVERT TO DATAFRAME: "
        #     f"{time.perf_counter() - start:.3f} s"
        # )
        start = time.perf_counter()
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(
                writer,
                index=False,
                sheet_name="Sedes"
            )
        # print(
        #     f"[PRICING SITES] CONVERT TO EXCEL: "
        #     f"{time.perf_counter() - start:.3f} s"
        # )
        output.seek(0)
        # print(
        #     f"[PRICING SITES] TOTAL SERVICE SQL/BACKEND: "
        #     f"{time.perf_counter() - total_start:.3f} s"
        # )
        return output

    @staticmethod
    def get_filter_options(filters):
        fecha_inicio = PricingSiteService._get_start_date(filters)
        params = {
            "fecha_inicio": fecha_inicio,
            "capacity_min": filters.capacity_min,
            "capacity_max": filters.capacity_max,
            "filter_client": 1 if filters.clients else 0,
            "clients": filters.clients,
            "filter_funnel_status": 1 if filters.funnel_statuses else 0,
            "funnel_statuses": filters.funnel_statuses,
            "filter_department": 1 if filters.departments else 0,
            "departments": filters.departments,
            "filter_municipality": 1 if filters.municipalities else 0,
            "municipalities": filters.municipalities,
            "filter_dane": 1 if filters.danes else 0,
            "danes": filters.danes,
            "filter_product": 1 if filters.products else 0,
            "products": filters.products,
            "filter_plan": 1 if filters.plans else 0,
            "plans": filters.plans,
            "filter_product_family": 1 if filters.product_families else 0,
            "product_families": filters.product_families,
        }
        expanding_params = [
            "clients",
            "funnel_statuses",
            "departments",
            "municipalities",
            "danes",
            "products",
            "plans",
            "product_families",
        ]
        create_query = text(pricing_site_queries.QUERY_FILTER_OPTIONS_CREATE_BASE)
        # Query INSERT sí tiene parámetros
        insert_query = text(
            pricing_site_queries.QUERY_FILTER_OPTIONS_INSERT_BASE
        ).bindparams(
            *[
                bindparam(param, expanding=True)
                for param in expanding_params
            ]
        )

        with engine.connect() as connection:
            # 1. Crear tabla temporal
            connection.execute(create_query)
            # 2. Poblarla con los filtros
            connection.execute(
                insert_query,
                params
            )
            summary_rows = connection.execute(
                text(pricing_site_queries.QUERY_FILTER_OPTIONS_SUMMARY)
            ).mappings().all()
            client_rows = connection.execute(
                text(pricing_site_queries.QUERY_FILTER_OPTIONS_CLIENTS)
            ).mappings().all()
            status_rows = connection.execute(
                text(pricing_site_queries.QUERY_FILTER_OPTIONS_STATUSES)
            ).mappings().all()
            location_rows = connection.execute(
                text(pricing_site_queries.QUERY_FILTER_OPTIONS_LOCATIONS)
            ).mappings().all()
            product_rows = connection.execute(
                text(pricing_site_queries.QUERY_FILTER_OPTIONS_PRODUCTS)
            ).mappings().all()
            funnel_rows = connection.execute(
                text(pricing_site_queries.QUERY_FILTER_OPTIONS_FUNNELS)
            ).mappings().all()
        total_sites = (
            summary_rows[0]["TOTAL_SEDES"]
            if summary_rows
            else 0
        )
        clients = {}
        for row in client_rows:
            nit = row["NIT"]
            business_name = row["BUSINESS_NAME"]
            if nit not in clients:
                clients[nit] = set()
            if business_name is not None:
                clients[nit].add(business_name)
        client_result = [
            {
                "nit": nit,
                "business_names": sorted(business_names)
            }
            for nit, business_names in clients.items()
        ]
        funnels = [
            row['FUNNEL']
            for row in funnel_rows
        ]
        funnel_statuses = [
            row["STATUS"]
            for row in status_rows
        ]
        locations = {}
        for row in location_rows:
            department = row["DEPARTMENT"]
            municipality = row["MUNICIPALITY"]
            dane = row["DANE"]
            if department not in locations:
                locations[department] = {}
            if municipality not in locations[department]:
                locations[department][municipality] = set()
            if dane is not None:
                locations[department][municipality].add(
                    str(dane)
                )
        location_result = []
        for department, municipalities in locations.items():
            municipality_result = []
            for municipality, danes in municipalities.items():
                municipality_result.append({
                    "municipality": municipality,
                    "danes": sorted(danes)
                })
            location_result.append({
                "department": department,
                "municipalities": municipality_result
            })
        products = {}
        for row in product_rows:
            family = row["FAMILY"]
            product = row["PRODUCT"]
            plan = row["PLAN"]
            if family not in products:
                products[family] = {}
            if product not in products[family]:
                products[family][product] = set()
            if plan is not None:
                products[family][product].add(plan)
        product_result = []
        for family, product_map in products.items():
            product_list = []
            for product, plans in product_map.items():
                product_list.append({
                    "product": product,
                    "plans": sorted(plans)
                })
            product_result.append({
                "family": family,
                "products": product_list
            })
        return {
            "total_sites": total_sites,
            "clients": client_result,
            'funnels': funnels,
            "funnel_statuses": funnel_statuses,
            "locations": location_result,
            "products": product_result,
        }
    
    @staticmethod
    def _get_start_date(filters):
        if filters.period_value is None:
            return None
        today = date.today()
        if filters.period_unit == "día(s)":
            return today - timedelta(days=filters.period_value)
        if filters.period_unit == "semana(s)":
            return today - timedelta(weeks=filters.period_value)
        if filters.period_unit == "mes(es)":
            return today - relativedelta(months=filters.period_value)
        if filters.period_unit == "trimestre(s)":
            return today - relativedelta(
                months=filters.period_value * 3
            )
        if filters.period_unit == "año(s)":
            return today - relativedelta(
                years=filters.period_value
            )
        return None

from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import text
from sqlalchemy.engine import Engine

from Backend.sql import ser_queries, sed_queries
from Backend.sql.database import engine 

from math import isfinite, radians
from sklearn.neighbors import BallTree


class FunnelTrackerService:

    EARTH_RADIUS_M = 6_371_008.8
    MATCH_RADIUS_M = 100.0

    @staticmethod
    def _execute_tracker_queries(engine: Engine,table_name: str,create_query: str,insert_query: str, measures_query: str, coordinates_query: str) -> dict:
        drop_query = text(
            f"""
            IF OBJECT_ID('tempdb..{table_name}') IS NOT NULL
                DROP TABLE {table_name};
            """
        )
        with engine.connect() as connection:
            try:
                # Limpiar posibles restos de una sesión reutilizada.
                connection.execute(drop_query)
                # Construir el universo una sola vez.
                connection.execute(text(create_query))
                connection.execute(text(insert_query))
                # Consultar métricas.
                measures = (
                    connection.execute(text(measures_query))
                    .mappings()
                    .one()
                )
                # Recuperar registros para el cruce geográfico.
                coordinates = (
                    connection.execute(text(coordinates_query))
                    .mappings()
                    .all()
                )
                # Eliminar la temporal antes de devolver la conexión al pool.
                connection.execute(drop_query)
                connection.commit()
                return {
                    "metrics": dict(measures),
                    "coordinates": [
                        dict(row) for row in coordinates
                    ],
                    "coordinates_count": len(coordinates),
                }
            except Exception:
                connection.rollback()
                # Si falló la operación, intentar limpiar la temporal.
                try:
                    connection.execute(drop_query)
                    connection.commit()
                except Exception:
                    connection.rollback()
                raise

    @staticmethod
    def _load_locations(engine: Engine) -> dict:
        return FunnelTrackerService._execute_tracker_queries(
            engine=engine,
            table_name="#LocationTrackerBase",
            create_query=(
                sed_queries.QUERY_LOCATIONS_TRACKER_CREATE_BASE_V1
            ),
            insert_query=(
                sed_queries.QUERY_LOCATIONS_TRACKER_INSERT_BASE_V1
            ),
            measures_query=(
                sed_queries.QUERY_LOCATIONS_TRACKER_MEASURES_V1
            ),
            coordinates_query=(
                sed_queries.QUERY_LOCATIONS_TRACKER_SED_COORDINATES_V1
            ),
        )

    @staticmethod
    def _load_services(engine: Engine) -> dict:
        return FunnelTrackerService._execute_tracker_queries(
            engine=engine,
            table_name="#ServiceTrackerBase",
            create_query=(
                ser_queries.QUERY_SERVICES_TRACKER_CREATE_BASE_V1
            ),
            insert_query=(
                ser_queries.QUERY_SERVICES_TRACKER_INSERT_BASE_V1
            ),
            measures_query=(
                ser_queries.QUERY_SERVICES_TRACKER_MEASURES_V1
            ),
            coordinates_query=(
                ser_queries.QUERY_SERVICES_TRACKER_SERVICES_WITH_COORDINATES
            ),
        )

    @staticmethod
    def get_tracker_data() -> dict:
        with ThreadPoolExecutor(max_workers=2) as executor:
            locations_future = executor.submit(
                FunnelTrackerService._load_locations,
                engine,
            )

            services_future = executor.submit(
                FunnelTrackerService._load_services,
                engine,
            )

            return {
                "locations": locations_future.result(),
                "services": services_future.result(),
            }

    @staticmethod
    def _valid_coordinate_rows(rows: list[dict]) -> list[dict]:
        valid_rows = []
        for row in rows:
            try:
                latitude = float(row["Latitud"])
                longitude = float(row["Longitud"])
            except (KeyError, TypeError, ValueError):
                continue
            if not (
                isfinite(latitude)
                and isfinite(longitude)
                and -90 <= latitude <= 90
                and -180 <= longitude <= 180
                and latitude != 0
                and longitude != 0
            ):
                continue
            valid_rows.append({
                **row,
                "_latitude": latitude,
                "_longitude": longitude,
            })
        return valid_rows

    @staticmethod
    def _find_location_matches(
        location_rows: list[dict],
        service_rows: list[dict],
        radius_m: float = 100.0,
    ) -> dict:
        locations = FunnelTrackerService._valid_coordinate_rows(location_rows)
        services = FunnelTrackerService._valid_coordinate_rows(service_rows)
        if radius_m <= 0:
            raise ValueError("El radio debe ser mayor que cero.")
        matches = []
        matched_location_ids = set()
        matched_service_ids = set()
        if not locations or not services:
            return {
                "matches": [],
                "metrics": {
                    "radius_m": radius_m,
                    "sites_checked": len(locations),
                    "services_checked": len(services),
                    "sites_with_matches": 0,
                    "sites_without_matches": len(locations),
                    "services_matched": 0,
                    "matched_pairs": 0,
                },
            }
        service_coordinates = [
            [
                radians(service["_latitude"]),
                radians(service["_longitude"]),
            ]
            for service in services
        ]
        location_coordinates = [
            [
                radians(location["_latitude"]),
                radians(location["_longitude"]),
            ]
            for location in locations
        ]
        tree = BallTree(service_coordinates, metric="haversine")
        radius_radians = (radius_m / FunnelTrackerService.EARTH_RADIUS_M)
        neighbor_indices, angular_distances = tree.query_radius(
            location_coordinates,
            r=radius_radians,
            return_distance=True,
            sort_results=True,
        )
        for location_index, location in enumerate(locations):
            nearby_indices = neighbor_indices[location_index]
            nearby_distances = angular_distances[location_index]
            for service_index, angular_distance in zip(nearby_indices,nearby_distances):
                service = services[int(service_index)]
                distance_m = (float(angular_distance) * FunnelTrackerService.EARTH_RADIUS_M)
                matched_location_ids.add(location_index)
                matched_service_ids.add(int(service_index))
                matches.append({
                    "funnel": location.get("Funnel"),
                    "site_id": location.get("Consecutivo de Sede"),
                    "site_nit": location.get("NIT"),
                    "site_status": location.get("ESTADO_FUNNEL"),
                    "commercial": location.get("NOMBRE_COMERCIAL_FUNNEL"),
                    "site_product": location.get("Producto"),
                    "site_plan": location.get("Plan"),
                    "site_capacity_mbps": (
                        float(location["Ancho de banda (Nro)"])
                        if location.get("Ancho de banda (Nro)") is not None
                        else None
                    ),
                    "site_department": location.get("Departamento"),
                    "site_municipality": location.get("Municipio"),
                    "site_dane": location.get("DANE_Mpio"),
                    "site_address": location.get("Direccion Sede"),
                    "site_latitude": location["_latitude"],
                    "site_longitude": location["_longitude"],

                    "active_service_ser": service.get("SER"),
                    "service_nit": service.get("NIT"),
                    "service_client": service.get("RAZON_SOCIAL"),
                    "service_family": service.get("FAMILIA_PRODUCTOS"),
                    "service_product": service.get("PRODUCTO"),
                    "service_plan": service.get("PLAN"),
                    "service_tariff": (
                        float(service["TARIFA"])
                        if service.get("TARIFA") is not None
                        else None
                    ),
                    "service_price_per_mbps": (
                        float(service["VLR_MBPS"])
                        if service.get("VLR_MBPS") is not None
                        else None
                    ),
                    "service_department": service.get("Departamento"),
                    "service_municipality": service.get("Municipio"),
                    "service_dane": service.get("Codigo DANE"),
                    "service_address": service.get("Direccion Servicio"),
                    "service_latitude": service["_latitude"],
                    "service_longitude": service["_longitude"],

                    "distance_m": round(distance_m, 2),
                })

        return {
            "matches": matches,
            "metrics": {
                "radius_m": radius_m,
                "sites_checked": len(locations),
                "services_checked": len(services),
                "sites_with_matches": len(matched_location_ids),
                "sites_without_matches": (
                    len(locations) - len(matched_location_ids)
                ),
                "services_matched": len(matched_service_ids),
                "matched_pairs": len(matches),
            },
        }


    @staticmethod
    def get_funnel_tracker(radius_m: float = 100.0) -> dict:
        # Consultar sedes y servicios en paralelo.
        data = FunnelTrackerService.get_tracker_data()

        # Cruzar las coordenadas obtenidas.
        proximity = FunnelTrackerService._find_location_matches(
            location_rows=data["locations"]["coordinates"],
            service_rows=data["services"]["coordinates"],
            radius_m=radius_m,
        )

        return {
            "metrics": {
                "locations": data["locations"]["metrics"],
                "services": data["services"]["metrics"],
                "proximity": proximity["metrics"],
            },
            "matches": proximity["matches"],
        }
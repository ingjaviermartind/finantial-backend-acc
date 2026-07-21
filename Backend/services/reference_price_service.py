from bisect import bisect_right

REFERENCE_PRICES = {
    50: {
        "Región1": 20700,
        "Región2": 25000,
        "Región3": 25000,
    },
    100: {
        "Región1": 11000,
        "Región2": 14300,
        "Región3": 14300,
    },
    200: {
        "Región1": 8000,
        "Región2": 9000,
        "Región3": 9000,
    },
    300: {
        "Región1": 6000,
        "Región2": 8500,
        "Región3": 8500,
    },
    400: {
        "Región1": 4800,
        "Región2": 7000,
        "Región3": 7000,
    },
    500: {
        "Región1": 4200,
        "Región2": 6000,
        "Región3": 6000,
    },
    600: {
        "Región1": 4000,
        "Región2": 5800,
        "Región3": 5800,
    },
    700: {
        "Región1": 3700,
        "Región2": 5600,
        "Región3": 5600,
    },
    800: {
        "Región1": 3400,
        "Región2": 5200,
        "Región3": 5200,
    },
    900: {
        "Región1": 3100,
        "Región2": 4800,
        "Región3": 4800,
    },
    1000: {
        "Región1": 2900,
        "Región2": 4300,
        "Región3": 4300,
    },
    2000: {
        "Región1": 2600,
        "Región2": 3900,
        "Región3": 3900,
    },
    4000: {
        "Región1": 2400,
        "Región2": 3600,
        "Región3": 3600,
    },
    5000: {
        "Región1": 2300,
        "Región2": 3500,
        "Región3": 3500,
    },
    8000: {
        "Región1": 2000,
        "Región2": 3100,
        "Región3": 3100,
    },
    10000: {
        "Región1": 1800,
        "Región2": 2700,
        "Región3": 2700,
    },
}

CAPACITIES = sorted(REFERENCE_PRICES.keys())


def get_reference_price(region: str, capacity: float) -> float:
    if region == "Por Proyecto":
        return None
    idx = bisect_right(CAPACITIES, capacity) - 1

    if idx < 0:
        idx = 0

    capacity_key = CAPACITIES[idx]
    return REFERENCE_PRICES[capacity_key][region]
from Backend.models import ReferencePrice

def get_ref_price(municipality, capacity : float, price_type='BASE') -> dict:
    region = municipality.region
    if not region:
        return {}
    if region.name == "Por proyecto":
        return {}
    
    reference_price = (
        ReferencePrice.objects
        .filter(
            region_id=municipality.region.id,
            capacity__mbps__lte=capacity
        )
        .order_by('-capacity__mbps')
        .first()
    )
    if not reference_price:
        return {}
    selected_capacity = reference_price.capacity.mbps
    prices = (
        ReferencePrice.objects
        .filter(
            region=region,
            capacity__mbps=selected_capacity
        )
        .select_related('capacity')
    )
    result = {}
    for price in prices:
        result[price.price_type] = float(price.value)

    return result
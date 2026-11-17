from Backend.models import ReferencePrice

def get_ref_price(municipality, capacity : float, subsegment : str = 'ISPs') -> dict:
    region = municipality.region
    if not region:
        return {}
    if region.name == "Por proyecto":
        return {}
    reference_price = (
        ReferencePrice.objects
        .filter(
            region_id=municipality.region.id,
            subsegment__name=subsegment,
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
            subsegment__name=subsegment,
            capacity__mbps=selected_capacity
        )
        .select_related('capacity')
    )
    result = {}
    for price in prices:
        result[price.price_type] = float(price.value)
    return result
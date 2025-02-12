

from src.crud.logistics_zones_crud import logistics_zones_crud
from src.database.models.logistics_zones import LogisticsZones
from src.database.models.pricing.location_price import LocationPrice



async def fetch_region(city: str, account_id: int):
    location = await LocationPrice.filter(city=city, account_id=account_id).first()
    if location and location.region:
        return location.region
    return ""


async def fetch_zone(city: str, account_id: int):
    region = await fetch_region(city, account_id)
    logistics_zones_objs: list[LogisticsZones] = await logistics_zones_crud.get_all(account_id)
    zone = [zone for zone in logistics_zones_objs if zone.zone_name == region]
    if zone is not None and len(zone) > 0:
        return zone[0].zone_name
    return "A"

async def fetch_region_signature(city: str, account_id: int):
    region = await fetch_region(city, account_id)
    logistics_zones_objs: list[LogisticsZones] = await logistics_zones_crud.get_all(1)

    signatures = {}
    for lz in logistics_zones_objs:
        signatures[lz.zone_name] = {
            'email': lz.email,
            'coordinator': lz.coordinator_name,
            'company': 'USA Containers',
            'support': 'Office: ' + lz.support_number,
            'direct': 'Direct: ' + lz.direct_number,
        }
    singature = signatures.get(region)
    # We are defaulting to zone "A" because for accerrories there are not region/zones
    return singature if singature is not None else signatures.get("A")


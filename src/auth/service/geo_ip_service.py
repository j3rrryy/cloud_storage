import asyncio

from geoip2.database import Reader

from protocols import GeoIPServiceProtocol


class GeoIPService(GeoIPServiceProtocol):
    def __init__(self, reader: Reader):
        self._reader = reader

    async def get_country_code(self, user_ip: str) -> str | None:
        try:
            country = await asyncio.to_thread(self._reader.country, user_ip)
            return country.country.iso_code
        except Exception:
            return None

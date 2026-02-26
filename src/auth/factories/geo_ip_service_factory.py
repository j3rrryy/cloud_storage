import asyncio
import os
from pathlib import Path

from geoip2.database import Reader

from protocols import GeoIPServiceProtocol
from service import GeoIPService


class GeoIPServiceFactory:
    def __init__(self):
        self._reader = None
        self._geo_ip_service = None

    def initialize(self) -> None:
        try:
            self._setup_geo_ip_service()
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        if self._reader is not None:
            try:
                self._reader.close()
            finally:
                self._reader = None
                self._geo_ip_service = None

    def _setup_geo_ip_service(self) -> None:
        project_root = Path(__file__).parent.parent
        path = os.path.join(project_root, "geo", "GeoLite2-Country.mmdb")
        self._reader = Reader(path)
        self._geo_ip_service = GeoIPService(self._reader)

    def get_geo_ip_service(self) -> GeoIPServiceProtocol:
        if not self._geo_ip_service:
            raise RuntimeError("GeoIPService not initialized")
        return self._geo_ip_service

    async def is_ready(self) -> bool:
        if not self._reader or not self._geo_ip_service:
            return False
        try:
            await asyncio.to_thread(self._reader.country, "8.8.8.8")
            return True
        except Exception:
            return False

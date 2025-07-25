"""Data update coordinator for Windmill Fan."""
import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL
from .blynk_service import BlynkServiceError

_LOGGER = logging.getLogger(__name__)


class WindmillDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Windmill Fan API."""

    def __init__(self, hass, blynk_service):
        """Initialize the coordinator."""
        _LOGGER.debug("Initializing Windmill Fan data coordinator")
        self.blynk_service = blynk_service
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from Windmill Fan."""
        _LOGGER.debug("Fetching data from Windmill Fan")
        
        try:
            # Fetch both power and fan speed data
            power_state = await self.blynk_service.async_get_power()
            fan_speed = await self.blynk_service.async_get_fan()
            
            data = {
                "power": power_state,
                "fan": fan_speed,
            }
            
            _LOGGER.debug(f"Successfully fetched data: {data}")
            return data
            
        except BlynkServiceError as err:
            _LOGGER.error(f"Blynk service error: {err}")
            raise UpdateFailed(f"Error communicating with Windmill device: {err}")
        except Exception as err:
            _LOGGER.error(f"Unexpected error fetching data: {err}")
            raise UpdateFailed(f"Unexpected error fetching data: {err}")

    async def async_shutdown(self):
        """Shutdown the coordinator and clean up resources."""
        _LOGGER.debug("Shutting down coordinator")
        if self.blynk_service:
            await self.blynk_service.close()
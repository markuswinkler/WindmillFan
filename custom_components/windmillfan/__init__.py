"""The Windmill Fan integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, PLATFORMS, CONF_TOKEN, BASE_URL
from .blynk_service import BlynkService, BlynkServiceError
from .coordinator import WindmillDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Windmill Fan from a config entry."""
    _LOGGER.debug("Setting up Windmill Fan config entry")

    server = BASE_URL
    token = entry.data[CONF_TOKEN]

    # Initialize the Blynk service
    blynk_service = BlynkService(hass, server, token)
    
    try:
        # Validate connection during setup
        is_valid = await blynk_service.async_validate_token()
        if not is_valid:
            await blynk_service.close()
            raise ConfigEntryNotReady("Failed to authenticate with Windmill device")
    except BlynkServiceError as err:
        await blynk_service.close()
        _LOGGER.error(f"Failed to connect to Windmill device: {err}")
        raise ConfigEntryNotReady(f"Failed to connect to Windmill device: {err}")

    # Initialize the data coordinator
    coordinator = WindmillDataUpdateCoordinator(hass, blynk_service)

    # Store the coordinator and service
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "service": blynk_service,
    }

    # Perform initial data refresh
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error(f"Failed to perform initial data refresh: {err}")
        await blynk_service.close()
        hass.data[DOMAIN].pop(entry.entry_id)
        raise ConfigEntryNotReady(f"Failed to fetch initial data: {err}")

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Windmill Fan config entry")
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Clean up coordinator and service
        entry_data = hass.data[DOMAIN].pop(entry.entry_id)
        
        # Shutdown coordinator
        coordinator = entry_data.get("coordinator")
        if coordinator:
            await coordinator.async_shutdown()
        
        # Close service session
        service = entry_data.get("service")
        if service:
            await service.close()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
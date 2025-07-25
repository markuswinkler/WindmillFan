"""Platform for Windmill Fan integration."""
import logging
from homeassistant.components.fan import FanEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import WindmillFan

_LOGGER = logging.getLogger(__name__)

ENTITY_DESCRIPTIONS = [
    FanEntityDescription(
        key="windmill_fan",
        name="Windmill Fan",
        icon="mdi:fan",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant, 
    entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Windmill Fan entities."""
    _LOGGER.debug("Setting up Windmill Fan entities")
    
    # Get the coordinator from the stored data
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Create fan entities
    entities = [
        WindmillFan(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    ]

    # Add entities to Home Assistant
    async_add_entities(entities, update_before_add=True)
    _LOGGER.debug(f"Added {len(entities)} Windmill Fan entities")
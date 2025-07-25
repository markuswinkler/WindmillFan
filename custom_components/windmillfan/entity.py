"""Windmill Fan entity implementation."""
import logging

from homeassistant.components.fan import FanEntity, FanEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

# Try to import FanEntityFeature from different locations
try:
    from homeassistant.components.fan import FanEntityFeature
except ImportError:
    try:
        from homeassistant.components.fan.const import FanEntityFeature
    except ImportError:
        # Fallback for older versions
        class FanEntityFeature:
            SET_SPEED = 1
            TURN_ON = 2
            TURN_OFF = 4
            PRESET_MODE = 8

from .const import DOMAIN, FAN_SPEED_MAPPING, DEFAULT_FAN_SPEED
from .blynk_service import BlynkServiceError

_LOGGER = logging.getLogger(__name__)


class WindmillFan(CoordinatorEntity, FanEntity):
    """Representation of a Windmill Fan device."""

    def __init__(self, coordinator, entity_description: FanEntityDescription):
        """Initialize the fan device."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_name = entity_description.name
        
        # Create unique ID safely
        token_suffix = str(coordinator.blynk_service.token)[-8:] if coordinator.blynk_service.token else "unknown"
        self._attr_unique_id = f"{DOMAIN}_{token_suffix}_{entity_description.key}"
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name="Windmill Fan",
            manufacturer="Windmill",
            model="Windmill AC",
            sw_version="1.0"
        )
        
        # Fan-specific attributes
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED |
            FanEntityFeature.TURN_ON |
            FanEntityFeature.TURN_OFF |
            FanEntityFeature.PRESET_MODE
        )
        
        # Define speed list for percentage conversion (ordered from slowest to fastest)
        self._speed_list = list(FAN_SPEED_MAPPING.keys())
        self._attr_speed_count = len(self._speed_list)
        
        # Define preset modes
        self._attr_preset_modes = list(FAN_SPEED_MAPPING.keys())
        
        _LOGGER.debug(f"Initialized WindmillFan entity: {self.entity_description.name}")
        _LOGGER.debug(f"Preset modes: {self._attr_preset_modes}")

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def is_on(self):
        """Return True if the fan is on."""
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("power", False)

    @property
    def percentage(self):
        """Return the current speed percentage."""
        if not self.is_on or not self.coordinator.data:
            return 0
        
        current_speed = self.coordinator.data.get("fan")
        if current_speed and current_speed in self._speed_list:
            return ordered_list_item_to_percentage(self._speed_list, current_speed)
        return 0

    @property
    def preset_mode(self):
        """Return the current preset mode."""
        if not self.is_on or not self.coordinator.data:
            return None
        return self.coordinator.data.get("fan")

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return self._attr_preset_modes

    @property
    def speed_count(self):
        """Return the number of speeds the fan supports."""
        return len(self._speed_list)

    async def async_set_preset_mode(self, preset_mode: str):
        """Set the preset mode of the fan."""
        _LOGGER.debug(f"Setting fan preset mode to: {preset_mode}")
        
        if preset_mode not in self._attr_preset_modes:
            _LOGGER.error(f"Invalid preset mode: {preset_mode}")
            return
        
        try:
            # Turn on fan if it's off
            if not self.is_on:
                await self.coordinator.blynk_service.async_set_power(True)
            
            # Set the fan speed
            await self.coordinator.blynk_service.async_set_fan(preset_mode)
            
            # Request data refresh
            await self.coordinator.async_request_refresh()
            
        except BlynkServiceError as err:
            _LOGGER.error(f"Failed to set preset mode: {err}")
            raise
        except Exception as err:
            _LOGGER.error(f"Unexpected error setting preset mode: {err}")
            raise

    async def async_set_percentage(self, percentage: int):
        """Set the speed percentage of the fan."""
        _LOGGER.debug(f"Setting fan percentage to: {percentage}")
        
        try:
            if percentage == 0:
                await self.async_turn_off()
            else:
                # Ensure fan is on first
                if not self.is_on:
                    await self.coordinator.blynk_service.async_set_power(True)
                
                # Convert percentage to speed name
                speed = percentage_to_ordered_list_item(self._speed_list, percentage)
                _LOGGER.debug(f"Converting {percentage}% to speed: {speed}")
                
                await self.coordinator.blynk_service.async_set_fan(speed)
                
            # Request data refresh
            await self.coordinator.async_request_refresh()
            
        except BlynkServiceError as err:
            _LOGGER.error(f"Failed to set fan percentage: {err}")
            raise
        except Exception as err:
            _LOGGER.error(f"Unexpected error setting fan percentage: {err}")
            raise

    async def async_turn_on(self, percentage=None, preset_mode=None, **kwargs):
        """Turn on the fan."""
        _LOGGER.debug(f"Turning on fan with percentage: {percentage}, preset_mode: {preset_mode}")
        
        try:
            # Turn on power first
            await self.coordinator.blynk_service.async_set_power(True)
            
            # Priority: preset_mode > percentage > current > default
            if preset_mode is not None:
                if preset_mode in self._attr_preset_modes:
                    await self.coordinator.blynk_service.async_set_fan(preset_mode)
                else:
                    _LOGGER.warning(f"Invalid preset mode: {preset_mode}")
                    await self.coordinator.blynk_service.async_set_fan(DEFAULT_FAN_SPEED)
            elif percentage is not None:
                speed = percentage_to_ordered_list_item(self._speed_list, percentage)
                await self.coordinator.blynk_service.async_set_fan(speed)
            else:
                # If no current speed or fan is off, set to default
                current_speed = self.coordinator.data.get("fan") if self.coordinator.data else None
                if not current_speed or current_speed not in self._speed_list:
                    await self.coordinator.blynk_service.async_set_fan(DEFAULT_FAN_SPEED)
            
            # Request data refresh
            await self.coordinator.async_request_refresh()
            
        except BlynkServiceError as err:
            _LOGGER.error(f"Failed to turn on fan: {err}")
            raise
        except Exception as err:
            _LOGGER.error(f"Unexpected error turning on fan: {err}")
            raise

    async def async_turn_off(self, **kwargs):
        """Turn off the fan."""
        _LOGGER.debug("Turning off fan")
        
        try:
            await self.coordinator.blynk_service.async_set_power(False)
            await self.coordinator.async_request_refresh()
            
        except BlynkServiceError as err:
            _LOGGER.error(f"Failed to turn off fan: {err}")
            raise
        except Exception as err:
            _LOGGER.error(f"Unexpected error turning off fan: {err}")
            raise

    async def async_update(self):
        """Update the fan entity."""
        _LOGGER.debug("Updating WindmillFan entity")
        await super().async_update()
        
        if self.coordinator.data:
            _LOGGER.debug(f"Updated power state: {self.coordinator.data.get('power')}")
            _LOGGER.debug(f"Updated fan speed: {self.coordinator.data.get('fan')}")
            _LOGGER.debug(f"Updated percentage: {self.percentage}")
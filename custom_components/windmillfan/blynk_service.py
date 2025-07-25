"""Blynk service for Windmill Fan integration."""
import logging
import asyncio
import aiohttp
from urllib.parse import urlencode
from typing import Union, Dict, Any

from .const import (
    FAN_SPEED_MAPPING,
    FAN_SPEED_REVERSE_MAPPING,
    POWER_MAPPING,
    PIN_POWER,
    PIN_FAN_SPEED,
    HTTP_TIMEOUT,
    MAX_RETRIES,
)

_LOGGER = logging.getLogger(__name__)


class BlynkServiceError(Exception):
    """Custom exception for Blynk service errors."""
    pass


class BlynkService:
    """Service to interact with Blynk API for Windmill Fan control."""

    def __init__(self, hass, server: str, token: str):
        """Initialize the Blynk service."""
        self.hass = hass
        self.server = server
        self.token = token
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=HTTP_TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def _get_request_url(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Build the request URL with parameters."""
        query = urlencode(params)
        return f"{self.server}/{endpoint}?{query}"

    async def _make_request_with_retry(self, url: str, retries: int = MAX_RETRIES) -> str:
        """Make HTTP request with retry logic."""
        session = await self._get_session()
        
        for attempt in range(retries):
            try:
                async with session.get(url) as response:
                    _LOGGER.debug(f"Request URL: {url}")
                    _LOGGER.debug(f"Response Status: {response.status}")
                    
                    if response.status == 200:
                        text = await response.text()
                        _LOGGER.debug(f"Response Text: {text}")
                        return text.strip()
                    elif response.status == 401:
                        raise BlynkServiceError("Invalid authentication token")
                    elif response.status == 400:
                        raise BlynkServiceError("Bad request - check device token and pin")
                    else:
                        raise BlynkServiceError(f"HTTP {response.status}: {await response.text()}")
                        
            except aiohttp.ClientError as e:
                _LOGGER.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    raise BlynkServiceError(f"Request failed after {retries} attempts: {e}")
                await asyncio.sleep(1)  # Wait before retry
        
        raise BlynkServiceError("Max retries exceeded")

    async def async_get_pin_value(self, pin: str) -> Union[int, str]:
        """Get the value of a specific pin."""
        _LOGGER.debug(f"Getting pin value for pin {pin}")
        
        try:
            params = {'token': self.token}
            url = self._get_request_url('external/api/get', params) + f"&{pin}"
            
            response_text = await self._make_request_with_retry(url)
            
            # Parse response
            if response_text.isdigit():
                return int(response_text)
            elif response_text.isalpha():
                return response_text
            else:
                # Try to parse as JSON array for legacy compatibility
                try:
                    import json
                    data = json.loads(response_text)
                    if isinstance(data, list) and len(data) > 0:
                        return data[0]
                    return response_text
                except (json.JSONDecodeError, IndexError):
                    return response_text
                    
        except BlynkServiceError:
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error getting pin {pin}: {e}")
            raise BlynkServiceError(f"Failed to get pin value for {pin}: {e}")

    async def async_set_pin_value(self, pin: str, value: Union[int, str]) -> str:
        """Set the value of a specific pin."""
        _LOGGER.debug(f"Setting pin value for pin {pin} to {value}")
        
        try:
            params = {'token': self.token, pin: value}
            url = self._get_request_url('external/api/update', params)
            
            response_text = await self._make_request_with_retry(url)
            return response_text
            
        except BlynkServiceError:
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error setting pin {pin}: {e}")
            raise BlynkServiceError(f"Failed to set pin value for {pin}: {e}")

    async def async_set_power(self, value: bool) -> None:
        """Set the power state of the fan."""
        _LOGGER.debug(f"Setting power to: {value}")
        pin_value = POWER_MAPPING.get(value, 0)
        _LOGGER.debug(f"Mapped power value: {pin_value}")
        await self.async_set_pin_value(PIN_POWER, pin_value)

    async def async_set_fan(self, value: str) -> None:
        """Set the fan speed."""
        _LOGGER.debug(f"Setting fan speed to: {value}")
        pin_value = FAN_SPEED_MAPPING.get(value, "3")  # Default to Medium
        _LOGGER.debug(f"Mapped fan speed {value} to pin value {pin_value}")
        await self.async_set_pin_value(PIN_FAN_SPEED, pin_value)

    async def async_get_power(self) -> bool:
        """Get the current power state."""
        try:
            pin_value = await self.async_get_pin_value(PIN_POWER)
            _LOGGER.debug(f"Pin value received for power: {pin_value} (type: {type(pin_value)})")
            return bool(pin_value == 1 or pin_value == "1")
        except Exception as e:
            _LOGGER.error(f"Error getting power state: {e}")
            raise BlynkServiceError(f"Failed to get power state: {e}")

    async def async_get_fan(self) -> str:
        """Get the current fan speed."""
        try:
            pin_value = await self.async_get_pin_value(PIN_FAN_SPEED)
            pin_value_str = str(pin_value)
            
            fan_mode = FAN_SPEED_REVERSE_MAPPING.get(pin_value_str, "Medium")
            _LOGGER.debug(f"Pin value {pin_value_str} mapped to fan mode: {fan_mode}")
            return fan_mode
            
        except Exception as e:
            _LOGGER.error(f"Error getting fan speed: {e}")
            raise BlynkServiceError(f"Failed to get fan speed: {e}")

    async def async_validate_token(self) -> bool:
        """Validate the authentication token by making a test request."""
        try:
            await self.async_get_power()
            return True
        except BlynkServiceError as e:
            _LOGGER.error(f"Token validation failed: {e}")
            return False
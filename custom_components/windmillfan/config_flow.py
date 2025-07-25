"""Config flow for Windmill Fan integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_TOKEN, BASE_URL
from .blynk_service import BlynkService, BlynkServiceError

_LOGGER = logging.getLogger(__name__)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class WindmillConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Windmill integration."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return WindmillOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                await self._test_credentials(user_input[CONF_TOKEN])
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create a unique ID based on the token (last 8 characters for privacy)
                token_suffix = user_input[CONF_TOKEN][-8:] if len(user_input[CONF_TOKEN]) >= 8 else user_input[CONF_TOKEN]
                await self.async_set_unique_id(f"windmill_fan_{token_suffix}")
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title="Windmill Fan", 
                    data=user_input
                )

        schema = vol.Schema({
            vol.Required(CONF_TOKEN): str,
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=schema, 
            errors=errors,
            description_placeholders={
                "dashboard_url": "https://dashboard.windmillair.com"
            }
        )

    async def _test_credentials(self, token: str):
        """Validate credentials."""
        if not token or len(token) < 10:  # Basic token format validation
            raise InvalidAuth
            
        try:
            # Create service and test connection
            service = BlynkService(self.hass, BASE_URL, token)
            is_valid = await service.async_validate_token()
            await service.close()
            
            if not is_valid:
                raise InvalidAuth
                
        except BlynkServiceError as e:
            _LOGGER.error(f"Authentication failed: {e}")
            if "Invalid authentication" in str(e) or "401" in str(e):
                raise InvalidAuth
            else:
                raise CannotConnect
        except Exception as e:
            _LOGGER.error(f"Connection test failed: {e}")
            raise CannotConnect


class WindmillOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Windmill options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        
        if user_input is not None:
            # Test new credentials if token changed
            if user_input[CONF_TOKEN] != self.config_entry.data.get(CONF_TOKEN):
                try:
                    service = BlynkService(self.hass, BASE_URL, user_input[CONF_TOKEN])
                    is_valid = await service.async_validate_token()
                    await service.close()
                    
                    if not is_valid:
                        errors["base"] = "invalid_auth"
                    else:
                        # Update config entry data
                        self.hass.config_entries.async_update_entry(
                            self.config_entry, data=user_input
                        )
                        return self.async_create_entry(title="", data={})
                        
                except Exception as e:
                    _LOGGER.error(f"Options validation failed: {e}")
                    errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="", data={})

        schema = vol.Schema({
            vol.Required(
                CONF_TOKEN, 
                default=self.config_entry.data.get(CONF_TOKEN)
            ): str,
        })

        return self.async_show_form(
            step_id="init", 
            data_schema=schema, 
            errors=errors,
            description_placeholders={
                "dashboard_url": "https://dashboard.windmillair.com"
            }
        )
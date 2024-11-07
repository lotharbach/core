"""Adds config flow for Nord Pool integration."""

from __future__ import annotations

from typing import Any

from pynordpool import NordpoolClient
from pynordpool.const import AREAS, Currency
from pynordpool.exceptions import NordpoolError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_CURRENCY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
from homeassistant.util import dt as dt_util

from .const import CONF_AREAS, DEFAULT_NAME, DOMAIN

SELECT_AREAS = [
    SelectOptionDict(value=area, label=name) for area, name in AREAS.items()
]
SELECT_CURRENCY = [currency.value for currency in Currency]

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_AREAS, default=[]): SelectSelector(
            SelectSelectorConfig(
                options=SELECT_AREAS,
                multiple=True,
                mode=SelectSelectorMode.DROPDOWN,
                sort=True,
            )
        ),
        vol.Required(CONF_CURRENCY, default="SEK"): SelectSelector(
            SelectSelectorConfig(
                options=SELECT_CURRENCY,
                multiple=False,
                mode=SelectSelectorMode.DROPDOWN,
                sort=True,
            )
        ),
    }
)


async def test_api(hass: HomeAssistant, user_input: dict[str, Any]) -> dict[str, str]:
    """Test fetch data from Nord Pool."""
    client = NordpoolClient(async_get_clientsession(hass))
    try:
        data = await client.async_get_delivery_period(
            dt_util.now(),
            Currency(user_input[CONF_CURRENCY]),
            user_input[CONF_AREAS],
        )
    except NordpoolError:
        return {"base": "cannot_connect"}

    if not data.raw:
        return {"base": "no_data"}

    return {}


class NordpoolConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nord Pool integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input:
            areas = user_input[CONF_AREAS]

            errors = await test_api(self.hass, user_input)
            if not errors:
                return self.async_create_entry(
                    title=f"{DEFAULT_NAME} {",".join(areas)}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

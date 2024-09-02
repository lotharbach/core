"""Cover entity for Nice G.O."""

from typing import Any

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import NiceGOConfigEntry
from .entity import NiceGOEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: NiceGOConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nice G.O. cover."""
    coordinator = config_entry.runtime_data

    async_add_entities(
        NiceGOCoverEntity(coordinator, device_id, device_data.name)
        for device_id, device_data in coordinator.data.items()
    )


class NiceGOCoverEntity(NiceGOEntity, CoverEntity):
    """Representation of a Nice G.O. cover."""

    _attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE
    _attr_name = None
    _attr_device_class = CoverDeviceClass.GARAGE

    @property
    def is_closed(self) -> bool:
        """Return if cover is closed."""
        return self.data.barrier_status == "closed"

    @property
    def is_opened(self) -> bool:
        """Return if cover is open."""
        return self.data.barrier_status == "open"

    @property
    def is_opening(self) -> bool:
        """Return if cover is opening."""
        return self.data.barrier_status == "opening"

    @property
    def is_closing(self) -> bool:
        """Return if cover is closing."""
        return self.data.barrier_status == "closing"

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the garage door."""
        if self.is_closed:
            return

        await self.coordinator.api.close_barrier(self._device_id)

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the garage door."""
        if self.is_opened:
            return

        await self.coordinator.api.open_barrier(self._device_id)
"""Support for Lutron shades."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import LUTRON_CONTROLLER, LUTRON_DEVICES, LutronDevice

_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Lutron shades."""
    devs = []
    for area_name, device in hass.data[LUTRON_DEVICES]["cover"]:
        dev = LutronCover(area_name, device, hass.data[LUTRON_CONTROLLER])
        devs.append(dev)

    for area_name, device in hass.data[LUTRON_DEVICES]["venetian"]:
        dev = LutronCover(area_name, device, hass.data[LUTRON_CONTROLLER], can_tilt=True)
        devs.append(dev)

    add_entities(devs, True)


class LutronCover(LutronDevice, CoverEntity):
    """Representation of a Lutron shade."""

    # Set up the Lutron Cover - allowing tilt if it's a venetian blind.
    def __init__(
        self,
        area_name: str,
        lutron_device: LutronDevice,
        lutron_controller: LUTRON_CONTROLLER,
        can_tilt: bool = False,
    ) -> None:
        """Initialize the Lutron cover."""
        super().__init__(area_name, lutron_device, lutron_controller)
        self._can_tilt = can_tilt
        if self._can_tilt:
            self._attr_supported_features = (
                CoverEntityFeature.OPEN
                | CoverEntityFeature.CLOSE
                | CoverEntityFeature.SET_POSITION
                | CoverEntityFeature.OPEN_TILT
                | CoverEntityFeature.CLOSE_TILT
                | CoverEntityFeature.SET_TILT_POSITION
            )
        else:
            self._attr_supported_features = (
                CoverEntityFeature.OPEN
                | CoverEntityFeature.CLOSE
                | CoverEntityFeature.SET_POSITION
            )

    @property
    def is_closed(self) -> bool:
        """Return if the cover is closed."""
        return self._lutron_device.last_level() < 1
    
    @property
    def is_tilt_closed(self) -> bool:
        """Return if the cover is closed."""
        return self._lutron_device.last_tilt() < 1

    @property
    def current_cover_position(self) -> int:
        """Return the current position of cover."""
        return self._lutron_device.last_level()
    
    @property
    def current_cover_tilt_position(self) -> int:
        """Return the current position of cover."""
        return self._lutron_device.last_tilt()

    def close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        self._lutron_device.level = 0

    def open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        self._lutron_device.level = 100

    def set_cover_position(self, **kwargs: Any) -> None:
        """Move the shade to a specific position."""
        if ATTR_POSITION in kwargs:
            position = kwargs[ATTR_POSITION]
            self._lutron_device.level = position

    def set_cover_tilt_position(self, **kwargs: Any) -> None:
        """Move the shade to a specific position."""
        if ATTR_TILT_POSITION in kwargs:
            tilt_position = kwargs[ATTR_TILT_POSITION]
            self._lutron_device.tilt = tilt_position

    def update(self) -> None:
        """Call when forcing a refresh of the device."""
        # Reading the property (rather than last_level()) fetches value
        level = self._lutron_device.level
        _LOGGER.debug("Lutron ID: %d updated to %f position", self._lutron_device.id, level)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {"lutron_integration_id": self._lutron_device.id}

"""Support for Amcrest IP camera binary sensors."""
from __future__ import annotations

from contextlib import suppress
from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Callable

from amcrest import AmcrestError
import voluptuous as vol

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import CONF_BINARY_SENSORS, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle

from .const import (
    BINARY_POLLED_SENSORS,
    BINARY_SENSOR_ONLINE,
    BINARY_SENSOR_SCAN_INTERVAL_SECS,
    BINARY_SENSORS,
    DATA_AMCREST,
    DEVICES,
    EXCLUSIVE_BINARY_SENSORS,
    SERVICE_EVENT,
    SERVICE_UPDATE,
    AmcrestSensorEntityDescription,
)
from .helpers import log_update_error, service_signal

if TYPE_CHECKING:
    from . import AmcrestDevice


_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=BINARY_SENSOR_SCAN_INTERVAL_SECS)
_ONLINE_SCAN_INTERVAL = timedelta(seconds=60 - BINARY_SENSOR_SCAN_INTERVAL_SECS)

_UPDATE_MSG = "Updating %s binary sensor"


def check_binary_sensors(value: list[str]) -> list[str]:
    """Validate binary sensor configurations."""
    for exclusive_options in EXCLUSIVE_BINARY_SENSORS:
        if len(set(value) & exclusive_options) > 1:
            raise vol.Invalid(
                f"must contain at most one of {', '.join(exclusive_options)}."
            )
    return value


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up a binary sensor for an Amcrest IP Camera."""
    if discovery_info is None:
        return

    name = discovery_info[CONF_NAME]
    device = hass.data[DATA_AMCREST][DEVICES][name]
    async_add_entities(
        [
            AmcrestBinarySensor(name, device, sensor_type)
            for sensor_type in discovery_info[CONF_BINARY_SENSORS]
        ],
        True,
    )


class AmcrestBinarySensor(BinarySensorEntity):
    """Binary sensor for Amcrest camera."""

    def __init__(self, name: str, device: AmcrestDevice, sensor_type: str) -> None:
        """Initialize entity."""
        self.entity_description: AmcrestSensorEntityDescription = BINARY_SENSORS[
            sensor_type
        ]
        self._signal_name = name
        self._api = device.api
        self._sensor_type = sensor_type
        self._state: bool | None = None
        self._unsub_dispatcher: list[Callable[[], None]] = []

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return self._sensor_type in BINARY_POLLED_SENSORS

    @property
    def is_on(self) -> bool | None:
        """Return if entity is on."""
        return self._state

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._sensor_type == BINARY_SENSOR_ONLINE or self._api.available

    def update(self) -> None:
        """Update entity."""
        if self._sensor_type == BINARY_SENSOR_ONLINE:
            self._update_online()
        else:
            self._update_others()

    @Throttle(_ONLINE_SCAN_INTERVAL)
    def _update_online(self) -> None:
        if not (self._api.available or self.is_on):
            return
        _LOGGER.debug(_UPDATE_MSG, self.name)
        if self._api.available:
            # Send a command to the camera to test if we can still communicate with it.
            # Override of Http.command() in __init__.py will set self._api.available
            # accordingly.
            with suppress(AmcrestError):
                self._api.current_time  # pylint: disable=pointless-statement
        self._state = self._api.available

    def _update_others(self) -> None:
        if not self.available:
            return
        _LOGGER.debug(_UPDATE_MSG, self.name)

        if self.entity_description.event_code is None:
            _LOGGER.error("Binary sensor %s event code not set", self.name)
            return

        event_code = self.entity_description.event_code
        try:
            self._state = len(self._api.event_channels_happened(event_code)) > 0
        except AmcrestError as error:
            log_update_error(
                _LOGGER, "update", self._signal_name, "binary sensor", error
            )

    async def async_on_demand_update(self) -> None:
        """Update state."""
        if self._sensor_type == BINARY_SENSOR_ONLINE:
            _LOGGER.debug(_UPDATE_MSG, self.name)
            self._state = self._api.available
            self.async_write_ha_state()
        else:
            self.async_schedule_update_ha_state(True)

    @callback
    def async_event_received(self, state: bool) -> None:
        """Update state from received event."""
        _LOGGER.debug(_UPDATE_MSG, self.name)
        self._state = state
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Subscribe to signals."""
        assert self.hass is not None

        self._unsub_dispatcher.append(
            async_dispatcher_connect(
                self.hass,
                service_signal(SERVICE_UPDATE, self._signal_name),
                self.async_on_demand_update,
            )
        )
        if (
            self.entity_description.event_code
            and self._sensor_type not in BINARY_POLLED_SENSORS
        ):
            self._unsub_dispatcher.append(
                async_dispatcher_connect(
                    self.hass,
                    service_signal(
                        SERVICE_EVENT,
                        self._signal_name,
                        self.entity_description.event_code,
                    ),
                    self.async_event_received,
                )
            )

    async def async_will_remove_from_hass(self) -> None:
        """Disconnect from update signal."""
        for unsub_dispatcher in self._unsub_dispatcher:
            unsub_dispatcher()

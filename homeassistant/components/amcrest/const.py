"""Constants for amcrest component."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_SOUND,
    BinarySensorEntityDescription,
)


@dataclass
class AmcrestSensorEntityDescription(BinarySensorEntityDescription):
    """Describe Amcrest sensor entity."""

    event_code: str | None = None


DOMAIN = "amcrest"
DATA_AMCREST = DOMAIN
CAMERAS = "cameras"
DEVICES = "devices"

BINARY_SENSOR_SCAN_INTERVAL_SECS = 5
CAMERA_WEB_SESSION_TIMEOUT = 10
COMM_RETRIES = 1
COMM_TIMEOUT = 6.05
SENSOR_SCAN_INTERVAL_SECS = 10
SNAPSHOT_TIMEOUT = 20

SERVICE_EVENT = "event"
SERVICE_UPDATE = "update"

_BINARY_SENSOR_AUDIO_DETECTED = "audio_detected"
_BINARY_SENSOR_AUDIO_DETECTED_POLLED = "audio_detected_polled"
_BINARY_SENSOR_MOTION_DETECTED = "motion_detected"
_BINARY_SENSOR_MOTION_DETECTED_POLLED = "motion_detected_polled"
_BINARY_SENSOR_CROSSLINE_DETECTED = "crossline_detected"
_BINARY_SENSOR_CROSSLINE_DETECTED_POLLED = "crossline_detected_polled"
BINARY_SENSOR_ONLINE = "online"

_AUDIO_DETECTED_NAME = "Audio Detected"
_AUDIO_DETECTED_EVENT_CODE = "AudioMutation"
_MOTION_DETECTED_NAME = "Motion Detected"
_MOTION_DETECTED_EVENT_CODE = "VideoMotion"
_CROSSLINE_DETECTED_NAME = "Crossline Detected"
_CROSSLINE_DETECTED_EVENT_CODE = "CrossLineDetection"

BINARY_SENSORS = {
    _BINARY_SENSOR_AUDIO_DETECTED: AmcrestSensorEntityDescription(
        key=_BINARY_SENSOR_AUDIO_DETECTED,
        name=_AUDIO_DETECTED_NAME,
        device_class=DEVICE_CLASS_SOUND,
        event_code=_AUDIO_DETECTED_EVENT_CODE,
    ),
    _BINARY_SENSOR_AUDIO_DETECTED_POLLED: AmcrestSensorEntityDescription(
        key=_BINARY_SENSOR_AUDIO_DETECTED_POLLED,
        name=_AUDIO_DETECTED_NAME,
        device_class=DEVICE_CLASS_SOUND,
        event_code=_AUDIO_DETECTED_EVENT_CODE,
    ),
    _BINARY_SENSOR_MOTION_DETECTED: AmcrestSensorEntityDescription(
        key=_BINARY_SENSOR_MOTION_DETECTED,
        name=_MOTION_DETECTED_NAME,
        device_class=DEVICE_CLASS_MOTION,
        event_code=_MOTION_DETECTED_EVENT_CODE,
    ),
    _BINARY_SENSOR_MOTION_DETECTED_POLLED: AmcrestSensorEntityDescription(
        key=_BINARY_SENSOR_MOTION_DETECTED_POLLED,
        name=_MOTION_DETECTED_NAME,
        device_class=DEVICE_CLASS_MOTION,
        event_code=_MOTION_DETECTED_EVENT_CODE,
    ),
    _BINARY_SENSOR_CROSSLINE_DETECTED: AmcrestSensorEntityDescription(
        key=_BINARY_SENSOR_CROSSLINE_DETECTED,
        name=_CROSSLINE_DETECTED_NAME,
        device_class=DEVICE_CLASS_MOTION,
        event_code=_CROSSLINE_DETECTED_EVENT_CODE,
    ),
    _BINARY_SENSOR_CROSSLINE_DETECTED_POLLED: AmcrestSensorEntityDescription(
        key=_BINARY_SENSOR_CROSSLINE_DETECTED_POLLED,
        name=_CROSSLINE_DETECTED_NAME,
        device_class=DEVICE_CLASS_MOTION,
        event_code=_CROSSLINE_DETECTED_EVENT_CODE,
    ),
    BINARY_SENSOR_ONLINE: AmcrestSensorEntityDescription(
        key=BINARY_SENSOR_ONLINE,
        name="Online",
        device_class=DEVICE_CLASS_CONNECTIVITY,
    ),
}

BINARY_POLLED_SENSORS = [
    _BINARY_SENSOR_AUDIO_DETECTED_POLLED,
    _BINARY_SENSOR_MOTION_DETECTED_POLLED,
    BINARY_SENSOR_ONLINE,
]

EXCLUSIVE_BINARY_SENSORS = [
    {_BINARY_SENSOR_AUDIO_DETECTED, _BINARY_SENSOR_AUDIO_DETECTED_POLLED},
    {_BINARY_SENSOR_MOTION_DETECTED, _BINARY_SENSOR_MOTION_DETECTED_POLLED},
    {_BINARY_SENSOR_CROSSLINE_DETECTED, _BINARY_SENSOR_CROSSLINE_DETECTED_POLLED},
]

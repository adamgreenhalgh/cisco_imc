"""Models for the CiscoIMC integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.components.button import ButtonEntityDescription
from homeassistant.components.select import SelectEntityDescription


@dataclass
class CiscoImcSensorEntityDescription(SensorEntityDescription):
    """Sensor entity description for CiscoImc."""

    property_key: str | None = None
    # When set, hass.custom_attributes[imc][attributes_key] is exposed as
    # this sensor's extra_state_attributes under that same key - e.g. a
    # count sensor whose attribute holds the full list it counted.
    attributes_key: str | None = None

@dataclass
class CiscoImcBinarySensorEntityDescription(BinarySensorEntityDescription):
    """BinarySensor entity description for CiscoImc."""

    property_key: str | None = None

@dataclass
class CiscoImcSwitchEntityDescription(SwitchEntityDescription):
    """Switch entity description for CiscoImc."""

    property_key: str | None = None
    # dn/state_on/state_off identify a CIMC-backed hardware feature switch
    # (e.g. locator LED, KVM). When dn is None, the switch is purely local
    # (e.g. the polling switch) and these are unused.
    dn: str | None = None
    state_on: str | None = None
    state_off: str | None = None

@dataclass
class CiscoImcButtonEntityDescription(ButtonEntityDescription):
    """Button entity description for CiscoImc."""

    # "admin_power" (default) writes desired_state to sys/rack-unit-1's
    # admin_power. "eject_vmedia" ignores desired_state and ejects all
    # mounted virtual media instead.
    feature: str = "admin_power"
    desired_state: str | None = None

@dataclass
class CiscoImcSelectEntityDescription(SelectEntityDescription):
    """Select entity description for CiscoImc."""

    property_key: str | None = None
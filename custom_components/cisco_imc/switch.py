"""Switch platform for CiscoImc."""

import logging

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.const import CONF_IP_ADDRESS
from .const import DOMAIN, NAME
from .imc_device import CiscoImcDevice
from .models import CiscoImcSwitchEntityDescription


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the IMC switches by config_entry."""
    print(f"entry_id = {config_entry.entry_id}")
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry_data["coordinator"]
    entities = []
    for device_key in entry_data["devices"]["switch"].keys():
        device_class = entry_data["devices"]["switch"][device_key]
        if device_class.key == "power":
            entities.append(ImcPowerSwitch(hass, config_entry, device_class, coordinator))
        elif device_class.dn:
            entities.append(ImcFeatureSwitch(hass, config_entry, device_class, coordinator))
        else:
            entities.append(ImcPollingSwitch(hass, config_entry, device_class, coordinator))
    async_add_entities(entities, True)



class ImcPollingSwitch(CiscoImcDevice, SwitchEntity):
    """Representation of an IMC polling switch."""

    entity_description: CiscoImcSwitchEntityDescription

    def __init__(self, hass, config_entry, entity_description, coordinator):
        """Initialise the switch."""
        self.hass = hass
        self.platform_name = "switch"
        self.entity_description = entity_description
        self.imc = config_entry.data.get(CONF_IP_ADDRESS)[0]
        self.coordinator = coordinator
        self._attr_name = f"{NAME} {self.imc} {self.entity_description.name}"
        self._attr_available = True
        self._is_on = True
        self.hass.custom_attributes[self.imc]['polling_switch'] = True
        if self.hass.custom_attributes[self.imc]['usr_lbl']:
            self._attr_name = f"{self.hass.custom_attributes[self.imc]['usr_lbl']} {self.entity_description.name}"
        self._attributes = {}
        
        super().__init__(self, hass, self.imc, entity_description, coordinator)


    @property
    def unique_id(self):
        """Return a unique ID."""
        if not self.coordinator.imc:
            return None
        return f"{DOMAIN}_{self.imc.lower().replace('.', '_')}_{self.entity_description.key}"

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        _LOGGER.debug("Enable polling for: %s", self.name)
        self._is_on = True
#        self.coordinator.set_polling_state(True)
        self.hass.custom_attributes[self.imc]['polling_switch'] = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        _LOGGER.debug("Disable polling for: %s", self.name)
        self._is_on = False
#        self.coordinator.set_polling_state(False)
        self.hass.custom_attributes[self.imc]['polling_switch'] = False
        _LOGGER.debug(f"After disabling polling, is_polling = {self.coordinator.is_polling()}")
        self.async_write_ha_state()

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._is_on

    @property
    def available(self):
        return True

    @callback
    def async_update_available(self):
        super().async_update_available()
        self._attr_extra_state_attributes["available"] = True

    @property
    def should_poll(self):
        return False


class ImcFeatureSwitch(CiscoImcDevice, SwitchEntity):
    """Representation of a CIMC-backed hardware feature switch.

    Covers on/off toggles for things like the locator LED, KVM console,
    virtual media, serial-over-LAN and IPMI-over-LAN, all of which are a
    single admin_state property write on a fixed dn.
    """

    entity_description: CiscoImcSwitchEntityDescription

    def __init__(self, hass, config_entry, entity_description, coordinator):
        """Initialise the switch."""
        self.hass = hass
        self.platform_name = "switch"
        self.entity_description = entity_description
        self.imc = config_entry.data.get(CONF_IP_ADDRESS)[0]
        self.coordinator = coordinator
        self._attr_name = f"{NAME} {self.imc} {self.entity_description.name}"
        if self.hass.custom_attributes[self.imc]['usr_lbl']:
            self._attr_name = f"{self.hass.custom_attributes[self.imc]['usr_lbl']} {self.entity_description.name}"
        self._attributes = {}

        super().__init__(self, hass, self.imc, entity_description, coordinator)

    @property
    def unique_id(self):
        """Return a unique ID."""
        if not self.coordinator.imc:
            return None
        return f"{DOMAIN}_{self.imc.lower().replace('.', '_')}_{self.entity_description.key}"

    @property
    def is_on(self):
        """Return the last-polled state of this feature."""
        return bool(self.coordinator.sensor_state(self.entity_description.key))

    @property
    def available(self):
        return True

    async def async_turn_on(self, **kwargs):
        """Enable this feature on the CIMC."""
        await self._async_set_admin_state(self.entity_description.state_on)

    async def async_turn_off(self, **kwargs):
        """Disable this feature on the CIMC."""
        await self._async_set_admin_state(self.entity_description.state_off)

    async def _async_set_admin_state(self, admin_state):
        """Write admin_state to the CIMC and optimistically update cached state."""
        dn = self.entity_description.dn

        def wrapper():
            mo = self.coordinator.client.query_dn(dn)
            mo.admin_state = admin_state
            self.coordinator.client.set_mo(mo)

        await self.hass.async_add_executor_job(wrapper)
        self.hass.custom_attributes[self.imc][self.entity_description.key] = (
            admin_state == self.entity_description.state_on
        )
        self.async_write_ha_state()

    @property
    def should_poll(self):
        return False


class ImcPowerSwitch(CiscoImcDevice, SwitchEntity):
    """Representation of the server's actual power state.

    Unlike ImcFeatureSwitch, this reflects oper_power (already polled as
    part of the rack-unit sensors) and writes admin_power on
    sys/rack-unit-1 itself, matching the Power On/Off buttons.
    """

    entity_description: CiscoImcSwitchEntityDescription

    def __init__(self, hass, config_entry, entity_description, coordinator):
        """Initialise the switch."""
        self.hass = hass
        self.platform_name = "switch"
        self.entity_description = entity_description
        self.imc = config_entry.data.get(CONF_IP_ADDRESS)[0]
        self.coordinator = coordinator
        self._attr_name = f"{NAME} {self.imc} {self.entity_description.name}"
        if self.hass.custom_attributes[self.imc]['usr_lbl']:
            self._attr_name = f"{self.hass.custom_attributes[self.imc]['usr_lbl']} {self.entity_description.name}"
        self._attributes = {}

        super().__init__(self, hass, self.imc, entity_description, coordinator)

    @property
    def unique_id(self):
        """Return a unique ID."""
        if not self.coordinator.imc:
            return None
        return f"{DOMAIN}_{self.imc.lower().replace('.', '_')}_{self.entity_description.key}"

    @property
    def is_on(self):
        """Return whether the server is currently powered on."""
        return self.coordinator.sensor_state("oper_power") == "on"

    @property
    def available(self):
        return True

    async def async_turn_on(self, **kwargs):
        """Power the server on."""
        await self._async_set_admin_power(self.entity_description.state_on)

    async def async_turn_off(self, **kwargs):
        """Gracefully shut the server down."""
        await self._async_set_admin_power(self.entity_description.state_off)

    async def _async_set_admin_power(self, desired_state):
        def wrapper():
            rack_unit_mo = self.coordinator.client.query_dn("sys/rack-unit-1")
            rack_unit_mo.admin_power = desired_state
            self.coordinator.client.set_mo(rack_unit_mo)

        await self.hass.async_add_executor_job(wrapper)
        await self.coordinator.async_request_refresh()

    @property
    def should_poll(self):
        return False

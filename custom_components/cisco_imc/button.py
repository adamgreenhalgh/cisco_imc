"""Button platform for CiscoImc."""
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.const import CONF_IP_ADDRESS

from .const import DOMAIN, NAME
from .imc_device import CiscoImcDevice
from .models import CiscoImcButtonEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the IMC power buttons by config_entry."""
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry_data["coordinator"]
    entities = []
    for device_key in entry_data["devices"]["button"].keys():
        device_class = entry_data["devices"]["button"][device_key]
        entities.append(CiscoImcPowerButton(hass, config_entry, device_class, coordinator))
    async_add_entities(entities, True)


class CiscoImcPowerButton(CiscoImcDevice, ButtonEntity):
    """Representation of a Cisco IMC admin-power action button."""

    entity_description: CiscoImcButtonEntityDescription

    def __init__(self, hass, config_entry, entity_description, coordinator):
        """Initialise the button."""
        self.hass = hass
        self.platform_name = "button"
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
    def available(self):
        return True

    async def async_press(self) -> None:
        """Send the button's admin-power action to the CIMC."""
        _LOGGER.debug(
            "Setting admin_power=%s for %s",
            self.entity_description.desired_state,
            self.imc,
        )

        def wrapper():
            rack_unit_mo = self.coordinator.client.query_dn("sys/rack-unit-1")
            rack_unit_mo.admin_power = self.entity_description.desired_state
            self.coordinator.client.set_mo(rack_unit_mo)

        await self.hass.async_add_executor_job(wrapper)

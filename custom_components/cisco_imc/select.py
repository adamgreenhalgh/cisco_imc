"""Select platform for CiscoImc."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_IP_ADDRESS

from imcsdk.apis.server.boot import boot_order_precision_set

from .const import DOMAIN, NAME, ONE_TIME_BOOT_NONE
from .imc_device import CiscoImcDevice
from .models import CiscoImcSelectEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the IMC boot-device selects by config_entry."""
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry_data["coordinator"]
    entities = []
    for device_key in entry_data["devices"]["select"].keys():
        device_class = entry_data["devices"]["select"][device_key]
        if device_class.key == "one_time_boot_device":
            entities.append(CiscoImcOneTimeBootDeviceSelect(hass, config_entry, device_class, coordinator))
        else:
            entities.append(CiscoImcBootDeviceSelect(hass, config_entry, device_class, coordinator))
    async_add_entities(entities, True)


class CiscoImcBootDeviceSelect(CiscoImcDevice, SelectEntity):
    """Promote a device to first in the CIMC precision boot order.

    Reorders the existing configured boot-precision list so the chosen
    device is first, keeping the other devices in their prior relative
    order. Does not force a reboot.
    """

    entity_description: CiscoImcSelectEntityDescription

    def __init__(self, hass, config_entry, entity_description, coordinator):
        """Initialise the select."""
        self.hass = hass
        self.platform_name = "select"
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

    @property
    def options(self):
        """Return the currently configured boot devices."""
        return [device["name"] for device in self.coordinator.sensor_state("boot_order")]

    @property
    def current_option(self):
        """Return the device currently first in the boot order."""
        boot_order = self.coordinator.sensor_state("boot_order")
        first = next((d for d in boot_order if str(d["order"]) == "1"), None)
        return first["name"] if first else None

    async def async_select_option(self, option: str) -> None:
        """Promote the selected device to boot order 1."""

        def wrapper():
            boot_order = self.hass.custom_attributes[self.imc]["boot_order"]
            configured_boot_mode = self.hass.custom_attributes[self.imc]["configured_boot_mode"]

            selected = [d for d in boot_order if d["name"] == option]
            remaining = [d for d in boot_order if d["name"] != option]

            reordered = [
                {"order": "1", "device-type": d["device-type"], "name": d["name"]}
                for d in selected
            ]
            for index, device in enumerate(remaining, start=2):
                reordered.append({
                    "order": str(index),
                    "device-type": device["device-type"],
                    "name": device["name"],
                })

            boot_order_precision_set(
                self.coordinator.client,
                reboot_on_update="no",
                reapply="no",
                configured_boot_mode=configured_boot_mode,
                boot_devices=reordered,
            )

        await self.hass.async_add_executor_job(wrapper)
        await self.coordinator.async_request_refresh()

    @property
    def should_poll(self):
        return False


class CiscoImcOneTimeBootDeviceSelect(CiscoImcDevice, SelectEntity):
    """Set (or clear) a one-time next-boot device override.

    Unlike CiscoImcBootDeviceSelect, this doesn't touch the persistent
    boot order - it sets sys/rack-unit-1/one-time-precision-boot, which
    CIMC applies for exactly one boot and then reverts automatically.
    Safer for one-off PXE/rescue boots.
    """

    entity_description: CiscoImcSelectEntityDescription

    def __init__(self, hass, config_entry, entity_description, coordinator):
        """Initialise the select."""
        self.hass = hass
        self.platform_name = "select"
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

    @property
    def options(self):
        """Return the known boot devices, plus the option to clear any pending override."""
        boot_order = self.coordinator.sensor_state("boot_order")
        return [ONE_TIME_BOOT_NONE] + [device["name"] for device in boot_order]

    @property
    def current_option(self):
        """Return the pending one-time boot device, or ONE_TIME_BOOT_NONE if none is set."""
        return self.coordinator.sensor_state("one_time_boot_device") or ONE_TIME_BOOT_NONE

    async def async_select_option(self, option: str) -> None:
        """Set, or clear, the one-time boot device override."""

        def wrapper():
            dn = "sys/rack-unit-1/one-time-precision-boot"
            mo = self.coordinator.client.query_dn(dn)
            if option == ONE_TIME_BOOT_NONE:
                mo.admin_action = "clear-one-time-boot-device"
            else:
                mo.device = option
                mo.reboot_on_update = "no"
            self.coordinator.client.set_mo(mo)

        await self.hass.async_add_executor_job(wrapper)
        await self.coordinator.async_request_refresh()

    @property
    def should_poll(self):
        return False

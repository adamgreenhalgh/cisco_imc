"""CiscoImc services."""
import asyncio
import voluptuous as vol
import iso8601
import logging

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_component
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import device_registry as dr

from datetime import datetime
from imcsdk.imchandle import ImcHandle
from imcsdk.apis.server.vmedia import (
    vmedia_mount_iso_uri,
    vmedia_mount_delete,
    vmedia_mount_remove_all,
)

# pylint: disable=relative-beyond-top-level
from .const import (
    DOMAIN,
    CISCO_IMC_SERVICES,
    SERVICE_DESIRED_STATE,
    SERVICE_ENTITY_TYPE,
    SERVICE_ENTITY_ID,
    SERVICE_ENTRY_ID,
    SERVICE_DATA,
    SERVICE_SET_ADMIN_POWER,
    SERVICE_MOUNT_ISO,
    SERVICE_UNMOUNT_ISO,
    SERVICE_URI,
    SERVICE_VOLUME_NAME,
    SERVICE_USERNAME,
    SERVICE_PASSWORD,
)

_LOGGER = logging.getLogger(__name__)


SERVICE_SET_ADMIN_POWER_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Required(SERVICE_DESIRED_STATE): str,
            vol.Required(SERVICE_ENTITY_ID): str,
        }
    )
)

SERVICE_MOUNT_ISO_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Required(SERVICE_ENTITY_ID): str,
            vol.Required(SERVICE_URI): str,
            vol.Optional(SERVICE_VOLUME_NAME): str,
            vol.Optional(SERVICE_USERNAME): str,
            vol.Optional(SERVICE_PASSWORD): str,
        }
    )
)

SERVICE_UNMOUNT_ISO_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Required(SERVICE_ENTITY_ID): str,
            vol.Optional(SERVICE_VOLUME_NAME): str,
        }
    )
)

async def async_setup_services(hass):
    """Set up services for CiscoImc integration."""

    async def async_call_cisco_imc_service(service_call):
        """Call correct CiscoImc service."""
        service = service_call.service
        service_data = service_call.data

        if service == SERVICE_SET_ADMIN_POWER:
            await async_set_admin_power_service(hass, service_data)
        elif service == SERVICE_MOUNT_ISO:
            await async_mount_iso_service(hass, service_data)
        elif service == SERVICE_UNMOUNT_ISO:
            await async_unmount_iso_service(hass, service_data)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_ADMIN_POWER,
        async_call_cisco_imc_service,
        schema=SERVICE_SET_ADMIN_POWER_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_MOUNT_ISO,
        async_call_cisco_imc_service,
        schema=SERVICE_MOUNT_ISO_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UNMOUNT_ISO,
        async_call_cisco_imc_service,
        schema=SERVICE_UNMOUNT_ISO_SCHEMA,
    )
    _LOGGER.debug("Set up service")


async def async_unload_services(hass):
    """Unload CiscoImc services."""
    if not hass.data.get(DOMAIN):
        return

    hass.services.async_remove(DOMAIN, SERVICE_SET_ADMIN_POWER)
    hass.services.async_remove(DOMAIN, SERVICE_MOUNT_ISO)
    hass.services.async_remove(DOMAIN, SERVICE_UNMOUNT_ISO)


async def async_set_admin_power_service(hass, data):
    """Set the Admin_Power state in CiscoImc."""
    service_entity_id = data[SERVICE_ENTITY_ID]
    desired_state = data[SERVICE_DESIRED_STATE]
    _LOGGER.debug("EntityID: {}".format(service_entity_id))

    def wrapper():
        entity_reg = er.async_get(hass)
        entry = entity_reg.async_get(service_entity_id)
        _LOGGER.debug("Entity Registry Items for {}: {}".format(service_entity_id, entity_reg))
        local_id = entry.config_entry_id
        local_coordinator = hass.data[DOMAIN][local_id]["coordinator"]
        imc_rack_unit_mo = local_coordinator.client.query_dn("sys/rack-unit-1")
        imc_rack_unit_mo.admin_power = desired_state
        local_coordinator.client.set_mo(imc_rack_unit_mo)

    await hass.async_add_executor_job(wrapper)


def _get_coordinator_for_entity(hass, service_entity_id):
    """Resolve the CiscoImcDataService coordinator for an entity_id."""
    entity_reg = er.async_get(hass)
    entry = entity_reg.async_get(service_entity_id)
    local_id = entry.config_entry_id
    return hass.data[DOMAIN][local_id]["coordinator"]


async def async_mount_iso_service(hass, data):
    """Mount a remote ISO via CIMC virtual media."""
    service_entity_id = data[SERVICE_ENTITY_ID]
    uri = data[SERVICE_URI]
    volume_name = data.get(SERVICE_VOLUME_NAME)
    username = data.get(SERVICE_USERNAME)
    password = data.get(SERVICE_PASSWORD)
    _LOGGER.debug("Mounting ISO %s for entity %s", uri, service_entity_id)

    def wrapper():
        local_coordinator = _get_coordinator_for_entity(hass, service_entity_id)
        vmedia_mount_iso_uri(
            local_coordinator.client,
            uri,
            volume_name=volume_name,
            user_id=username,
            password=password,
        )

    await hass.async_add_executor_job(wrapper)


async def async_unmount_iso_service(hass, data):
    """Unmount a CIMC virtual media volume, or all of them if none given."""
    service_entity_id = data[SERVICE_ENTITY_ID]
    volume_name = data.get(SERVICE_VOLUME_NAME)
    _LOGGER.debug("Unmounting ISO volume %s for entity %s", volume_name, service_entity_id)

    def wrapper():
        local_coordinator = _get_coordinator_for_entity(hass, service_entity_id)
        if volume_name:
            vmedia_mount_delete(local_coordinator.client, volume_name)
        else:
            vmedia_mount_remove_all(local_coordinator.client)

    await hass.async_add_executor_job(wrapper)

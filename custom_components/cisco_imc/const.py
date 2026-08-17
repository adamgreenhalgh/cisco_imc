"""Constants for CiscoImc."""
from enum import Enum
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

from .models import (
    CiscoImcBinarySensorEntityDescription,
    CiscoImcSensorEntityDescription,
    CiscoImcSwitchEntityDescription,
    CiscoImcButtonEntityDescription,
    CiscoImcSelectEntityDescription,
)

# Base component constants
NAME = "Cisco IMC"
DOMAIN = "cisco_imc"
VERSION = "v2.3.2"

ISSUE_URL = "https://github.com/adamgreenhalgh/cisco_imc/issues"

LOGGER = logging.getLogger(__package__)

DATA_API_CLIENT = "api_client"

RACK_UNIT_UPDATE_DELAY = timedelta(minutes=1)

DATA_LISTENER = "listener"
ICONS = {
    "model": "mdi:card-text-outline",
    "serial": "mdi:numeric",
    "asset_tag": "mdi:tag-outline",
    "usr_lbl": "mdi:label-outline",
    "uuid": "mdi:sticker-text-outline",
    "num_of_cpus": "mdi:cpu-64-bit",
    "num_of_cores": "mdi:checkbox-multiple-blank-outline",
    "num_of_threads": "mdi:math-norm",
    "total_memory": "mdi:memory",
    "cimc_reset_reason": "mdi:alert-octagon-outline",
    "oper_power": "mdi:power",
    "reachable": "mdi:lan-connect",
    "polling_switch": "mdi:sync",
    "ip_address": "mdi:ip-outline",
}
DEFAULT_SCAN_INTERVAL = 660
MIN_SCAN_INTERVAL = 60

SIGNAL_STATE_UPDATED = f"{DOMAIN}.updated"

# Platforms
PLATFORMS = ["binary_sensor", "sensor", "switch", "button", "select"]

# Configuration and options
CONF_NAME = "name"

RACK_UNIT_SENSORS = [
    "model",
    "serial",
    "asset_tag",
    "usr_lbl",
    "uuid",
    "num_of_cpus",
    "num_of_cores",
    "num_of_threads",
    "total_memory",
    "cimc_reset_reason",
    "oper_power"
]

STATIC_SENSOR = "ip_address"
SWITCH = "polling_switch"
BINARY_SENSOR = "reachable"

POLLING_ICON = "mdi:sync"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

CISCO_IMC_SERVICES = "cisco_imc_services"
SERVICE_DESIRED_STATE = "desired_state"
SERVICE_ENTITY_TYPE = "entity_type"
SERVICE_ENTITY_ID = "entity_id"
SERVICE_ENTRY_ID = "config_entry_id"
SERVICE_DATA = "data"
SERVICE_SET_ADMIN_POWER = "set_admin_power"
SERVICE_MOUNT_ISO = "mount_iso"
SERVICE_UNMOUNT_ISO = "unmount_iso"
SERVICE_URI = "uri"
SERVICE_VOLUME_NAME = "volume_name"
SERVICE_USERNAME = "username"
SERVICE_PASSWORD = "password"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
SENSOR_TYPES = [
    CiscoImcSensorEntityDescription(
        key="model",
        name="Model",
        icon="mdi:card-text-outline",
    ),
    CiscoImcSensorEntityDescription(
        key="serial",
        name="Serial",
        icon="mdi:numeric",
    ),
    CiscoImcSensorEntityDescription(
        key="asset_tag",
        name="Asset Tag",
        icon="mdi:tag-outline",
    ),
    CiscoImcSensorEntityDescription(
        key="usr_lbl",
        name="User Label",
        icon="mdi:label-outline",
    ),
    CiscoImcSensorEntityDescription(
        key="uuid",
        name="UUID",
        icon="mdi:sticker-text-outline",
    ),
    CiscoImcSensorEntityDescription(
        key="num_of_cpus",
        name="CPUs",
        icon="mdi:cpu-64-bit",
    ),
    CiscoImcSensorEntityDescription(
        key="num_of_cores",
        name="Cores",
        icon="mdi:checkbox-multiple-blank-outline",
    ),
    CiscoImcSensorEntityDescription(
        key="num_of_threads",
        name="Threads",
        icon="mdi:math-norm",
    ),
    CiscoImcSensorEntityDescription(
        key="total_memory",
        name="Total Memory",
        icon="mdi:memory",
        unit_of_measurement="MB",
    ),
    CiscoImcSensorEntityDescription(
        key="cimc_reset_reason",
        name="Reset Reason",
        icon="mdi:alert-octagon-outline",
    ),
    CiscoImcSensorEntityDescription(
        key="oper_power",
        name="Power",
        icon="mdi:power",
    ),
]

STATIC_SENSOR_TYPE = CiscoImcSensorEntityDescription(
    key="ip_address",
    name="IP Address",
    icon="mdi:ip-outline",
)

FAULT_COUNT_SENSOR = "fault_count"
FAULT_COUNT_SENSOR_TYPE = CiscoImcSensorEntityDescription(
    key=FAULT_COUNT_SENSOR,
    name="Fault Count",
    icon="mdi:alert-circle-outline",
)

# Populated PCIe slots (adaptors, HBAs, GPUs, etc.) from PciEquipSlot.
# The sensor's state is just the count; the full per-device list (model,
# vendor, pid, firmware version) is exposed as an attribute since it's a
# variable-length list, not something worth a fixed set of entities.
PCI_DEVICE_COUNT_SENSOR = "pci_device_count"
PCI_DEVICES_ATTR = "pci_devices"
PCI_DEVICE_COUNT_SENSOR_TYPE = CiscoImcSensorEntityDescription(
    key=PCI_DEVICE_COUNT_SENSOR,
    name="PCI Device Count",
    icon="mdi:expansion-card",
    attributes_key=PCI_DEVICES_ATTR,
)

# CPU make/model from ProcessorUnit. State is the first equipped socket's
# model string (in practice all sockets match on every server we've seen);
# the full per-socket breakdown (vendor, speed, cores, threads, presence)
# is exposed as an attribute for asymmetric/partially-populated cases.
CPU_MODEL_SENSOR = "cpu_model"
CPUS_ATTR = "cpu_details"
CPU_MODEL_SENSOR_TYPE = CiscoImcSensorEntityDescription(
    key=CPU_MODEL_SENSOR,
    name="CPU Model",
    icon="mdi:cpu-64-bit",
    attributes_key=CPUS_ATTR,
)

# Severities counted as an actual problem for FAULT_PROBLEM_TYPE below.
# "condition"/"info"/"cleared" are excluded as informational/resolved.
FAULT_PROBLEM_SEVERITIES = {"critical", "major", "minor", "warning"}

BINARY_SENSOR_TYPE = CiscoImcBinarySensorEntityDescription(
    key="reachable",
    name="Reachable",
    icon="mdi:lan-connect",
    device_class=BinarySensorDeviceClass.CONNECTIVITY
)

FAULT_PROBLEM_SENSOR = "fault_problem"
FAULT_PROBLEM_TYPE = CiscoImcBinarySensorEntityDescription(
    key=FAULT_PROBLEM_SENSOR,
    name="Fault",
    icon="mdi:alert-octagon-outline",
    device_class=BinarySensorDeviceClass.PROBLEM,
)

SWITCH_TYPE = CiscoImcSwitchEntityDescription(
    key="polling_switch",
    name="Polling Switch",
    icon="mdi:sync",
    device_class=SwitchDeviceClass.SWITCH
)

BUTTON_TYPES = [
    CiscoImcButtonEntityDescription(
        key="power_on",
        name="Power On",
        icon="mdi:power-on",
        desired_state="up",
    ),
    CiscoImcButtonEntityDescription(
        key="power_off",
        name="Power Off",
        icon="mdi:power-off",
        desired_state="soft-shut-down",
    ),
    CiscoImcButtonEntityDescription(
        key="power_cycle",
        name="Power Cycle",
        icon="mdi:restart",
        desired_state="cycle-immediate",
    ),
    CiscoImcButtonEntityDescription(
        key="hard_reset",
        name="Hard Reset",
        icon="mdi:restart-alert",
        desired_state="hard-reset-immediate",
    ),
    CiscoImcButtonEntityDescription(
        key="eject_all_vmedia",
        name="Eject All Virtual Media",
        icon="mdi:eject",
        feature="eject_vmedia",
    ),
]

# CIMC-backed hardware feature switches. All read/write a single
# "admin_state" property on a fixed dn under sys/rack-unit-1 or
# sys/svc-ext (classic/rack-mount platform only, matching the rest of
# this integration's assumptions).
FEATURE_SWITCH_TYPES = [
    CiscoImcSwitchEntityDescription(
        key="locator_led",
        name="Locator LED",
        icon="mdi:led-on",
        device_class=SwitchDeviceClass.SWITCH,
        dn="sys/rack-unit-1/locator-led",
        state_on="on",
        state_off="off",
    ),
    CiscoImcSwitchEntityDescription(
        key="kvm",
        name="KVM Console",
        icon="mdi:remote-desktop",
        device_class=SwitchDeviceClass.SWITCH,
        dn="sys/svc-ext/kvm-svc",
        state_on="enabled",
        state_off="disabled",
    ),
    CiscoImcSwitchEntityDescription(
        key="vmedia",
        name="Virtual Media",
        icon="mdi:disc-player",
        device_class=SwitchDeviceClass.SWITCH,
        dn="sys/svc-ext/vmedia-svc",
        state_on="enabled",
        state_off="disabled",
    ),
    CiscoImcSwitchEntityDescription(
        key="sol",
        name="Serial Over LAN",
        icon="mdi:console-network",
        device_class=SwitchDeviceClass.SWITCH,
        dn="sys/rack-unit-1/sol-if",
        state_on="enable",
        state_off="disable",
    ),
    CiscoImcSwitchEntityDescription(
        key="ipmi_lan",
        name="IPMI over LAN",
        icon="mdi:server-network",
        device_class=SwitchDeviceClass.SWITCH,
        dn="sys/svc-ext/ipmi-lan-svc",
        state_on="enabled",
        state_off="disabled",
    ),
]

# Handled separately from FEATURE_SWITCH_TYPES: reflects oper_power
# (already polled as part of RACK_UNIT_SENSORS) rather than an
# admin_state on a sub-object, and writes admin_power on sys/rack-unit-1
# itself rather than admin_state.
POWER_SWITCH_TYPE = CiscoImcSwitchEntityDescription(
    key="power",
    name="Power",
    icon="mdi:power",
    device_class=SwitchDeviceClass.SWITCH,
    state_on="up",
    state_off="soft-shut-down",
)

BOOT_DEVICE_SELECT_TYPE = CiscoImcSelectEntityDescription(
    key="next_boot_device",
    name="Next Boot Device",
    icon="mdi:restart",
)

# Sentinel option representing "no one-time boot device pending".
ONE_TIME_BOOT_NONE = "None"

ONE_TIME_BOOT_SELECT_TYPE = CiscoImcSelectEntityDescription(
    key="one_time_boot_device",
    name="One-Time Boot Device",
    icon="mdi:restart-alert",
)

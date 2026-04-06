"""The Russound RIO Enhanced integration."""

from __future__ import annotations

import logging

import aiorussound.util as rs_util
from aiorussound import RussoundClient, RussoundTcpConnectionHandler

from .const import DOMAIN, MBX_SOURCE_MODE_DEVICES
from .riose import MbxRioSeClient

try:
    import aiorussound.rio as rs_rio
except ImportError:
    rs_rio = None

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.MEDIA_PLAYER,
    Platform.NUMBER,
    Platform.SWITCH,
    Platform.BUTTON,
]

type RussoundConfigEntry = ConfigEntry[RussoundClient]


def _patched_get_max_zones(controller_type: str) -> int:
    """Return the correct max zones for supported controllers."""
    if controller_type == "SMZ16-PRE":
        return 16

    original = getattr(_patched_get_max_zones, "_original", None)
    if original is None:
        raise RuntimeError("Original get_max_zones function not available")

    return original(controller_type)


def _apply_smz16_patch() -> None:
    """Patch aiorussound zone count handling for SMZ16-PRE."""
    if not hasattr(_patched_get_max_zones, "_original"):
        _patched_get_max_zones._original = rs_util.get_max_zones  # type: ignore[attr-defined]

    rs_util.get_max_zones = _patched_get_max_zones  # type: ignore[assignment]

    if rs_rio is not None:
        rs_rio.get_max_zones = _patched_get_max_zones  # type: ignore[assignment]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Russound RIO Enhanced integration."""
    _apply_smz16_patch()
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RussoundConfigEntry,
) -> bool:
    """Set up Russound RIO Enhanced from a config entry."""
    _apply_smz16_patch()

    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    client = RussoundClient(RussoundTcpConnectionHandler(host, port))

    try:
        await client.connect()
        await client.load_zone_source_metadata()
    except Exception as err:
        raise ConfigEntryNotReady(
            f"Unable to connect to Russound controller at {host}:{port}"
        ) from err

    mbx_clients: dict[str, MbxRioSeClient] = {}

    for device in MBX_SOURCE_MODE_DEVICES:
        name = str(device["name"])
        mbx_host = str(device["host"])
        mbx_port = int(device["port"])
        source_id = int(device["source_id"])

        mbx_client = MbxRioSeClient(
            host=mbx_host,
            port=mbx_port,
            source_id=source_id,
            name=name,
        )

        try:
            await mbx_client.connect()
            await mbx_client.initialize()
            mbx_clients[name] = mbx_client
            _LOGGER.info(
                "Connected MBX RIO SE source client: %s (%s:%s, source_id=%s)",
                name,
                mbx_host,
                mbx_port,
                source_id,
            )
        except Exception as err:
            _LOGGER.warning(
                "Failed to connect MBX RIO SE source client %s at %s:%s: %s",
                name,
                mbx_host,
                mbx_port,
                err,
            )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "controller_client": client,
        "mbx_clients": mbx_clients,
    }

    entry.runtime_data = client

    if 1 in client.controllers:
        _LOGGER.warning(
            "Russound controller 1 zone count: %s",
            len(client.controllers[1].zones),
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: RussoundConfigEntry,
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    client = entry.runtime_data
    if unload_ok and client is not None:
        try:
            client.clear_state_update_callbacks()
            await client.disconnect()
        except Exception:
            _LOGGER.debug("Error while disconnecting Russound client", exc_info=True)

    domain_data = hass.data.get(DOMAIN, {})
    entry_data = domain_data.get(entry.entry_id, {})
    mbx_clients: dict[str, MbxRioSeClient] = entry_data.get("mbx_clients", {})

    for mbx_client in mbx_clients.values():
        try:
            await mbx_client.disconnect()
        except Exception:
            _LOGGER.debug("Error while disconnecting MBX RIO SE client", exc_info=True)

    domain_data.pop(entry.entry_id, None)

    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: RussoundConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)

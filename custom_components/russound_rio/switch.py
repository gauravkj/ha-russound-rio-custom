"""Switch platform for Russound RIO Enhanced."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from aiorussound import RussoundClient
from aiorussound.models import RussoundZone

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RussoundConfigEntry
from .const import DOMAIN
from .entity import RussoundZoneEntity


@dataclass(frozen=True)
class RussoundZoneSwitchDescription:
    """Describe a Russound zone switch entity."""

    key: str
    name: str
    icon: str
    is_on_fn: Callable[[RussoundZone], bool]
    turn_on_fn: Callable[[RussoundClient, int, int], object]
    turn_off_fn: Callable[[RussoundClient, int, int], object]


SWITCH_TYPES: tuple[RussoundZoneSwitchDescription, ...] = (
    RussoundZoneSwitchDescription(
        key="low_volume_boost",
        name="Low Volume Boost",
        icon="mdi:volume-plus",
        is_on_fn=lambda zone: bool(zone.low_volume_boost),
        turn_on_fn=lambda client, controller_id, zone_id: client.set_low_volume_boost(
            controller_id, zone_id, True
        ),
        turn_off_fn=lambda client, controller_id, zone_id: client.set_low_volume_boost(
            controller_id, zone_id, False
        ),
    ),
    RussoundZoneSwitchDescription(
        key="do_not_disturb",
        name="Do Not Disturb",
        icon="mdi:minus-circle-off",
        is_on_fn=lambda zone: bool(zone.do_not_disturb),
        turn_on_fn=lambda client, controller_id, zone_id: client.set_do_not_disturb(
            controller_id, zone_id, True
        ),
        turn_off_fn=lambda client, controller_id, zone_id: client.set_do_not_disturb(
            controller_id, zone_id, False
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Russound switch entities from a config entry."""
    russound_entry = entry
    client: RussoundClient = russound_entry.runtime_data

    entities: list[RussoundZoneSwitch] = []

    for controller_id, controller in client.controllers.items():
        for zone_id, zone in controller.zones.items():
            for description in SWITCH_TYPES:
                entities.append(
                    RussoundZoneSwitch(
                        russound_entry,
                        controller_id,
                        zone_id,
                        description,
                    )
                )

    async_add_entities(entities)


class RussoundZoneSwitch(RussoundZoneEntity, SwitchEntity):
    """Representation of a Russound zone switch."""

    entity_description: RussoundZoneSwitchDescription

    def __init__(
        self,
        entry: RussoundConfigEntry,
        controller_id: int,
        zone_id: int,
        description: RussoundZoneSwitchDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(entry, controller_id, zone_id)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_name = description.name
        self._attr_icon = description.icon
        self._attr_unique_id = (
            f"{DOMAIN}_{controller_id}_{zone_id}_{description.key}"
        )

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        zone = self.zone
        if zone is None:
            return False
        return self.entity_description.is_on_fn(zone)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self.entity_description.turn_on_fn(
            self.client,
            self.controller_id,
            self.zone_id,
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self.entity_description.turn_off_fn(
            self.client,
            self.controller_id,
            self.zone_id,
        )

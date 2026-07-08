"""Support for buttons."""

from typing import override

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import MIKROTIK_SERVICES
from .coordinator import (
    MikrotikConfigEntry,
    MikrotikDataUpdateCoordinator,
    mikrotik_config_entry_errors,
)

# Coordinator is used to centralize the data updates
PARALLEL_UPDATES = 0


BUTTON_TYPES = {
    ButtonEntityDescription(
        key="reboot",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
    ),
    ButtonEntityDescription(
        key="shutdown",
        translation_key="shutdown",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MikrotikConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up button entities for Mikrotik Devices."""

    coordinator = entry.runtime_data

    sensors_list = [
        MikrotikButtonEntity(coordinator, sensor_desc) for sensor_desc in BUTTON_TYPES
    ]

    async_add_entities(sensors_list)


class MikrotikButtonEntity(
    CoordinatorEntity[MikrotikDataUpdateCoordinator], ButtonEntity
):
    """Button entity for Mikrotik."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MikrotikDataUpdateCoordinator,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize button entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{coordinator.api.serial_number}_{description.key}"

    @override
    async def async_press(self) -> None:
        """Handle button press action."""
        with mikrotik_config_entry_errors():
            self.coordinator.api.command(MIKROTIK_SERVICES[self.entity_description.key])

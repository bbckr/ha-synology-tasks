"""Support for Synology DSM Task sensors."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CAN_RUN,
    ATTR_NEXT_RUN_TIME,
    ATTR_TASK_ENABLED,
    ATTR_TASK_ID,
    ATTR_TASK_NAME,
    ATTR_TASK_OWNER,
    ATTR_TASK_TYPE,
    CONFIG_DEVICE_IDENTIFIERS,
    CONFIG_DEVICE_MANUFACTURER,
    CONFIG_DEVICE_MODEL,
    CONFIG_DEVICE_NAME,
    CONFIG_DEVICE_SW_VERSION,
    DOMAIN,
    KEY_STATUS,
    STATE_DISABLED,
    STATE_ENABLED,
    TRANSLATION_KEY_TASK_STATUS,
)
from .coordinator import SynologyTasksCoordinator

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType

    from .models import Task

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SynologyTaskSensorEntityDescription(SensorEntityDescription):
    """Class describing Synology task sensor entities."""

    value_fn: Callable[[Task], StateType] = lambda _: None


TASK_SENSORS = [
    SynologyTaskSensorEntityDescription(
        key=KEY_STATUS,
        translation_key=TRANSLATION_KEY_TASK_STATUS,
        icon="mdi:calendar-check",
        value_fn=lambda task: STATE_ENABLED if task.enabled else STATE_DISABLED,
    ),
]


class SynologyTaskSensor(CoordinatorEntity[SynologyTasksCoordinator], SensorEntity):
    """Representation of a Synology task sensor."""

    entity_description: SynologyTaskSensorEntityDescription

    def __init__(
        self,
        coordinator: SynologyTasksCoordinator,
        task: Task,
        entity_description: SynologyTaskSensorEntityDescription,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._task = task
        # Convert task name to snake_case for unique_id
        # Convert task name to snake_case and remove special characters
        task_name_id = "".join(c if c.isalnum() or c == " " else "_" for c in task.name)
        task_name_id = task_name_id.lower().replace(" ", "_")
        self._attr_unique_id = f"{task_name_id}_{task.id}_{entity_description.key}"
        self.unique_id = self._attr_unique_id

        # Set device info from the Synology DSM device
        if config_entry.data.get(CONFIG_DEVICE_IDENTIFIERS):
            # Convert identifiers list back to set of tuples (JSON converts sets to
            # lists)
            identifiers = {
                tuple(identifier)
                for identifier in config_entry.data[CONFIG_DEVICE_IDENTIFIERS]
            }
            self._attr_device_info = DeviceInfo(
                identifiers=identifiers,
                name=config_entry.data.get(CONFIG_DEVICE_NAME),
                manufacturer=config_entry.data.get(CONFIG_DEVICE_MANUFACTURER),
                model=config_entry.data.get(CONFIG_DEVICE_MODEL),
                sw_version=config_entry.data.get(CONFIG_DEVICE_SW_VERSION),
            )

        # Set a clean display name - just the task name
        self._attr_name = task.name
        self._attr_has_entity_name = False

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not (task := self._get_task()):
            return None
        return self.entity_description.value_fn(task)

    @property
    def extra_state_attributes(self) -> dict[str, str | int | bool | datetime | None]:
        """Return the state attributes."""
        if not (task := self._get_task()):
            return {}

        return {
            ATTR_TASK_ID: task.id,
            ATTR_TASK_NAME: task.name,
            ATTR_TASK_TYPE: task.type,
            ATTR_TASK_OWNER: task.owner,
            ATTR_TASK_ENABLED: task.enabled,
            ATTR_NEXT_RUN_TIME: task.next_run_time,
            ATTR_CAN_RUN: task.can_run,
        }

    def _get_task(self) -> Task | None:
        """Get the task data from the coordinator."""
        if not self.coordinator.data:
            return None
        return next(
            (task for task in self.coordinator.data if task.id == self._task.id),
            None,
        )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Synology task sensors."""
    coordinator: SynologyTasksCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    @callback
    def _create_entities(tasks: list[Task]) -> list[SynologyTaskSensor]:
        """Create sensor entities for the tasks."""
        entities: list[SynologyTaskSensor] = []

        for task in tasks:
            entities.extend(
                SynologyTaskSensor(
                    coordinator=coordinator,
                    task=task,
                    entity_description=description,
                    config_entry=entry,
                )
                for description in TASK_SENSORS
            )

        return entities

    # Create initial entities
    async_add_entities(_create_entities(coordinator.data))

    # Track existing entity IDs to avoid duplicates
    existing_ids = {entity.unique_id for entity in _create_entities(coordinator.data)}

    @callback
    def _async_update_entities() -> None:
        """Create new entities for new tasks."""
        new_entities = []
        current_entities = _create_entities(coordinator.data)

        for entity in current_entities:
            if entity.unique_id not in existing_ids:
                new_entities.append(entity)
                existing_ids.add(entity.unique_id)

        if new_entities:
            async_add_entities(new_entities)

    coordinator.async_add_listener(_async_update_entities)

"""Tests for binary sensors."""

from homeassistant.core import HomeAssistant

from .conftest import (
    EntityAndExpectedValues,
    _test_sensors,
    get_lifetime_data,
    get_vitals_data,
    get_wifi_status_data,
)


async def test_sensors(hass: HomeAssistant) -> None:
    """Test all binary sensors."""

    entity_and_expected_values = [
        EntityAndExpectedValues(
            "binary_sensor.tesla_wall_connector_contactor_closed", "off", "on"
        ),
        EntityAndExpectedValues(
            "binary_sensor.tesla_wall_connector_vehicle_connected", "on", "off"
        ),
    ]

    vitals_first_update = get_vitals_data()
    vitals_second_update = get_vitals_data(
        contactor_closed=True, vehicle_connected=False
    )
    lifetime_data = get_lifetime_data()
    wifi_status_data = get_wifi_status_data()

    await _test_sensors(
        hass,
        entities_and_expected_values=entity_and_expected_values,
        vitals_first_update=vitals_first_update,
        vitals_second_update=vitals_second_update,
        lifetime_first_update=lifetime_data,
        lifetime_second_update=lifetime_data,
        wifi_status_first_update=wifi_status_data,
        wifi_status_second_update=wifi_status_data,
    )

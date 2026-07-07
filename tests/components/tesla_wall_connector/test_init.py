"""Test the Tesla Wall Connector config flow."""

from unittest.mock import AsyncMock, patch

from tesla_wall_connector.exceptions import WallConnectorConnectionError

from homeassistant.components.tesla_wall_connector.const import (
    CONF_SPLIT_PHASE,
    DOMAIN,
    WALLCONNECTOR_DEVICE_MANUFACTURER,
    WALLCONNECTOR_DEVICE_MODEL,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
import homeassistant.helpers.device_registry as dr

from .conftest import (
    create_wall_connector_entry,
    get_default_version_data,
    get_lifetime_data,
    get_vitals_data,
    get_wifi_status_data,
)

from tests.common import MockConfigEntry


async def test_init_success(
    hass: HomeAssistant, device_registry: dr.DeviceRegistry
) -> None:
    """Test setup and that we get the device info, including firmware version."""

    entry = await create_wall_connector_entry(
        hass,
        vitals_data=get_vitals_data(),
        lifetime_data=get_lifetime_data(),
        wifi_status_data=get_wifi_status_data(),
    )

    assert entry.state is ConfigEntryState.LOADED
    device = device_registry.async_get_device(identifiers={(DOMAIN, "abc123")})
    assert device
    assert device.manufacturer == WALLCONNECTOR_DEVICE_MANUFACTURER
    assert device.model == WALLCONNECTOR_DEVICE_MODEL
    assert device.model_id == "part_123"
    assert device.serial_number == "abc123"
    assert device.sw_version == "1.2.3"


async def test_init_while_offline(hass: HomeAssistant) -> None:
    """Test init with the wall connector offline."""
    entry = await create_wall_connector_entry(
        hass, side_effect=WallConnectorConnectionError
    )

    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_load_unload(hass: HomeAssistant) -> None:
    """Config entry can be unloaded."""

    entry = await create_wall_connector_entry(
        hass,
        vitals_data=get_vitals_data(),
        lifetime_data=get_lifetime_data(),
        wifi_status_data=get_wifi_status_data(),
    )
    assert entry.state is ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_init_uses_split_phase_option(hass: HomeAssistant) -> None:
    """Test setup passes the split phase option to the Wall Connector client."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "1.2.3.4"},
        options={CONF_SPLIT_PHASE: True},
    )
    entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.tesla_wall_connector.WallConnector"
    ) as wall_connector:
        client = wall_connector.return_value
        client.async_get_version = AsyncMock(return_value=get_default_version_data())
        client.async_get_vitals = AsyncMock(return_value=get_vitals_data())
        client.async_get_lifetime = AsyncMock(return_value=get_lifetime_data())
        client.async_get_wifi_status = AsyncMock(return_value=get_wifi_status_data())

        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert wall_connector.call_args.kwargs[CONF_SPLIT_PHASE] is True

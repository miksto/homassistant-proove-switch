"""
Allows to configure a proove switch using a 433MHz module via GPIO on a Raspberry Pi.
"""
import logging

import voluptuous as vol

from homeassistant.components.switch import SwitchDevice, PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, CONF_SWITCHES, EVENT_HOMEASSISTANT_STOP)
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['pigpio']

_LOGGER = logging.getLogger(__name__)

CONF_GPIO = 'gpio'
CONF_UNIT_CODE = 'unit_code'
CONF_TRANSMITTER_CODE = 'transmitter_code'

SWITCH_SCHEMA = vol.Schema({
    vol.Required(CONF_UNIT_CODE): cv.string
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_GPIO): cv.positive_int,
    vol.Required(CONF_SWITCHES): vol.Schema({cv.string: SWITCH_SCHEMA}),
    vol.Required(CONF_TRANSMITTER_CODE): cv.string
})

# pylint: disable=unused-argument, import-error
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Find and return switches controlled by a generic RF device via GPIO."""
    from custom_components.switch import proove_433_transmitter
    import pigpio

    gpio = config.get(CONF_GPIO)
    pi = pigpio.pi()
    rfdevice = proove_433_transmitter.tx(pi, gpio=gpio)
    switches = config.get(CONF_SWITCHES)

    devices = []
    for dev_name, properties in switches.items():
        _LOGGER.info("Adding proove device: %s", dev_name)
        devices.append(
            ProoveSwitch(
                hass = hass,
                name = properties.get(CONF_NAME, dev_name),
                rfdevice = rfdevice,
                transmitter_code = config.get(CONF_TRANSMITTER_CODE),
                unit_code = properties.get(CONF_UNIT_CODE),
            )
        )

    add_devices(devices)

    hass.bus.listen_once(
        EVENT_HOMEASSISTANT_STOP, lambda event: rfdevice.destroy())


class ProoveSwitch(SwitchDevice):
    """Representation of a GPIO RF switch."""

    PROOVE_CODE_ON = '10'
    PROOVE_CODE_OFF = '11'

    def __init__(self, hass, name, rfdevice, transmitter_code, unit_code):
        """Initialize the switch."""
        self._hass = hass
        self._name = name
        self._state = False
        self._rfdevice = rfdevice
        self._unit_code = unit_code
        self._transmitter_code = transmitter_code

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    def _code_on(self):
        return int(self._transmitter_code + self.PROOVE_CODE_ON + self._unit_code, 2)

    def _code_off(self):
        return int(self._transmitter_code + self.PROOVE_CODE_OFF + self._unit_code, 2)

    def _send_code(self, code):
        """Send the code(s) with a specified pulselength."""
        _LOGGER.info("Sending code: %s", code)
        self._rfdevice.send(code)
        return True

    def turn_on(self):
        """Turn the switch on."""
        if self._send_code(self._code_on()):
            self._state = True
            self.schedule_update_ha_state()

    def turn_off(self):
        """Turn the switch off."""
        if self._send_code(self._code_off()):
            self._state = False
            self.schedule_update_ha_state()

import logging
from datetime import timedelta
import requests
import csv 
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, STATE_UNKNOWN, ATTR_ATTRIBUTION)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

_RESOURCE = 'https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/5/station/53430/period/latest-day/data.csv'
_LOGGER = logging.getLogger(__name__)

CONF_ATTRIBUTION = 'Data provided by smhi.com'

DEFAULT_NAME = 'Smhi rain last day'
ICON = 'mdi:weather-rainy'
UNIT = 'mm'

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    name = config.get(CONF_NAME)

    try:
        data = SMHIRainData(hass)
        data.update()
    except requests.exceptions.HTTPError as error:
        _LOGGER.error(error)
        return False

    add_devices([SmhiRainSensor(data, name)])


class SmhiRainSensor(Entity):
    def __init__(self, data, name):
        self.data = data
        self._name = name

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        if self.data.data:
            return self.data.data
        else:
            return STATE_UNKNOWN

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        attr = {}
        return attr

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return UNIT

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return ICON

    def update(self):
        """Update current values."""
        self.data.update()


# pylint: disable=too-few-public-methods
class SMHIRainData(object):
    """Get data from Smhi rain API."""

    def __init__(self, hass):
        """Initialize the data object."""
        self._hass = hass
        self.data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        try:
            download = requests.get(_RESOURCE, timeout=5).json()
            decoded_content = download.content.decode('utf-8')

            cr = csv.reader(decoded_content.splitlines(), delimiter=';')
            my_list = list(cr)
            for row in my_list:
                if len(row) > 3 and row[-1] == "Data från senaste dygnet":
                    self.data = row[3]
            _LOGGER.debug("Data = %s", self.data)
        except ValueError as err:
            _LOGGER.error("Check Smhi rain data %s", err.args)
            self.data = None
            raise
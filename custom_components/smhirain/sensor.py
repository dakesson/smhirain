import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

import requests
import csv 
import logging
from datetime import timedelta

DOMAIN = "smhirain"
ICON = 'mdi:weather-rainy'
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=120)
_LOGGER = logging.getLogger(__name__)
_HEADRESOURCE = 'https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/5/station/'
_TAILRESOURCE = '/period/latest-day/data.csv'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required('station'): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):

    station = config.get('station')
    if len(station) > 0:
        add_entities([SmhiRainSensor(_HEADRESOURCE + station + _TAILRESOURCE)])


class SmhiRainSensor(Entity):

    def __init__(self, resource):
        self._state = None
        self._attributes = {}
        self.resource = resource

    @property
    def name(self):
        return 'Smhi Rain last day'

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON

    @property
    def device_state_attributes(self):
        return self._attributes

    @property
    def unit_of_measurement(self):
        return 'mm'

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        try:
            download = requests.get(self.resource, timeout=5)
            decoded_content = download.content.decode('utf-8')

            for row in list(csv.reader(decoded_content.splitlines(), delimiter=';')):
                if len(row) > 4 and row[-1] == "Data från senaste dygnet":
                    self._state = row[3]
                    
                    self._attributes['From'] = row[0]
                    self._attributes['To'] = row[1]

                    if row[4] == 'G':
                        self._attributes['Quality'] = 'Confirmed'
                    else:
                        self._attributes['Quality'] = 'Not confirmed'
        except ValueError as err:
            _LOGGER.error("Check Smhi rain data %s", err.args)
            raise

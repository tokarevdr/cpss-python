from skyfield.api import wgs84
from skyfield.units import Angle
from datetime import datetime

from satellite import Satellite
from antenna import LinearAntenna


class Vessel:
    def __init__(self, latitude: Angle, longitude: Angle):
        self.position = wgs84.latlon(latitude.degrees, longitude.degrees)


    def can_communicate(self, sat: Satellite, antenna: LinearAntenna, time: datetime):
        # diff = sat.satellite - self.position
        # t = sat.ts.from_datetime(time)
        # topocentric = diff.at(t)

        # alt, az, _ = topocentric.altaz()

        alt, az = sat.altaz(self.position.latitude, self.position.longitude, time)

        print(alt, az)

        visible = alt.degrees > 0

        if visible:
            print('visible')

        detectable = antenna.is_detectable(alt.radians - antenna.altitude, az.radians - antenna.azimuth, 5, 1)

        if detectable:
            print('detectable')

        return visible and detectable
from skyfield.api import EarthSatellite, load, wgs84
from skyfield.positionlib import Geocentric
import datetime
import numpy as np
from geopy.distance import geodesic


class Satellite:
    def __init__(self, tle: str):
        lines = tle.split('\n')
        self.ts = load.timescale()
        self.satellite = EarthSatellite(lines[1].strip(), lines[2].strip(), lines[0].strip())


    def position_and_coverage_area(self, time: datetime):
        t = self.ts.from_datetime(time)
        geocentric = self.satellite.at(t)

        coverage_area = self._coverage_area(geocentric)

        return (geocentric, coverage_area)


    def _coverage_area(self, position: Geocentric):
        # Угол видимости с учетом минимального угла места
        h = wgs84.height_of(position).km
        azimuths = np.linspace(0, 360, 50)
        eps = 0
        R = wgs84.radius.km
        theta = np.arccos(R * np.cos(eps) / (R + h)) - eps
        lat, lon = wgs84.latlon_of(position)

        # Радиус зоны покрытия
        d = R * theta

        boundary_lat = []
        boundary_lon = []
        for azimuth in azimuths:
            point = geodesic(kilometers=d).destination(point=(lat.degrees, lon.degrees), bearing=azimuth)
            boundary_lat.append(point.latitude)
            boundary_lon.append(point.longitude)

        coverage_area = wgs84.latlon(boundary_lat, boundary_lon)

        return coverage_area


def earth_sphere(x0 = 0, y0 = 0, z0 = 0, n = 100, m = 100):
    r = wgs84.radius.km
    u = np.reshape(np.linspace(0, np.pi, n), (n, 1))
    v = np.reshape(np.linspace(0, 2*np.pi, m), (1, m))

    x = x0 + r * np.sin(u) * np.cos(v)
    y = y0 + r * np.sin(u) * np.sin(v)
    z = z0 + r * np.cos(u) * np.ones((1, m))

    return (x, y, z)

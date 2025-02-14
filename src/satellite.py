from skyfield.api import EarthSatellite, load, wgs84
from skyfield.positionlib import Geocentric
from skyfield.timelib import Time
from skyfield.units import Angle, Distance
import datetime
from numpy import sin, cos, arccos, arcsin, arctan, linspace, pi, reshape, ones, tan
from geopy.distance import geodesic


class Satellite:
    def __init__(self, tle: str):
        lines = tle.split('\n')
        self.ts = load.timescale()
        self.satellite = EarthSatellite(lines[1].strip(), lines[2].strip(), lines[0].strip())
        self.pos = 0
        self.dist = Distance(au=0)
        self.sub_pos = 0
        self.coverage_area = []


    def at(self, time: datetime):
        t = self.ts.from_datetime(time)
        geocentric = self.satellite.at(t)
        self.pos = geocentric.position
        self.r = geocentric.distance()
        sub_lat, _ = wgs84.latlon_of(geocentric)
        (ra, _, _) = geocentric.radec()
        sub_lon = Angle(radians=(ra.radians - self.right_ascension_of_greenwich_meridian(time).radians))
        # sub_lat, sub_lon = self._subpoint_mashbits(geocentric, t)
        print(sub_lat, sub_lon)
        self.sub_pos = wgs84.latlon(sub_lat.degrees, sub_lon.degrees)
        self.coverage_area = self._coverage_area(geocentric, t)


    # Satellite Orbits Models, Methods and Applications (Dr. Oliver Montenbruck), p. 33
    def right_ascension_of_greenwich_meridian(self, t: datetime):
        J2000 = datetime.datetime(2000, 1, 2, 12, tzinfo=datetime.UTC)

        timedelta_since_epoch: datetime.timedelta = t - J2000
        days_since_epoch = timedelta_since_epoch.total_seconds() / 3600 / 24

        degs = (280.4606 + 360.9856473*days_since_epoch) % 2*pi

        return Angle(degrees=degs)


    def position_and_coverage_area(self, time: datetime):
        t = self.ts.from_datetime(time)
        geocentric = self.satellite.at(t)

        coverage_area = self._coverage_area(geocentric, t)

        return (geocentric, coverage_area)


    def _coverage_area(self, position: Geocentric, time: Time):
        # Угол видимости с учетом минимального угла места
        h = wgs84.height_of(position).km
        azimuths = linspace(0, 360, 50)
        eps = 0
        R = wgs84.radius.km
        theta = arccos(R * cos(eps) / (R + h)) - eps
        lat, lon = wgs84.latlon_of(position)
        # lat, lon = self._subpoint_mashbits(position, time)

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
    

    def _subpoint_mashbits(self, position: Geocentric, time: Time):
        r = position.distance().km
        x = position.position.km[0]
        y = position.position.km[1]
        z = position.position.km[2]

        alpha = arctan(y/x)
        sigma = arcsin(z/r)

        S = Angle(hours=time.gmst)

        e_earth = 0.081813
        lon = Angle(radians=arctan((sin(alpha) * cos(S.radians) - cos(alpha) * sin(S.radians)) / (cos(alpha) * cos(S.radians) + sin(alpha) * sin(S.radians))))
        lat = Angle(radians=arctan(tan(sigma) / (1 - e_earth**2)))

        return (lat, lon)

        


def earth_sphere(x0 = 0, y0 = 0, z0 = 0, n = 100, m = 100):
    r = wgs84.radius.km
    u = reshape(linspace(0, pi, n), (n, 1))
    v = reshape(linspace(0, 2*pi, m), (1, m))

    x = x0 + r * sin(u) * cos(v)
    y = y0 + r * sin(u) * sin(v)
    z = z0 + r * cos(u) * ones((1, m))

    return (x, y, z)

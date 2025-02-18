import abc
from numpy import ones, linspace
from skyfield.api import wgs84
from skyfield.units import Angle
from geopy.distance import geodesic


class LinearAntenna(abc.ABC):
    def __init__(self, latitude: Angle, longitude: Angle):
        self.position = wgs84.latlon(latitude.degrees, longitude.degrees)


    def setPosition(self, latitude: Angle, longitude: Angle):
        self.position = wgs84.latlon(latitude.degrees, longitude.degrees)


    def radiation_area(self):
        rho, theta = self.radiation_pattern()
        boundary_lat = []
        boundary_lon = []
        for i in range(len(rho)):
            radius = rho[i]
            azimuth = theta[i]

            point = geodesic(meters=radius).destination(point=(self.position.latitude.degrees, self.position.longitude.degrees), bearing=azimuth)
            boundary_lat.append(point.latitude)
            boundary_lon.append(point.longitude)

        return wgs84.latlon(boundary_lat, boundary_lon)


    @abc.abstractmethod
    def radiation_pattern(self):
        pass


class SmallDipole(LinearAntenna):
    def __init__(self, latitude: Angle, longitude: Angle):
        super().__init__(latitude, longitude)


    def radiation_pattern(self):
        m = 100

        rho = ones(m) * 1e+5
        theta = linspace(0, 360, m)

        return (rho, theta)

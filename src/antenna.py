import abc
from numpy import ones, linspace, sqrt, sin, exp
from scipy.constants import mu_0, epsilon_0, pi, c
from skyfield.api import wgs84
from skyfield.units import Angle
from geopy.distance import geodesic


class LinearAntenna(abc.ABC):
    def __init__(self, latitude: Angle, longitude: Angle,
                 frequency: float, current: float, length: float,
                 altitude: float, azimuth: float,
                 power_input: float, minimal_detectable_power: float):
        self.position = wgs84.latlon(latitude.degrees, longitude.degrees)
        self.altitude = altitude
        self.azimuth = azimuth
        self.frequency = frequency
        self.current = current
        self.length = length
        self.power_input = power_input
        self.minimal_detectable_power = minimal_detectable_power


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
    

    def radiation_intensity(self, theta: float, phi: float, r: float):
        eta = sqrt(mu_0 / epsilon_0)
        return r**2 / (2 * eta) * abs(self.far_field(theta, phi, r))**2
    

    def gain(self, theta: float, phi: float, r: float):
        return 4 * pi * self.radiation_intensity(theta, phi, r) / self.power_input
    

    def is_detectable(self, theta: float, phi: float, r: float, input_power: float):
        print('theta:', theta, 'phi:', phi)
        received_power = self.gain(theta, phi, r) * input_power
        print("far field:", abs(self.far_field(theta, phi, r)))
        print('gain:', self.gain(theta, phi, r))
        print("received power:", received_power)
        print('minimal power:', self.minimal_detectable_power)
        return self.minimal_detectable_power <= received_power
    

    @abc.abstractmethod
    def radiation_pattern(self):
        pass


    @abc.abstractmethod
    def far_field(self, theta: float, phi: float, r: float):
        pass


class SmallDipole(LinearAntenna):
    def __init__(self, latitude: Angle, longitude: Angle,
                 frequency: float, current: float, length: float,
                 altitude: float, azimuth: float,
                 power_input: float, minimal_detectable_power: float):
        super().__init__(latitude, longitude,
                         frequency, current, length,
                         altitude, azimuth,
                         power_input, minimal_detectable_power)


    def radiation_pattern(self):
        m = 100

        rho = ones(m) * 1e+5
        theta = linspace(0, 360, m)

        return (rho, theta)
    

    def far_field(self, theta: float, phi: float, r: float):
        k = 2 * pi * self.frequency / c
        eta = sqrt(mu_0 / epsilon_0)
        return 1j * eta * k * self.current * self.length * exp(-1j * k * r) / (8 * pi * r) * sin(theta)

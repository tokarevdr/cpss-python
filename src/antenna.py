import abc
from scipy.constants import c, pi, mu_0, epsilon_0
from numpy import sin, exp, sqrt

class LinearAntenna(abc.ABC):
    def __init__(self, frequency: float, length: float, current: float):
        self.frequency = frequency
        self.length = length
        self.current = current


    @abc.abstractmethod
    def directivity(self):
        pass


    @abc.abstractmethod
    def beamwidth(self):
        pass


    @abc.abstractmethod
    def maximum_effective_aperture(self):
        pass


    @abc.abstractmethod
    def radiation_resistance(self):
        pass


    @abc.abstractmethod
    def radiated_power(self):
        pass


    @abc.abstractmethod
    def far_field(self, r: float, theta: float):
        pass


class SmallDipole(LinearAntenna):
    def __init__(self, frequency: float, length: float, current: float):
        super().__init__(frequency, length, current)


    def directivity(self):
        return 1.5


    def beamwidth(self):
        return 90 * pi/180


    def maximum_effective_aperture(self):
        wavelength = c / self.frequency
        return 3. * wavelength**2 / (8. * pi)


    def radiation_resistance(self):
        return 20. * (pi * self.length * self.frequency / c)**2


    def radiated_power(self):
        return 0.5 * self.radiation_resistance() * abs(self.current)**2


    def far_field(self, r, theta):
        # Calculate the wave impedance
        eta = sqrt(mu_0 / epsilon_0)

        # Calculate the wavenumber
        k = 2.0 * pi * self.frequency / c

        # Define the radial-component of the electric far field (V/m)
        e_r = 0.0

        # Define the theta-component of the electric far field (V/m)
        e_theta = 1j * eta * k * self.current * self.length / (8.0 * pi * r) * sin(theta) * exp(-1j * k * r)

        # Define the phi-component of the electric far field (V/m)
        e_phi = 0.0

        # Define the r-component of the magnetic far field (A/m)
        h_r = 0.0

        # Define the theta-component of the magnetic far field (A/m)
        h_theta = 0.0

        # Define the phi-component of the magnetic far field (A/m)
        h_phi = 1j * k * self.current * self.length / (8.0 * pi * r) * sin(theta) * exp(-1j * k * r)

        # Return all six components of the far field
        return e_r, e_theta, e_phi, h_r, h_theta, h_phi

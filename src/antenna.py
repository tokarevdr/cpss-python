import abc
from numpy import cos
from scipy.constants import c
from skyfield.units import Angle, Distance

from transmission import received_power


class LinearAntenna(abc.ABC):
    def __init__(self, frequency: float, azimuth: Angle, elevation: Angle,
                 minimal_detectable_power: float):
        self.azimuth = Angle(radians=azimuth.radians)
        self.elevation = Angle(radians=elevation.radians)
        self.frequency = frequency
        self._wavelength = c / frequency
        self.minimal_detectable_power = minimal_detectable_power
    

    @abc.abstractmethod
    def gain(self, theta: float, phi: float):
        pass


    def is_input_detectable(self, p_t: float, g_t: float, azimuth: Angle, elevation: Angle, distance: Distance):
        g_r = self.gain(elevation.radians, azimuth.radians)
        p_r = received_power(p_t, g_t, g_r, self._wavelength, distance.m)

        print('gain:', g_r)
        print('power:', p_r)
        print('min power:', self.minimal_detectable_power)

        return p_r >= self.minimal_detectable_power


class SmallDipole(LinearAntenna):
    def __init__(self, frequency: float, azimuth: Angle, elevation: Angle,
                 minimal_detectable_power: float):
        super().__init__(frequency, azimuth, elevation,
                         minimal_detectable_power)
    

    def gain(self, theta: float, phi: float):
        return cos(theta)**2
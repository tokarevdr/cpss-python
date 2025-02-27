from numpy import pi


def received_power(p_t: float, g_t: float, g_r: float, lam: float, d: float):
    '''Friis transmission formula. Euating the power at the terminals of a receive antenna
    as the product of power density of the incident wave and the effective aperture of the receiving antenna
    under idealized conditions given another antenna some distance away transmitting a known amount of power.
    
    Parameters
    ----------
    p_t : float
          The power fed into the transmitting antenna input terminals
    g_t : float
        The transmittin antenna gain
    g_r : float
        The receiving antenna gain
    lam : float
        Wavelength
    d : float
        The distance separating the antennas
    
    Returns
    -------
    p_t : float
        The power available at receiving antenna output terminals.
    '''

    return p_t * g_t * g_r * (lam / (4 * pi * d))**2
import datetime, pytz
import numpy as np
import matplotlib.pyplot as plt

from satellite import Satellite, earth_sphere
from antenna import SmallDipole


def main():
    print("Hello!")

    #observer_position = wgs84.latlon(60, 30)

    moscow_timezone = pytz.timezone("Europe/Moscow")
    time = datetime.datetime(2025, 2, 19, 18, 20, 10, 637, moscow_timezone)
    time_step = datetime.timedelta(hours=2)
    time_end = datetime.datetime(2025, 2, 19, 18, 20, 10, 673, moscow_timezone)
 
    # line1 = "1 53385U 22096R   22269.14435733  .00009653  00000-0  37762-3 0  999 5"
    # line2 = "2 53385  97.4313 170.3195 0002683 298.0162 199.7004 15.26041929  732 7"

    # sat = EarthSatellite(line1, line2, "Edelweiss (GEOSCAN)", ts)

    tle = '''FLTSATCOM-7 (USA-20)
             1 17181U 86096A   24343.04493793  .00000019  00000-0  00000-0 0  9992
             2 17181  13.1563 343.6233 0041591 313.7972 237.2580  0.98925627146461'''

    sat = Satellite(tle)

    (xe, ye, ze) = earth_sphere(n = 10, m = 10)

    ax = plt.figure().add_subplot(projection="3d")
    a = 30e+3
    ax.set(xlim = (-a, a), ylim = (-a, a), zlim = (-a, a))

    ax.plot_wireframe(xe, ye, ze)

    while time <= time_end:
        sat.at(time)

        (x, y, z) = sat.pos.km
        (xs, ys, zs) = sat.sub_pos.itrs_xyz.km
        ax.scatter(x, y, z, linewidths=5, color="red")
        #ax.scatter(observer_position.itrs_xyz.km[0], observer_position.itrs_xyz.km[1], observer_position.itrs_xyz.km[2], linewidths=5, color="green")
        ax.scatter(xs, ys, zs, linewidths=5, color="red")
        ax.plot(sat.coverage_area.itrs_xyz.km[0], sat.coverage_area.itrs_xyz.km[1], sat.coverage_area.itrs_xyz.km[2], color = "red")

        time += time_step

    antenna = SmallDipole(1e+9, 0.4, 1)
    r = 1.0e9
    theta = np.linspace(0, 2.0 * np.pi, 1000)

    (_, et, _, _, _, _) = antenna.far_field(r, theta)

    plt.figure()
    plt.polar(theta, abs(et))

    plt.show()

if __name__ == "__main__":
    main()
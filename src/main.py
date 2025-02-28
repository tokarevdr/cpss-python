import datetime, pytz
import matplotlib.pyplot as plt
import numpy as np


from satellite import Satellite, earth_sphere
from antenna import FiniteLengthDipole, Angle
from vessel import Vessel

import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

from glob import glob


def main():
    print("Hello!")

    moscow_timezone = pytz.timezone("Europe/Moscow")
    time = datetime.datetime(2025, 2, 1, 9, 00, 10, 637, moscow_timezone)

    # tle = '''Edelweiss (GEOSCAN)
    #          1 53385U 22096R   22269.14435733  .00009653  00000-0  37762-3 0  999 5
    #          2 53385  97.4313 170.3195 0002683 298.0162 199.7004 15.26041929  732 7'''

    tle = '''FLTSATCOM-7 (USA-20)
             1 17181U 86096A   24343.04493793  .00000019  00000-0  00000-0 0  9992
             2 17181  13.1563 343.6233 0041591 313.7972 237.2580  0.98925627146461'''

    sat = Satellite(tle, 10, 1)

    (xe, ye, ze) = earth_sphere(n = 10, m = 10)

    ax = plt.figure().add_subplot(projection="3d")
    a = 8e+3
    ax.set(xlim = (-a, a), ylim = (-a, a), zlim = (-a, a))

    ax.plot_wireframe(xe, ye, ze)

    sat.at(time)

    (xs, ys, zs) = sat.sub_pos.itrs_xyz.km
    ax.scatter(xs, ys, zs, linewidths=5, color="red")
    ax.plot(sat.coverage_area.itrs_xyz.km[0], sat.coverage_area.itrs_xyz.km[1], sat.coverage_area.itrs_xyz.km[2], color = "red")

    antenna = FiniteLengthDipole(1e+6, Angle(degrees=-15), Angle(degrees=25), 3.7e-12)

    _, axs = plt.subplots(1, 2, subplot_kw={'projection': 'polar'})
    theta = np.linspace(0, 360, 100) * np.pi/180
    phi = np.linspace(0, 360, 100) * np.pi/180

    axs[0].plot(theta, antenna.gain(theta, 0))
    axs[1].plot(phi, antenna.gain(0, phi))

    vessel = Vessel(Angle(degrees=60), Angle(degrees=30))
    print(vessel.can_communicate(sat, antenna, time))

    ax.scatter(vessel.position.itrs_xyz.km[0], vessel.position.itrs_xyz.km[1], vessel.position.itrs_xyz.km[2], linewidths=5, color="green")
    
    fig = plt.figure(figsize=(10, 5))
    ax2 = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())

    # shape_files_dir_path = 'G:/Мой диск/MyEducation/ИТМО/ВКР/soft/python/first_steps/10m_physical'
    # shape_files = glob(shape_files_dir_path + '/*.shp')
    # for shape_file in shape_files:
    #     shape_feature = ShapelyFeature(Reader(shape_file).geometries(), ccrs.PlateCarree(), facecolor='none')
    #     ax2.add_feature(shape_feature)
    ax2.set_global()
    ax2.stock_img()
    ax2.coastlines()
    ax2.plot(vessel.position.longitude.degrees, vessel.position.latitude.degrees, 'o', color='green', transform=ccrs.PlateCarree())
    ax2.plot(sat.sub_pos.longitude.degrees, sat.sub_pos.latitude.degrees, 'o', transform=ccrs.PlateCarree(), color='red')
    ax2.plot(sat.coverage_area.longitude.degrees, sat.coverage_area.latitude.degrees, transform=ccrs.PlateCarree(), color='red')

    plt.show()

if __name__ == "__main__":
    main()
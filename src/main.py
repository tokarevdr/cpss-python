import datetime, pytz
import matplotlib.pyplot as plt
import numpy as np

import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

from glob import glob

import sys
sys.path.append('G:/Мой диск/MyEducation/ИТМО/ВКР/soft/')

import vesradcom as vrc
from vesradcom.entities import FiniteLengthDipole, Vessel, Satellite, Landmark, Station
from vesradcom.units import Angle, Frequency, Power, Distance


def earth_sphere(r = 1, x0 = 0, y0 = 0, z0 = 0, n = 100, m = 100):
    u = np.reshape(np.linspace(0, np.pi, n), (n, 1))
    v = np.reshape(np.linspace(0, 2*np.pi, m), (1, m))

    x = x0 + r * np.sin(u) * np.cos(v)
    y = y0 + r * np.sin(u) * np.sin(v)
    z = z0 + r * np.cos(u) * np.ones((1, m))

    return (x, y, z)


def draw_satellite(ax, sat: Satellite):
    ax.plot(sat.subpoint_position().longitude.degrees, sat.subpoint_position().latitude.degrees, 'o', transform=ccrs.PlateCarree(), color='red')
    ax.plot(*sat.coverage_area().exterior.xy, transform=ccrs.PlateCarree(), color='red')
    ax.annotate(sat.title(), (sat.subpoint_position().longitude.degrees - 5, sat.subpoint_position().latitude.degrees + 3), transform=ccrs.PlateCarree(), color='red')


def draw_vessel(ax, vessel: Vessel):
    ax.plot(vessel.position().longitude.degrees, vessel.position().latitude.degrees, 'o', color='green', transform=ccrs.PlateCarree())
    ax.annotate("", xytext=(vessel.position().longitude.degrees, vessel.position().latitude.degrees), xy=(vessel.position().longitude.degrees + 10 * np.sin(vessel.course().radians), vessel.position().latitude.degrees + 10 * np.cos(vessel.course().radians)), arrowprops=dict(arrowstyle="->"), transform=ccrs.PlateCarree())


def draw_landmark(ax, landmark: Landmark):
    ax.plot(landmark.position().longitude.degrees, landmark.position().latitude.degrees, 'o', transform=ccrs.PlateCarree(), color='blue')
    ax.annotate(landmark.title(), (landmark.position().longitude.degrees - 5, landmark.position().latitude.degrees + 3), transform=ccrs.PlateCarree(), color='blue')


def draw_station(ax, station: Station):
    draw_landmark(ax, station)
    ax.plot(*station.coverage_area().exterior.xy, transform=ccrs.PlateCarree(), color='blue')


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
    
    sat = Satellite(tle, Power(10), 1)
    antenna = FiniteLengthDipole(Frequency(hz=1e+6), Angle(degrees=25), Angle(degrees=-15), Power(w=3.7e-12), Power(w=10))
    vessel = Vessel(Angle(degrees=40), Angle(degrees=-25), Angle(degrees=60))
    area = [(-51, 48), (-15, 48), (-20, 12), (-51, 12)]

    simulation = vrc.Simulation(area = area, antenna = antenna, vessel = vessel)

    simulation.append_satellite(sat)
    simulation.append_landmark(Landmark('Санкт-Петербург', Angle(degrees=59.9386), Angle(degrees=30.3141)))
    simulation.append_station(Station('Станция', Angle(degrees=43), Angle(degrees=-9), Distance(km = 700)))
    simulation.set_current_datetime(time)
    simulation.update()

    print('satellite visible:', simulation.satellite_at(0).visible())
    print('satellite detectable:', simulation.satellite_at(0).detectable())
    
    fig = plt.figure(figsize=(15, 7))
    ax2 = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())

    shape_files_dir_path = 'G:/Мой диск/MyEducation/ИТМО/ВКР/soft/python/first_steps/10m_physical'
    shape_files = glob(shape_files_dir_path + '/ne_10m_land.shp')
    for shape_file in shape_files:
        shape_feature = ShapelyFeature(Reader(shape_file).geometries(), ccrs.PlateCarree(), facecolor='none', alpha = 0.5)
        ax2.add_feature(shape_feature)

    ax2.set_global()
    
    ax2.plot(*simulation.area().exterior.xy, '--', transform=ccrs.PlateCarree(), color='green')
    draw_vessel(ax2, vessel)

    for i in range(simulation.satellite_count()):
        draw_satellite(ax2, simulation.satellite_at(i))

    for i in range(simulation.landmark_count()):
        draw_landmark(ax2, simulation.landmark_at(i))

    for i in range(simulation.station_count()):
        draw_station(ax2, simulation.station_at(i))
    
    plt.show()

if __name__ == "__main__":
    main()
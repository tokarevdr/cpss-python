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
from vesradcom.units import Angle, Frequency, Power, Distance, Velocity


def draw_satellite(ax, sat: Satellite, color):
    ax.plot(sat.subpoint_position().longitude.degrees, sat.subpoint_position().latitude.degrees, 'o', transform=ccrs.PlateCarree(), color=color)
    ax.fill(*sat.coverage_area().exterior.xy, transform=ccrs.PlateCarree(), facecolor = 'grey', alpha = 0.2, edgecolor='grey')
    ax.plot(*sat.coverage_area().exterior.xy, transform=ccrs.PlateCarree(), color=color)
    ax.annotate(sat.title(), (sat.subpoint_position().longitude.degrees - 5, sat.subpoint_position().latitude.degrees + 3), transform=ccrs.PlateCarree(), color=color)


def draw_vessel(ax, vessel: Vessel):
    ax.plot(vessel.position().longitude.degrees, vessel.position().latitude.degrees, 'o', color='green', transform=ccrs.PlateCarree())
    ax.annotate("", xytext=(vessel.position().longitude.degrees, vessel.position().latitude.degrees), xy=(vessel.position().longitude.degrees + 10 * np.sin(vessel.course().radians), vessel.position().latitude.degrees + 10 * np.cos(vessel.course().radians)), arrowprops=dict(arrowstyle="->"), transform=ccrs.PlateCarree())


def draw_landmark(ax, landmark: Landmark):
    ax.plot(landmark.position().longitude.degrees, landmark.position().latitude.degrees, 'o', transform=ccrs.PlateCarree(), color='blue')
    ax.annotate(landmark.title(), (landmark.position().longitude.degrees - 5, landmark.position().latitude.degrees + 3), transform=ccrs.PlateCarree(), color='blue')


def draw_station(ax, station: Station):
    draw_landmark(ax, station)
    ax.plot(*station.coverage_area().exterior.xy, transform=ccrs.PlateCarree(), color='blue')


def draw_simulation(ax, sim: vrc.Simulation):
    ax.plot(*sim.area().exterior.xy, '--', transform=ccrs.PlateCarree(), color='green')
    draw_vessel(ax, sim.vessel())

    for i in range(sim.satellite_count()):
        draw_satellite(ax, sim.satellite_at(i), 'red')

    for i in range(sim.landmark_count()):
        draw_landmark(ax, sim.landmark_at(i))

    for i in range(sim.station_count()):
        draw_station(ax, sim.station_at(i))


def main():
    print("Hello!")

    moscow_timezone = pytz.timezone("Europe/Moscow")
    time = datetime.datetime(2025, 2, 1, 6, 00, 10, 637, moscow_timezone)

    tle1 = '''Спутник 1
             1 53385U 22096R   22269.14435733  .00009653  00000-0  37762-3 0  999 5
             2 53385  97.4313 170.3195 0002683 298.0162 199.7004 15.26041929  732 7'''

    tle2 = '''Спутник 2
             1 17181U 86096A   24343.04493793  .00000019  00000-0  00000-0 0  9992
             2 17181  13.1563 343.6233 0041591 313.7972 237.2580  0.98925627146461'''
    
    antenna = FiniteLengthDipole(Frequency(hz=1e+6), Power(w=3.7e-12), Power(w=12), Power(w=10))
    vessel = Vessel(Angle(degrees=15), Angle(degrees=-48), Angle(degrees=30), Velocity(km_per_s=0.02))
    area = [(-51, 48), (-15, 48), (-20, 12), (-51, 12)]

    simulation = vrc.Simulation(area = area, antenna = antenna, vessel = vessel)

    simulation.append_satellite(Satellite(tle1, Power(10), 1))
    simulation.append_satellite(Satellite(tle2, Power(15), 1))
    simulation.set_current_datetime(time)
    simulation.update()

    for i in range(simulation.satellite_count()):
        print(f'satellite {i} visible:', simulation.satellite_at(i).visible())
        print(f'satellite {i} detectable:', simulation.satellite_at(i).detectable())

    
    fig1 = plt.figure(figsize=(15, 7))
    ax1 = fig1.add_subplot(1, 1, 1, projection=ccrs.Robinson())

    fig2 = plt.figure(figsize=(15, 7))
    ax2 = fig2.add_subplot(1, 1, 1, projection=ccrs.Robinson())

    shape_files_dir_path = 'G:/Мой диск/MyEducation/ИТМО/ВКР/soft/python/first_steps/10m_physical'
    shape_files = glob(shape_files_dir_path + '/ne_10m_land.shp')
    for shape_file in shape_files:
        shape_feature = ShapelyFeature(Reader(shape_file).geometries(), ccrs.PlateCarree(), facecolor='none', alpha = 0.5)
        ax1.add_feature(shape_feature)
        ax2.add_feature(shape_feature)

    ax1.set_global()
    ax2.set_global()
    
    draw_simulation(ax1, simulation)

    # ax2.plot(*simulation.satellite_at(0).track(time, time + datetime.timedelta(hours=1.55), 35), '.', transform=ccrs.PlateCarree(), color='red')
    # ax2.plot(*simulation.satellite_at(1).track(time, time + datetime.timedelta(hours=24), 60), '.', transform=ccrs.PlateCarree(), color='blue')
    results = simulation.bruteforce(time + datetime.timedelta(hours=3), time + datetime.timedelta(hours=3.3))
    print(results[0])

    res_sim = vrc.from_bruteforce_result(simulation, results[0])

    print(res_sim.current_datetime())

    draw_simulation(ax2, res_sim)
    
    plt.show()

if __name__ == "__main__":
    main()
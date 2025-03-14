import datetime, pytz
import matplotlib.pyplot as plt
import numpy as np

import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

from glob import glob

import sys
sys.path.append('/home/vlad/Documents/Python/')

import vesradcom as vrc
from vesradcom.entities import FiniteLengthDipole, Vessel, Satellite, Landmark, Station
from vesradcom.units import Angle, Frequency, Power, Distance, Velocity


def draw_satellite(ax, sat: Satellite, color, transform):
    ax.plot(sat.subpoint_position().longitude.degrees, sat.subpoint_position().latitude.degrees, 'o', transform=transform, color=color)
    ax.fill(*sat.coverage_area().exterior.xy, transform=transform, facecolor = 'grey', alpha = 0.2, edgecolor='grey')
    ax.plot(*sat.coverage_area().exterior.xy, transform=transform, color=color)
    ax.annotate(sat.title(), (sat.subpoint_position().longitude.degrees - 5, sat.subpoint_position().latitude.degrees + 3), transform=transform, color=color)


def draw_vessel(ax, vessel: Vessel, transform):
    ax.plot(vessel.position().longitude.degrees, vessel.position().latitude.degrees, 'o', color='green', transform=transform)
    ax.annotate("", xytext=(vessel.position().longitude.degrees, vessel.position().latitude.degrees), xy=(vessel.position().longitude.degrees + 10 * np.sin(vessel.course().radians), vessel.position().latitude.degrees + 10 * np.cos(vessel.course().radians)), arrowprops=dict(arrowstyle="->"), transform=transform)


def draw_landmark(ax, landmark: Landmark, transform):
    ax.plot(landmark.position().longitude.degrees, landmark.position().latitude.degrees, 'o', transform=transform, color='blue')
    ax.annotate(landmark.title(), (landmark.position().longitude.degrees - 5, landmark.position().latitude.degrees + 3), transform=transform, color='blue')


def draw_station(ax, station: Station, transform):
    draw_landmark(ax, station, transform)
    ax.plot(*station.coverage_area().exterior.xy, transform=transform, color='blue')


def draw_simulation(ax, sim: vrc.Simulation, track_end_datetime: datetime, transform):
    ax.plot(*sim.area().exterior.xy, '--', transform=transform, color='green')
    draw_vessel(ax, sim.vessel(), transform)

    for i in range(sim.satellite_count()):
        draw_satellite(ax, sim.satellite_at(i), 'red', transform)
        track = sim.satellite_at(i).track(sim.current_datetime(), track_end_datetime, datetime.timedelta(minutes=5))
        ax.plot(track.longitude.degrees, track.latitude.degrees, '--', transform=transform, color='red')

    for i in range(sim.landmark_count()):
        draw_landmark(ax, sim.landmark_at(i), transform)

    for i in range(sim.station_count()):
        draw_station(ax, sim.station_at(i), transform)


def draw_result(ax, sim: vrc.Simulation, track_start_datetime: datetime, transform):
    ax.plot(*sim.area().exterior.xy, '--', transform=transform, color='green')
    draw_vessel(ax, sim.vessel(), transform)

    for i in range(sim.satellite_count()):
        draw_satellite(ax, sim.satellite_at(i), 'blue', transform)
        track = sim.satellite_at(i).track(track_start_datetime, sim.current_datetime(), datetime.timedelta(minutes=5))
        ax.plot(track.longitude.degrees, track.latitude.degrees, '--', transform=transform, color='blue')


def main():
    print("Hello!")

    moscow_timezone = pytz.timezone("Europe/Moscow")
    current_datetime = datetime.datetime(2025, 3, 14, 13, 0, 0, tzinfo=moscow_timezone)

    communication_session_start_time = current_datetime + datetime.timedelta(hours=2)
    communication_session_end_time = current_datetime + datetime.timedelta(hours=2.5)

    tle1 = '''Спутник 1
             1 53385U 22096R   22269.14435733  .00009653  00000-0  37762-3 0  999 5
             2 53385  97.4313 170.3195 0002683 298.0162 199.7004 15.26041929  732 7'''

    tle2 = '''MERIDIAN-9
    1 45254U 20015A   24344.16116386  .00000028  00000-0  00000+0 0  9996
    2 45254  64.9856  20.3505 6961787 286.4695  12.1378  2.00618940 35177'''
    
    antenna = FiniteLengthDipole(Frequency(hz=1e+6), Power(w=3.7e-12), Power(w=12), Power(w=10))
    vessel = Vessel(Angle(degrees=15), Angle(degrees=-20), Angle(degrees=45), Velocity(km_per_s=0.02))
    area = [(-52, 40), (-21, 40),  (-19, 12), (-52, 12)]

    simulation = vrc.Simulation(area = area, antenna = antenna, vessel = vessel)

    # simulation.append_satellite(Satellite(tle1, Power(10), 1))
    simulation.append_satellite(Satellite(tle2, Power(15), 1))
    simulation.set_current_datetime(current_datetime)
    simulation.update()

    for i in range(simulation.satellite_count()):
        print(f'satellite {i} visible:', simulation.satellite_at(i).visible())
        print(f'satellite {i} detectable:', simulation.satellite_at(i).detectable())

    results = simulation.bruteforce(communication_session_start_time, communication_session_end_time)

    res_sim = vrc.Simulation()

    if results:
        print(results[0])
        res_sim = vrc.from_bruteforce_result(simulation, results[0])

    # projection = ccrs.AzimuthalEquidistant(central_latitude=simulation.vessel().position().latitude.degrees, central_longitude=simulation.vessel().position().longitude.degrees)
    projection = ccrs.PlateCarree()
    transform = ccrs.Geodetic()

    fig1 = plt.figure(figsize=(15, 7))
    ax1 = fig1.add_subplot(1, 1, 1, projection=projection)

    shape_files_dir_path = '/home/vlad/Documents/10m_physical'
    shape_files = glob(shape_files_dir_path + '/ne_10m_land.shp')
    for shape_file in shape_files:
        shape_feature = ShapelyFeature(Reader(shape_file).geometries(), ccrs.PlateCarree(), facecolor='none', alpha = 0.5)
        ax1.add_feature(shape_feature)

    ax1.set_global()
    
    draw_simulation(ax1, simulation, communication_session_end_time, transform)
    
    if results:
        draw_result(ax1, res_sim, current_datetime, transform)
        ax1.plot(*results[0].intersection.exterior.xy, '.', transform=transform, color='blue')

    print(simulation.satellite_at(0).altitude(), simulation.satellite_at(0).azimuth())
    
    plt.show()

if __name__ == "__main__":
    main()